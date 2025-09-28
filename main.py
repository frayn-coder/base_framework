import uuid

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from apps.common import LoggerManager, get_settings
from apps.rag.main import create_app as create_rag
from apps.text2sql.main import create_app as create_t2s
from apps.uie.main import create_app as create_uie

settings = get_settings()

logger_manager = LoggerManager(settings.logging_config)

# 子项目日志器
rag_access = logger_manager.get_project_logger("rag", "access")
rag_error  = logger_manager.get_project_logger("rag", "error")
rag_app    = logger_manager.get_project_logger("rag", "app")
rag_perf   = logger_manager.get_project_logger("rag", "perf")

t2s_access = logger_manager.get_project_logger("text2sql", "access")
t2s_error  = logger_manager.get_project_logger("text2sql", "error")
t2s_app    = logger_manager.get_project_logger("text2sql", "app")
t2s_perf   = logger_manager.get_project_logger("text2sql", "perf")

uie_access = logger_manager.get_project_logger("uie", "access")
uie_error  = logger_manager.get_project_logger("uie", "error")
uie_app    = logger_manager.get_project_logger("uie", "app")
uie_perf   = logger_manager.get_project_logger("uie", "perf")

system_logger = logger_manager.system_logger

def create_main_app() -> FastAPI:
    app = FastAPI(title=settings.app_name)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.mount("/rag", create_rag(), name="rag")
    app.mount("/text2sql", create_t2s(), name="text2sql")
    app.mount("/uie", create_uie(), name="uie")

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        import time
        trace_id = str(uuid.uuid4())
        request.state.trace_id = trace_id
        start = time.time()

        try:
            response = await call_next(request)
        except Exception as e:
            path = request.url.path
            extra = {"trace_id": trace_id}
            if path.startswith("/rag"):
                rag_error.error(f"Unhandled error: {e}", exc_info=True, extra=extra)
            elif path.startswith("/text2sql"):
                t2s_error.error(f"Unhandled error: {e}", exc_info=True, extra=extra)
            elif path.startswith("/uie"):
                uie_error.error(f"Unhandled error: {e}", exc_info=True, extra=extra)
            else:
                system_logger.error(f"未分类错误: {e}", exc_info=True, extra=extra)
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal Server Error", "trace_id": trace_id},
                headers={"X-Trace-ID": trace_id},
            )

        elapsed = (time.time() - start) * 1000
        path = request.url.path
        log_msg = f"{request.method} {path} -> {response.status_code} ({elapsed:.2f}ms)"
        extra = {"trace_id": trace_id}

        if path.startswith("/rag"):
            rag_access.info(log_msg, extra=extra)
            rag_perf.info(f"{path} 耗时 {elapsed:.2f}ms", extra=extra)
        elif path.startswith("/text2sql"):
            t2s_access.info(log_msg, extra=extra)
            t2s_perf.info(f"{path} 耗时 {elapsed:.2f}ms", extra=extra)
        elif path.startswith("/uie"):
            uie_access.info(log_msg, extra=extra)
            uie_perf.info(f"{path} 耗时 {elapsed:.2f}ms", extra=extra)
        else:
            system_logger.info(f"外部请求: {log_msg}", extra=extra)

        response.headers["X-Trace-ID"] = trace_id
        return response

    system_logger.info("Unified API Server 已启动")
    return app

app = create_main_app()

if __name__ == "__main__":
    try:
        uvicorn.run(
            "main:app",
            host=settings.api_host,
            port=settings.api_port,
            reload=True,
        )
    finally:
        logger_manager.stop()
        system_logger.info("Unified API Server 已停止")
