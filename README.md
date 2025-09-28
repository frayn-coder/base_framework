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

## Service layout
每个子应用（`apps/rag`、`apps/text2sql`、`apps/uie`）都按照 "分层目录" 组织，便于后续扩展复杂业务：

```
apps/<service>/
├── main.py            # 应用工厂，注册路由与异常处理
├── routers/           # FastAPI 路由层，依赖注入、返回 Pydantic schema
├── services/          # 业务实现，纯 Python 函数，便于测试
├── schemas/           # Pydantic 数据模型
└── utils/             # 辅助方法（如日志、异常处理）
```

示例路由 `routers/sample.py` 展示了如何组合服务层逻辑、日志依赖与数据读写，后续可以按领域继续拆分多个 router/service 模块。

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
