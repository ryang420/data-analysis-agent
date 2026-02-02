import os
import json
from typing import Annotated
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage
from utils.runtime_ctx.context import default_headers
from storage.memory.memory_saver import get_memory_saver
from tools.sql_query_tool import execute_sql_query, get_table_schema

LLM_CONFIG = "config/agent_llm_config.json"

# 默认保留最近 20 轮对话 (40 条消息)
MAX_MESSAGES = 40

def _windowed_messages(old, new):
    """滑动窗口: 只保留最近 MAX_MESSAGES 条消息"""
    return add_messages(old, new)[-MAX_MESSAGES:]  # type: ignore

class AgentState(MessagesState):
    messages: Annotated[list[AnyMessage], _windowed_messages]

def build_agent(ctx=None):
    # Config path: PROJECT_ROOT or WORKSPACE_PATH or cwd; fallback to parent when running from src/
    workspace_path = os.getenv("PROJECT_ROOT") or os.getenv("WORKSPACE_PATH") or os.getcwd()
    config_path = os.path.join(workspace_path, LLM_CONFIG)
    if not os.path.isfile(config_path):
        config_path = os.path.abspath(os.path.join(os.getcwd(), "..", LLM_CONFIG))

    with open(config_path, 'r', encoding='utf-8') as f:
        cfg = json.load(f)

    # Local: OPENAI_API_KEY / OPENAI_BASE_URL; platform: WORKLOAD_IDENTITY_API_KEY / INTEGRATION_MODEL_BASE_URL
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("WORKLOAD_IDENTITY_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL") or os.getenv("INTEGRATION_MODEL_BASE_URL") or None

    llm_kw: dict = {
        "model": cfg['config'].get("model"),
        "api_key": api_key,
        "temperature": cfg['config'].get('temperature', 0.7),
        "streaming": True,
        "timeout": cfg['config'].get('timeout', 600),
        "default_headers": default_headers(ctx) if ctx else {},
    }
    if base_url:
        llm_kw["base_url"] = base_url
    # Only send extra_body.thinking when using a custom base_url; OpenAI API does not support it
    if base_url and cfg['config'].get('thinking') not in (None, '', 'disabled'):
        llm_kw["extra_body"] = {"thinking": {"type": cfg['config'].get('thinking', 'disabled')}}
    llm = ChatOpenAI(**llm_kw)

    return create_agent(
        model=llm,
        system_prompt=cfg.get("sp"),
        tools=[execute_sql_query, get_table_schema],
        checkpointer=get_memory_saver(),
        state_schema=AgentState,
    )
