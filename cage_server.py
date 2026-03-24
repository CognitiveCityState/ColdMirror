import secrets
import shutil
import os
import logging
import re
from pathlib import Path
from flask import Flask, request, jsonify

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("cage.log"),
        logging.StreamHandler()
    ]
)

app = Flask(__name__)

# 存储一次性令牌
tokens = {}

# 安全演示根目录（所有操作限定在此目录下）
DEMO_ROOT = Path(__file__).parent / "demo_safe"
DEMO_ROOT.mkdir(exist_ok=True)

DOWNLOAD_DIR = DEMO_ROOT / "Downloads"
DOCUMENTS_DIR = DEMO_ROOT / "Documents"
NOTES_FILE = DEMO_ROOT / "notes.txt"
OUTPUT_DIR = DEMO_ROOT

DOWNLOAD_DIR.mkdir(exist_ok=True)
DOCUMENTS_DIR.mkdir(exist_ok=True)

sample_files = [
    (DOWNLOAD_DIR / "cat.jpg", b"fake jpg content"),
    (DOWNLOAD_DIR / "report.pdf", b"fake pdf content"),
    (DOWNLOAD_DIR / "archive.zip", b"fake zip content"),
    (DOWNLOAD_DIR / "readme.txt", b"some notes")
]
for path, content in sample_files:
    if not path.exists():
        path.write_bytes(content)

if not NOTES_FILE.exists():
    NOTES_FILE.write_text("""
2026-03-24 讨论 CAGE 架构
- 安全隔离优于行为约束
- 一次性令牌机制
- 极轻量实现

2026-03-25 验证 PoC
- 三个场景已通过
- 下一步集成 ColdMirror
""", encoding='utf-8')

ALLOWED_ACTIONS = {
    "organize_downloads": {
        "params": {"source_dir": str, "target_base": str},
        "check": lambda params: (
            Path(params["source_dir"]).resolve() == DOWNLOAD_DIR.resolve() and
            Path(params["target_base"]).resolve() == DOCUMENTS_DIR.resolve()
        )
    },
    "format_clipboard": {
        "params": {"text": str},
        "check": lambda params: True
    },
    "summarize_notes": {
        "params": {"input_path": str, "output_path": str},
        "check": lambda params: (
            Path(params["input_path"]).resolve() == NOTES_FILE.resolve() and
            Path(params["output_path"]).resolve().parent == DEMO_ROOT.resolve()
        )
    }
}

def smart_format(text: str) -> str:
    # 极简处理：保留原始内容，只加项目符号，完全稳定
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    return "\n".join([f"- {line}" for line in lines])

def do_action(action, params):
    """执行实际操作（仅限 demo_safe 内）"""
    if action == "organize_downloads":
        source = Path(params["source_dir"])
        target_base = Path(params["target_base"])
        for f in source.iterdir():
            if not f.is_file():
                continue
            ext = f.suffix.lower()
            if ext in ['.jpg', '.png', '.gif']:
                dest = target_base / "Pictures"
            elif ext in ['.pdf', '.docx', '.txt']:
                dest = target_base / "Documents"
            elif ext in ['.zip', '.rar', '.7z']:
                dest = target_base / "Archives"
            else:
                continue
            dest.mkdir(exist_ok=True)
            shutil.move(str(f), str(dest / f.name))
        return f"已整理 {source} 中的文件"
    elif action == "format_clipboard":
        text = params["text"]
        formatted = smart_format(text)
        return formatted
    elif action == "summarize_notes":
        input_path = Path(params["input_path"])
        output_path = Path(params["output_path"])
        content = input_path.read_text(encoding='utf-8')
        summary = content[:200] + "..." if len(content) > 200 else content
        output_path.write_text(f"# 每日简报\n\n{summary}", encoding='utf-8')
        return f"已生成简报: {output_path}"
    return "未知操作"

@app.route('/request_token', methods=['POST'])
def request_token():
    data = request.get_json()
    action = data.get("action")
    params = data.get("params", {})
    logging.info(f"收到令牌请求: action={action}, params={params}")

    if action not in ALLOWED_ACTIONS:
        logging.warning(f"拒绝：未授权操作 {action}")
        return jsonify({"error": f"禁止的操作: {action}"}), 403

    rule = ALLOWED_ACTIONS[action]
    for k, t in rule["params"].items():
        if not isinstance(params.get(k), t):
            logging.warning(f"拒绝：参数类型错误 {k}")
            return jsonify({"error": f"参数 {k} 类型错误"}), 400
    if not rule["check"](params):
        logging.warning(f"拒绝：参数不符合安全规则 {params}")
        return jsonify({"error": "参数不符合安全规则"}), 403

    token = secrets.token_hex(16)
    tokens[token] = (action, params)
    logging.info(f"令牌生成: {token} -> {action}")
    return jsonify({"token": token})

@app.route('/execute', methods=['POST'])
def execute():
    data = request.get_json()
    token = data.get("token")
    logging.info(f"收到执行请求: token={token}")

    if token not in tokens:
        logging.warning(f"拒绝：无效或已过期的令牌 {token}")
        return jsonify({"error": "无效或已过期的令牌"}), 403

    action, params = tokens.pop(token)
    logging.info(f"执行操作: {action} (令牌已销毁)")
    result = do_action(action, params)
    logging.info(f"执行结果: {result}")
    return jsonify({"result": result})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)