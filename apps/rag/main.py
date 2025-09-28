from fastapi import FastAPI, Request, Depends
from apps.common import get_logger_with_trace
from fastapi.responses import JSONResponse
import logging, time

def create_app() -> FastAPI:
    app = FastAPI(title="RAG Service")

    def get_rag_logger(request: Request) -> logging.LoggerAdapter:
        from main import rag_app  # 运行时导入，避免循环引用
        return get_logger_with_trace(rag_app, request)

    # ✅ 全局异常处理器 —— 记 rag_error，并返回带 trace_id 的 JSON
    @app.exception_handler(Exception)
    async def rag_exception_handler(request: Request, exc: Exception):
        from main import rag_error  # 一定要拿 error logger
        err_logger = get_logger_with_trace(rag_error, request)
        err_logger.error("Unhandled exception", exc_info=True)

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
    async def query_rag(logger=Depends(get_rag_logger)):
        logger.info("RAG 查询业务开始执行")
        result = {"answer": "这是 RAG 查询结果"}
        logger.info(f"RAG 查询结果: {result}")
        return result

    @app.get("/test-error")
    async def test_error():
        1/0  # 故意触发错误

    @app.get("/test-perf")
    async def test_perf(logger=Depends(get_rag_logger)):
        start = time.time()
        time.sleep(0.05)
        cost = (time.time() - start) * 1000
        logger.info(f"RAG 性能测试完成，耗时 {cost:.2f} ms")
        return {"perf": f"{cost:.2f} ms"}

    return app
