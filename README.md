# FastAPI Logging Template (per-project logs + JSON + Trace ID)

## Run
```bash
python -m venv .venv && . .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8081
```

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
