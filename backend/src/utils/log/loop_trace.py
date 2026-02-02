"""
Run config with optional Loop tracing. When cozeloop is not installed, only Logger is used.
"""
import os
import logging
from langchain_core.runnables import RunnableConfig
from utils.log.common import get_execute_mode
from utils.log.node_log import Logger

logger = logging.getLogger(__name__)

loop_tracer = None
try:
    import cozeloop
    from cozeloop.integration.langchain.trace_callback import LoopTracer
    space_id = os.getenv("PROJECT_SPACE_ID", "YOUR_SPACE_ID")
    api_token = os.getenv("LOOP_API_TOKEN", "YOUR_LOOP_API_TOKEN")
    base_url = os.getenv("LOOP_BASE_URL", "https://api.coze.cn")
    loop_tracer = cozeloop.new_client(
        workspace_id=space_id,
        api_token=api_token,
        api_base_url=base_url,
    )
    cozeloop.set_default_client(loop_tracer)
except Exception as e:
    logger.debug("Loop tracer not available, tracing disabled: %s", e)

commit_hash = os.getenv("PROJECT_COMMIT_HASH", "")


def init_run_config(graph, ctx):
    tracer = Logger(graph, ctx)
    tracer.on_chain_start = tracer.on_chain_start_graph
    tracer.on_chain_end = tracer.on_chain_end_graph
    callbacks = [tracer]
    if loop_tracer is not None:
        try:
            trace_callback_handler = LoopTracer.get_callback_handler(
                loop_tracer,
                add_tags_fn=tracer.get_node_tags,
                modify_name_fn=tracer.get_node_name,
                tags={
                    "project_id": ctx.project_id,
                    "execute_mode": get_execute_mode(),
                    "log_id": ctx.logid,
                    "commit_hash": commit_hash,
                },
            )
            callbacks.append(trace_callback_handler)
        except Exception as e:
            logger.debug("LoopTracer handler skipped: %s", e)
    return RunnableConfig(callbacks=callbacks)


def init_agent_config(graph, ctx):
    callbacks = []
    if loop_tracer is not None:
        try:
            callbacks.append(
                LoopTracer.get_callback_handler(
                    loop_tracer,
                    tags={
                        "project_id": ctx.project_id,
                        "execute_mode": get_execute_mode(),
                        "log_id": ctx.logid,
                        "commit_hash": commit_hash,
                    },
                )
            )
        except Exception as e:
            logger.debug("LoopTracer handler skipped: %s", e)
    return RunnableConfig(callbacks=callbacks)


def add_trace_tags(trace, tags):
    """Add tags to trace; no-op if trace has no set_tags (e.g. when loop tracer not used)."""
    if hasattr(trace, "set_tags"):
        trace.set_tags(tags)
