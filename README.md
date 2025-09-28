# FastAPI Logging Template (per-project logs + JSON + Trace ID)

## Run
```bash
python -m venv .venv && . .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8081
```

## Configuration
- `.env` 汇总了 FastAPI 服务的基础配置以及日志参数：
  - `LOG_LEVEL`、`LOG_ROOT` 与 `LOG_BACKUP_DAYS` 控制日志等级、存储目录与保留天数；
  - `LOG_PROJECT_<SERVICE>`（如 `LOG_PROJECT_RAG`）分别以 JSON 定义各子项目是否启用及输出的日志类别。
- 启动时会自动读取这些环境变量，无需再提供单独的 `logging.yaml` 文件。

## Test (manual)
```bash
curl http://127.0.0.1:8081/rag/query
curl http://127.0.0.1:8081/rag/test-error
curl http://127.0.0.1:8081/rag/test-perf
```

## Test (script)
```bash
python tests/run_tests.py
```
