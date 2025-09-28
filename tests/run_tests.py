import os
import json
import requests

BASE_URL = "http://127.0.0.1:8081"

TEST_ENDPOINTS = {
    "rag": ["/query", "/test-error", "/test-perf"],
    "text2sql": ["/query", "/test-error"],
    "uie": ["/query", "/test-error"],
}

def check_log_file(project: str, category: str):
    log_file = f"logs/{project}/{category}.log"
    if not os.path.exists(log_file):
        print(f"[❌] {project}/{category}.log 未生成")
        return
    with open(log_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
        if not lines:
            print(f"[❌] {project}/{category}.log 为空")
            return
        last_log = json.loads(lines[-1])
        trace_id = last_log.get("trace_id")
        print(f"[✅] {project}/{category}.log 最后一条 trace_id={trace_id}")
        # print(f"     {last_log}")

def run_tests():
    for project, endpoints in TEST_ENDPOINTS.items():
        print(f"\n=== 测试子项目: {project} ===")
        for ep in endpoints:
            url = f"{BASE_URL}/{project}{ep}"
            print(f"\n请求: {url}")
            try:
                resp = requests.get(url)
                print(f"响应状态: {resp.status_code}")
                print(f"响应体: {resp.text}")
                print(f"Trace ID (header): {resp.headers.get('X-Trace-ID')}")
            except Exception as e:
                print(f"[❌] 请求失败: {e}")
                continue
            if "error" in ep:
                check_log_file(project, "error")
            elif "perf" in ep:
                check_log_file(project, "perf")
            else:
                check_log_file(project, "app")
                check_log_file(project, "access")

if __name__ == "__main__":
    run_tests()
