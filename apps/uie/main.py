from fastapi import FastAPI, Request, Depends, HTTPException
from apps.common import get_logger_with_trace, read_document
from fastapi.responses import JSONResponse
import logging

def create_app() -> FastAPI:
    app = FastAPI(title="UIE Service")

    def get_uie_logger(request: Request) -> logging.LoggerAdapter:
        from main import uie_app
        return get_logger_with_trace(uie_app, request)
    
    # ✅ 新增：子应用的全局异常处理器
    @app.exception_handler(Exception)
    async def uie_exception_handler(request: Request, exc: Exception):
        from main import uie_error  # 运行时导入子项目的 error logger
        err_logger = get_logger_with_trace(uie_error, request)
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
    async def query_uie(logger=Depends(get_uie_logger)):
        logger.info("UIE 信息抽取开始")
        result = {"entities": ["张三", "北京"]}
        logger.info(f"抽取结果: {result}")
        return result

    @app.get("/test-error")
    async def test_error():
        return 1/0

    @app.get("/data/sample")
    async def read_sample_prompt(logger=Depends(get_uie_logger)):
        try:
            content = read_document("uie", "example_prompt.json")
        except FileNotFoundError as exc:
            logger.warning("UIE 示例 prompt 不存在", extra={"filename": "example_prompt.json"})
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        logger.info("返回 UIE 示例 prompt")
        return {"filename": "example_prompt.json", "content": content}

    return app
