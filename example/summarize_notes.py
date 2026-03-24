import requests
from pathlib import Path

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
    input_path = "./demo_safe/notes.txt"
    output_path = "./demo_safe/summary.md"

    token = request_cage_token("summarize_notes", {
        "input_path": input_path,
        "output_path": output_path
    })
    result = execute_cage_token(token)
    print(result)

if __name__ == "__main__":
    main()