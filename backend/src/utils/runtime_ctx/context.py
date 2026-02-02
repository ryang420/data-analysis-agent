"""
Local runtime context: provides run_id, logid, project_id for logging and tracing;
default_headers for LLM calls (empty locally).
"""
import os
import uuid
from typing import Any, Optional


class Context:
    """Request-scoped context for run_id, logid, project_id, method, space_id, x_tt_env."""

    run_id: str = ""
    logid: str = ""
    project_id: str = ""
    method: str = ""
    space_id: str = ""
    x_tt_env: str = ""

    def __init__(
        self,
        run_id: str = "",
        logid: str = "",
        project_id: str = "",
        method: str = "",
        space_id: str = "",
        x_tt_env: str = "",
        **kwargs: Any,
    ):
        self.run_id = run_id or str(uuid.uuid4())
        self.logid = logid or self.run_id
        self.project_id = project_id or os.getenv("PROJECT_ID", "local")
        self.method = method or ""
        self.space_id = space_id or ""
        self.x_tt_env = x_tt_env or ""
        for k, v in kwargs.items():
            setattr(self, k, v)


def new_context(method: str = "", headers: Optional[Any] = None, **kwargs: Any) -> Context:
    """
    Create a new request context. For local runs, run_id and logid are generated.
    If headers (e.g. from FastAPI Request.headers) are provided, logid can be taken from X-Tt-Logid.
    """
    run_id = str(uuid.uuid4())
    logid = run_id
    project_id = os.getenv("PROJECT_ID", "local")

    space_id = ""
    x_tt_env = ""
    if headers is not None:
        try:
            get = getattr(headers, "get", lambda k: None)
            tt_logid = get("x-tt-logid")
            if tt_logid:
                logid = tt_logid
            space_id = get("x-tt-space-id") or ""
            x_tt_env = get("x-tt-env") or ""
        except Exception:
            pass

    return Context(
        run_id=run_id,
        logid=logid,
        project_id=project_id,
        method=method,
        space_id=space_id,
        x_tt_env=x_tt_env,
        **kwargs,
    )


def default_headers(ctx: Optional[Context]) -> dict:  # pylint: disable=unused-argument
    """
    Headers to attach to LLM API calls (e.g. trace/identity headers).
    For local runs we return an empty dict; use env OPENAI_API_KEY / OPENAI_BASE_URL.
    """
    return {}
