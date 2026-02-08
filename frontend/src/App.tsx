import { useState, useRef, useEffect, isValidElement } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import * as echarts from 'echarts'
import './App.css'

const API_BASE = import.meta.env.VITE_API_BASE || ''

interface ToolCall {
  id: string
  name: string
  args: string
  result?: string
}

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  toolCalls?: ToolCall[]
}

/** Strip outer ```markdown ... ``` wrapper so inner markdown can be rendered */
function stripOuterMarkdownCodeBlock(text: string): string {
  const trimmed = text.trim()
  if (!trimmed.startsWith('```')) return text
  const afterOpen = trimmed.slice(3).trimStart()
  const langMatch = afterOpen.match(/^(\w+)\s*\n/)
  const lang = langMatch?.[1]?.toLowerCase()
  if (lang && lang !== 'markdown' && lang !== 'md') return text
  const contentStart = langMatch ? langMatch[0].length : 0
  const inner = afterOpen.slice(contentStart)
  const closeIdx = inner.indexOf('\n```')
  if (closeIdx >= 0) return inner.slice(0, closeIdx).trimEnd()
  if (inner.endsWith('```')) return inner.slice(0, -3).trimEnd()
  return text
}

function ChartBlock({ specText }: { specText: string }) {
  const containerRef = useRef<HTMLDivElement>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!containerRef.current) return
    let option: echarts.EChartsOption
    try {
      option = JSON.parse(specText) as echarts.EChartsOption
    } catch (e) {
      const msg = e instanceof Error ? e.message : 'JSON 解析失败'
      setError(msg)
      return
    }

    setError(null)
    containerRef.current.innerHTML = ''
    const chart = echarts.init(containerRef.current, undefined, { renderer: 'canvas' })
    try {
      chart.setOption(option, { notMerge: true })
    } catch (e) {
      const msg = e instanceof Error ? e.message : '图表渲染失败'
      setError(msg)
    }

    const handleResize = () => chart.resize()
    window.addEventListener('resize', handleResize)
    return () => {
      window.removeEventListener('resize', handleResize)
      chart.dispose()
    }
  }, [specText])

  return (
    <div className="chart-block">
      <div className="chart-canvas" ref={containerRef} />
      {error && (
        <div className="chart-error">
          图表渲染失败：{error}
          <pre className="chart-fallback">
            <code>{specText}</code>
          </pre>
        </div>
      )}
    </div>
  )
}

function MarkdownContent({ text }: { text: string }) {
  const content = stripOuterMarkdownCodeBlock(text)
  return (
    <div className="message-content-inner">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          pre({ children, node, ...props }) {
            const child = Array.isArray(children) ? children[0] : children
            if (isValidElement(child) && child.type === ChartBlock) {
              return <div {...props}>{child}</div>
            }
            return <pre {...props}>{children}</pre>
          },
          code({ inline, className, children, node, ...props }) {
            const match = /language-(\w+)/.exec(className || '')
            const lang = match?.[1]?.toLowerCase()
            const codeText = String(children).replace(/\n$/, '')
            if (!inline && (lang === 'echarts' || lang === 'chart')) {
              return <ChartBlock specText={codeText} />
            }
            return (
              <code className={className} {...props}>
                {children}
              </code>
            )
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  )
}

function CollapsibleToolBlock({ tool }: { tool: ToolCall }) {
  const [collapsed, setCollapsed] = useState(true)
  let sql = ''
  let resultPreview = ''
  try {
    const args = JSON.parse(tool.args || '{}')
    sql = args.sql || ''
  } catch {
    sql = tool.args || ''
  }
  if (tool.result) {
    try {
      const parsed = JSON.parse(tool.result)
      if (parsed.columns && parsed.data) {
        resultPreview = `columns: ${parsed.columns.join(', ')} | rows: ${parsed.row_count ?? parsed.data?.length ?? 0}`
      } else {
        resultPreview = String(tool.result).slice(0, 80) + (tool.result.length > 80 ? '...' : '')
      }
    } catch {
      resultPreview = String(tool.result).slice(0, 80) + (tool.result.length > 80 ? '...' : '')
    }
  }

  const isSqlTool = tool.name === 'execute_sql_query' || tool.name === 'get_table_schema'

  return (
    <div className="tool-block">
      <button
        type="button"
        className="tool-block-header"
        onClick={() => setCollapsed((c) => !c)}
        aria-expanded={!collapsed}
      >
        <span className="tool-block-icon">🔧</span>
        <span className="tool-block-name">{tool.name}</span>
        <span className="tool-block-chevron">{collapsed ? '▶' : '▼'}</span>
      </button>
      {!collapsed && (
        <div className="tool-block-body">
          {isSqlTool && sql && (
            <div className="tool-block-section">
              <div className="tool-block-label">SQL</div>
              <pre className="tool-block-sql">
                <code>{sql}</code>
              </pre>
            </div>
          )}
          {tool.result && (
            <div className="tool-block-section">
              <div className="tool-block-label">执行结果</div>
              <pre className="tool-block-result">
                <code>{tool.result}</code>
              </pre>
            </div>
          )}
          {!tool.result && <div className="tool-block-placeholder">执行中...</div>}
        </div>
      )}
      {collapsed && resultPreview && (
        <div className="tool-block-preview">{resultPreview}</div>
      )}
    </div>
  )
}

function App() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const sessionIdRef = useRef(`session-${Date.now()}`)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const sendMessage = async () => {
    const text = input.trim()
    if (!text || loading) return

    setInput('')
    setError(null)
    const userMsg: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: text,
    }
    setMessages((prev) => [...prev, userMsg])
    setLoading(true)

    const assistantId = `assistant-${Date.now()}`
    setMessages((prev) => [
      ...prev,
      { id: assistantId, role: 'assistant', content: '' },
    ])

    try {
      const res = await fetch(`${API_BASE}/v1/chat/completions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model: 'default',
          stream: true,
          session_id: sessionIdRef.current,
          messages: [
            ...messages.map((m) => ({ role: m.role, content: m.content })),
            { role: 'user', content: text },
          ],
        }),
      })

      if (!res.ok) {
        const err = await res.json().catch(() => ({}))
        const msg =
          err?.error?.message ||
          err?.detail?.error?.message ||
          (typeof err?.detail === 'string' ? err.detail : null) ||
          `HTTP ${res.status}`
        throw new Error(msg)
      }

      const reader = res.body?.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      let fullContent = ''
      const toolCallsAcc: Record<number, { id: string; name: string; args: string }> = {}
      const toolResults: Record<string, string> = {}

      const mergeToolCalls = () =>
        Object.values(toolCallsAcc)
          .sort((a, b) => (a.id < b.id ? -1 : 1))
          .map((tc) => ({
            id: tc.id,
            name: tc.name,
            args: tc.args,
            result: toolResults[tc.id],
          }))

      if (reader) {
        while (true) {
          const { done, value } = await reader.read()
          if (done) break
          buffer += decoder.decode(value, { stream: true })
          const lines = buffer.split('\n')
          buffer = lines.pop() || ''
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const data = line.slice(6)
              if (data === '[DONE]') continue
              try {
                const obj = JSON.parse(data)
                const delta = obj.choices?.[0]?.delta
                if (!delta) continue

                if (delta.tool_calls) {
                  for (const tc of delta.tool_calls) {
                    const idx = tc.index ?? 0
                    if (!toolCallsAcc[idx]) toolCallsAcc[idx] = { id: '', name: '', args: '' }
                    if (tc.id) toolCallsAcc[idx].id += tc.id
                    if (tc.function?.name) toolCallsAcc[idx].name += tc.function.name
                    if (tc.function?.arguments) toolCallsAcc[idx].args += tc.function.arguments
                  }
                }
                if (delta.role === 'tool' && delta.tool_call_id != null && delta.content != null) {
                  toolResults[delta.tool_call_id] = (toolResults[delta.tool_call_id] || '') + delta.content
                } else if (delta.content) {
                  // Only assistant text content goes to message-content-inner; tool results stay in tool-blocks
                  fullContent += delta.content
                }

                const tools = Object.keys(toolCallsAcc).length > 0 ? mergeToolCalls() : undefined
                setMessages((prev) =>
                  prev.map((m) =>
                    m.id === assistantId ? { ...m, content: fullContent, toolCalls: tools } : m
                  )
                )
              } catch {
                // ignore parse errors
              }
            }
          }
        }
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : '请求失败')
      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantId
            ? { ...m, content: '(请求出错，请重试)' }
            : m
        )
      )
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className="app">
      <header className="header">
        <h1>数据分析助手</h1>
        <p>基于销售数据的智能分析，支持 SQL 查询与报告生成</p>
      </header>

      <div className="messages">
        {messages.length === 0 && (
          <div className="message assistant">
            <div className="message-avatar">🤖</div>
            <div className="message-content">
              你好，我是数据分析助手。你可以问我关于销售数据的问题，例如：
              <ul style={{ margin: '0.5rem 0 0 1rem', padding: 0 }}>
                <li>分析本月销售趋势</li>
                <li>哪些品类销售额最高？</li>
                <li>促销对销售的影响</li>
              </ul>
            </div>
          </div>
        )}
        {messages.map((m) => (
          <div key={m.id} className={`message ${m.role}`}>
            <div className="message-avatar">
              {m.role === 'user' ? '👤' : '🤖'}
            </div>
            <div className="message-content">
              {m.role === 'user' ? (
                m.content
              ) : (
                <>
                  {m.role === 'assistant' && m.toolCalls && m.toolCalls.length > 0 && (
                    <div className="tool-blocks">
                      {m.toolCalls.map((tc, i) => (
                        <CollapsibleToolBlock key={tc.id || `tc-${i}`} tool={tc} />
                      ))}
                    </div>
                  )}
                  {m.content ? (
                    <MarkdownContent text={m.content} />
                  ) : loading ? (
                    <>
                      <span className="loading-dot" />
                      <span className="loading-dot" />
                      <span className="loading-dot" />
                    </>
                  ) : null}
                </>
              )}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <div className="input-area">
        <div className="input-row">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="输入你的问题..."
            rows={1}
            disabled={loading}
          />
          <button
            className="send-btn"
            onClick={sendMessage}
            disabled={loading || !input.trim()}
          >
            发送
          </button>
        </div>
        {error && <div className="error-msg">{error}</div>}
      </div>
    </div>
  )
}

export default App
