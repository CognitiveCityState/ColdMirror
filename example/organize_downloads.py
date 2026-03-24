import requests

CAGE_URL = "http://127.0.0.1:5000"

def request_cage_token(action, params):
    resp = requests.post(f"{CAGE_URL}/request_token", json={"action": action, "params": params})
    if resp.status_code != 200:
        raise PermissionError(resp.json().get("error"))
    return resp.json()["token"]

def execute_cage_token(token):
    resp = requests.post(f"{CAGE_URL}/execute", json={"token": token})
    if resp.status_code != 200:
        raise RuntimeError(resp.json().get("error"))
    return resp.json()["result"]

def main():
    # 使用安全演示目录中的模拟路径（请勿修改为真实系统路径）
    source_dir = "./demo_safe/Downloads"
    target_base = "./demo_safe/Documents"

    print(f"将整理 {source_dir} 中的文件到 {target_base}")
    token = request_cage_token("organize_downloads", {
        "source_dir": source_dir,
        "target_base": target_base
    })
    result = execute_cage_token(token)
    print(result)

if __name__ == "__main__":
    main()