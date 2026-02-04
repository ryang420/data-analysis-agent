"""OpenAI Chat Completions 处理器"""

import asyncio
import json
import logging
from typing import Dict, Any, Union, AsyncGenerator

from fastapi.responses import StreamingResponse, JSONResponse

from utils.runtime_ctx.context import Context
from utils.openai.types.response import OpenAIError, OpenAIErrorResponse
from utils.openai.converter.request_converter import RequestConverter
from utils.openai.converter.response_converter import ResponseConverter
from utils.error.classifier import classify_error
from utils.helper import graph_helper
from utils.log.loop_trace import init_agent_config, init_run_config

logger = logging.getLogger(__name__)


class OpenAIChatHandler:
    """OpenAI Chat Completions 处理器"""

    def __init__(self, graph_service: Any):
        """
        初始化处理器

        Args:
            graph_service: GraphService 实例
        """
        self.graph_service = graph_service
        self.request_converter = RequestConverter()

    async def handle(
        self,
        payload: Dict[str, Any],
        ctx: Context,
    ) -> Union[StreamingResponse, JSONResponse]:
        """
        处理请求，根据 stream 参数返回流式或非流式响应

        Args:
            payload: 请求体
            ctx: 上下文

        Returns:
            StreamingResponse 或 JSONResponse
        """
        try:
            # 1. 解析请求
            request = self.request_converter.parse(payload)
            session_id = self.request_converter.get_session_id(request)

            if not session_id:
                return self._error_response(
                    message="session_id is required",
                    error_type="invalid_request_error",
                    code="400001",
                    status_code=400,
                )

            # 2. 初始化响应转换器
            response_converter = ResponseConverter(
                request_id=f"chatcmpl-{ctx.run_id}",
                model=request.model,
            )

            # 3. 转换为 LangGraph 输入
            stream_input = self.request_converter.to_stream_input(request)

            if not stream_input.get("messages"):
                return self._error_response(
                    message="No user message found",
                    error_type="invalid_request_error",
                    code="400002",
                    status_code=400,
                )

            # 4. 根据 stream 参数处理
            if request.stream:
                return await self._handle_stream(
                    stream_input,
                    session_id,
                    response_converter,
                    ctx,
                )
            else:
                return await self._handle_non_stream(
                    stream_input,
                    session_id,
                    response_converter,
                    ctx,
                )

        except Exception as e:
            logger.error(f"Error in OpenAIChatHandler.handle: {e}", exc_info=True)
            return self._handle_error(e)

    async def _handle_stream(
        self,
        stream_input: Dict[str, Any],
        session_id: str,
        response_converter: ResponseConverter,
        ctx: Context,
    ) -> StreamingResponse:
        """流式响应处理 - 使用 graph.astream() 异步流"""

        async def stream_generator() -> AsyncGenerator[str, None]:
            """异步流式生成器"""
            try:
                graph = self.graph_service._get_graph(ctx)

                if graph_helper.is_agent_proj():
                    run_config = init_agent_config(graph, ctx)
                else:
                    run_config = init_run_config(graph, ctx)

                run_config["recursion_limit"] = 100
                run_config["configurable"] = {"thread_id": session_id}

                items = graph.astream(
                    stream_input,
                    stream_mode="messages",
                    config=run_config,
                    context=ctx,
                )

                async for sse_data in response_converter.iter_langgraph_stream_async(
                    items
                ):
                    yield sse_data

            except Exception as ex:
                logger.error(f"Stream producer error: {ex}", exc_info=True)
                err = classify_error(ex, {"node_name": "openai_stream"})
                error_chunk = self._create_error_sse_chunk(
                    str(err.code),
                    str(ex),
                    response_converter.request_id,
                )
                yield error_chunk
                yield "data: [DONE]\n\n"
            except asyncio.CancelledError:
                logger.info(f"Stream cancelled for run_id: {ctx.run_id}")
                raise

        return StreamingResponse(
            stream_generator(),
            media_type="text/event-stream",
        )

    async def _handle_non_stream(
        self,
        stream_input: Dict[str, Any],
        session_id: str,
        response_converter: ResponseConverter,
        ctx: Context,
    ) -> JSONResponse:
        """非流式响应处理 - 使用 graph.astream() 异步流"""
        try:
            graph = self.graph_service._get_graph(ctx)

            if graph_helper.is_agent_proj():
                run_config = init_agent_config(graph, ctx)
            else:
                run_config = init_run_config(graph, ctx)

            run_config["recursion_limit"] = 100
            run_config["configurable"] = {"thread_id": session_id}

            items = graph.astream(
                stream_input,
                stream_mode="messages",
                config=run_config,
                context=ctx,
            )

            # 收集 astream 输出后转为同步迭代器供 collect 使用
            collected: list = []
            async for item in items:
                collected.append(item)

            response = response_converter.collect_langgraph_to_response(iter(collected))
            return JSONResponse(content=response.to_dict())

        except Exception as e:
            logger.error(f"Non-stream error: {e}", exc_info=True)
            return self._handle_error(e)

    def _handle_error(self, error: Exception) -> JSONResponse:
        """错误处理，返回 OpenAI 标准错误格式"""
        err = classify_error(error, {"node_name": "openai_handler"})

        error_type = "internal_error"
        status_code = 500

        # 根据错误类型映射
        error_category = err.category.name if err.category else "System"
        if error_category in ("Invalid", "BadRequest"):
            error_type = "invalid_request_error"
            status_code = 400
        elif error_category == "TimeOut":
            error_type = "timeout_error"
            status_code = 408
        elif error_category == "NotFound":
            error_type = "not_found_error"
            status_code = 404

        return self._error_response(
            message=str(error),
            error_type=error_type,
            code=str(err.code),
            status_code=status_code,
        )

    @staticmethod
    def _error_response(
        message: str,
        error_type: str,
        code: str,
        status_code: int = 500,
    ) -> JSONResponse:
        """创建错误响应"""
        error_resp = OpenAIErrorResponse(
            error=OpenAIError(
                message=message,
                type=error_type,
                code=code,
            )
        )
        return JSONResponse(
            content=error_resp.to_dict(),
            status_code=status_code,
        )

    @staticmethod
    def _create_error_sse_chunk(
        code: str,
        message: str,
        request_id: str,
    ) -> str:
        """创建错误 SSE chunk"""
        error_data = {
            "id": request_id,
            "object": "chat.completion.chunk",
            "error": {
                "message": message,
                "type": "internal_error",
                "code": code,
            }
        }
        return f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
