from fastapi import FastAPI, Request, Depends, HTTPException
from apps.common import get_logger_with_trace, read_document
from fastapi.responses import JSONResponse
import logging

def create_app() -> FastAPI:
    app = FastAPI(title="Text2SQL Service")

    def get_t2s_logger(request: Request) -> logging.LoggerAdapter:
        from main import t2s_app
        return get_logger_with_trace(t2s_app, request)
    
    # ✅ 新增：子应用的全局异常处理器
    @app.exception_handler(Exception)
    async def t2s_exception_handler(request: Request, exc: Exception):
        from main import t2s_error  # 运行时导入子项目的 error logger
        err_logger = get_logger_with_trace(t2s_error, request)
        err_logger.error("Unhandled exception", exc_info=True)  # 带堆栈

        trace_id = getattr(request.state, "trace_id", None)
        headers = {}
        if trace_id:
            headers["X-Trace-ID"] = trace_id

        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error", "trace_id": trace_id},
            headers=headers
        )


    @app.get("/query")
    async def query_t2s(logger=Depends(get_t2s_logger)):
        logger.info("Text2SQL 查询开始")
        result = {"sql": "SELECT * FROM sales LIMIT 10;"}
        logger.info(f"生成的 SQL: {result['sql']}")
        return result

    @app.get("/test-error")
    async def test_error():
        raise ValueError("模拟业务异常")

    @app.get("/data/sample")
    async def read_sample_prompt(logger=Depends(get_t2s_logger)):
        try:
            content = read_document("text2sql", "example_prompt.sql")
        except FileNotFoundError as exc:
            logger.warning("Text2SQL 示例 prompt 不存在", extra={"filename": "example_prompt.sql"})
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        logger.info("返回 Text2SQL 示例 prompt")
        return {"filename": "example_prompt.sql", "content": content}

    return app
