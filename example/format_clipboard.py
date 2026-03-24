import requests
import pyperclip   # 需要安装：pip install pyperclip

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
    # 从剪贴板获取文本
    text = pyperclip.paste()
    if not text:
        print("剪贴板为空")
        return

    token = request_cage_token("format_clipboard", {"text": text})
    formatted = execute_cage_token(token)
    pyperclip.copy(formatted)
    print("已格式化并写回剪贴板")

if __name__ == "__main__":
    main()