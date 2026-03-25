import requests
import json

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
    print("ERP 查询助手 (只读)")
    print("1. 查询库存")
    print("2. 查询订单")
    print("3. 导出订单报表")
    choice = input("请选择: ")

    if choice == "1":
        token = request_token("erp_query_inventory")
        result = execute_token(token)
        print("库存数据:")
        print(json.dumps(json.loads(result), indent=2, ensure_ascii=False))
    elif choice == "2":
        token = request_token("erp_query_orders")
        result = execute_token(token)
        print("订单数据:")
        print(json.dumps(json.loads(result), indent=2, ensure_ascii=False))
    elif choice == "3":
        token = request_token("erp_export_orders", {"format": "csv"})
        result = execute_token(token)
        print(result)  # 输出 "已导出到 orders_export.csv"
    else:
        print("无效选择")

if __name__ == "__main__":
    main()