import requests
import pandas as pd

CAGE_URL = "http://127.0.0.1:5000"

def request_token(action, params=None):
    resp = requests.post(f"{CAGE_URL}/request_token", json={"action": action, "params": params or {}})
    if resp.status_code != 200:
        raise Exception(resp.json().get("error"))
    return resp.json()["token"]

def execute_token(token):
    resp = requests.post(f"{CAGE_URL}/execute", json={"token": token})
    if resp.status_code != 200:
        raise Exception(resp.json().get("error"))
    return resp.json()["result"]

def main():
    # 模拟从 Excel 读取（这里手动构造数据，实际可用 pd.read_excel）
    orders_to_create = [
        {"product_id": "P001", "quantity": 200},
        {"product_id": "P002", "quantity": 80},
        {"product_id": "P003", "quantity": 100},
    ]

    print("待录入订单（来自 Excel）：")
    for i, order in enumerate(orders_to_create):
        print(f"{i+1}. 产品 {order['product_id']} 数量 {order['quantity']}")

    confirm = input("\n确认要全部录入吗？(y/n): ")
    if confirm.lower() != 'y':
        print("取消录入")
        return

    for order in orders_to_create:
        print(f"正在录入 {order['product_id']}...")
        token = request_token("erp_create_order", order)
        result = execute_token(token)
        print(result)  # 返回新订单信息
    print("所有订单已录入")

if __name__ == "__main__":
    main()