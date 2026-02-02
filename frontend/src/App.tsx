import { useState, useRef, useEffect } from 'react'
import './App.css'

const API_BASE = import.meta.env.VITE_API_BASE || ''

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
}

function MarkdownContent({ text }: { text: string }) {
  const lines = text.split('\n')
  const elements: React.ReactNode[] = []
  let inCodeBlock = false
  let codeBuffer: string[] = []
  let key = 0

  for (const line of lines) {
    if (line.startsWith('```')) {
      if (inCodeBlock) {
        elements.push(
          <pre key={key++}>
            <code>{codeBuffer.join('\n')}</code>
          </pre>
        )
        codeBuffer = []
      }
      inCodeBlock = !inCodeBlock
      continue
    }
    if (inCodeBlock) {
      codeBuffer.push(line)
      continue
    }
    if (line.startsWith('### ')) {
      elements.push(<h4 key={key++}>{line.slice(4)}</h4>)
    } else if (line.startsWith('## ')) {
      elements.push(<h3 key={key++}>{line.slice(3)}</h3>)
    } else if (line.startsWith('# ')) {
      elements.push(<h2 key={key++}>{line.slice(2)}</h2>)
    } else if (line.startsWith('- ') || line.startsWith('* ')) {
      elements.push(<p key={key++}>• {line.slice(2)}</p>)
    } else if (line.trim()) {
      elements.push(<p key={key++}>{line}</p>)
    } else {
      elements.push(<br key={key++} />)
    }
  }
  if (codeBuffer.length > 0) {
    elements.push(
      <pre key={key++}>
        <code>{codeBuffer.join('\n')}</code>
      </pre>
    )
  }
  return <div className="message-content-inner">{elements}</div>
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
                const delta = obj.choices?.[0]?.delta?.content
                if (delta) {
                  fullContent += delta
                  setMessages((prev) =>
                    prev.map((m) =>
                      m.id === assistantId ? { ...m, content: fullContent } : m
                    )
                  )
                }
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
              ) : m.content ? (
                <MarkdownContent text={m.content} />
              ) : loading ? (
                <>
                  <span className="loading-dot" />
                  <span className="loading-dot" />
                  <span className="loading-dot" />
                </>
              ) : null}
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
