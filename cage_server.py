import secrets
import logging
import requests
from flask import Flask, request, jsonify

# 配置日志（控制台+文件）
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

# 动作白名单及其参数校验规则
ALLOWED_ACTIONS = {
    "erp_query_inventory": {
        "params": {},
        "check": lambda params: True
    },
    "erp_query_orders": {
        "params": {},
        "check": lambda params: True
    },
    "erp_export_orders": {
        "params": {"format": str},
        "check": lambda params: params.get("format") == "csv"
    },
    "erp_create_order": {
        "params": {"product_id": str, "quantity": int},
        "check": lambda params: True
    }
}

# ERP 模拟器地址（假设运行在 5001 端口）
ERP_URL = "http://127.0.0.1:5001"

def do_action(action, params):
    """执行实际操作：通过 HTTP 调用 ERP 模拟器"""
    if action == "erp_query_inventory":
        resp = requests.get(f"{ERP_URL}/inventory")
        return resp.text
    elif action == "erp_query_orders":
        resp = requests.get(f"{ERP_URL}/orders")
        return resp.text
    elif action == "erp_export_orders":
        resp = requests.get(f"{ERP_URL}/export/orders")
        # 保存为本地文件
        filename = "orders_export.csv"
        with open(filename, "wb") as f:
            f.write(resp.content)
        return f"已导出到 {filename}"
    elif action == "erp_create_order":
        resp = requests.post(f"{ERP_URL}/orders", json=params)
        return resp.text
    else:
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
    # 参数类型检查
    for k, t in rule["params"].items():
        if not isinstance(params.get(k), t):
            logging.warning(f"拒绝：参数 {k} 类型错误，期望 {t}")
            return jsonify({"error": f"参数 {k} 类型错误"}), 400
    # 自定义校验
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
    try:
        result = do_action(action, params)
        logging.info(f"执行结果: {result}")
        return jsonify({"result": result})
    except Exception as e:
        logging.error(f"执行异常: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)