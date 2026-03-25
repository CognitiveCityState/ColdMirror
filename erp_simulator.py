import csv
from pathlib import Path
from flask import Flask, request, jsonify, send_file
from io import StringIO, BytesIO

app = Flask(__name__)

# 加载初始库存数据
inventory = []
inventory_file = Path(__file__).parent / "demo_data" / "inventory.csv"
if inventory_file.exists():
    with open(inventory_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["quantity"] = int(row["quantity"])
            inventory.append(row)
else:
    # 默认数据（文件不存在时）
    inventory = [
        {"product_id": "P001", "name": "螺栓", "quantity": 85},
        {"product_id": "P002", "name": "螺母", "quantity": 230},
        {"product_id": "P003", "name": "垫圈", "quantity": 500},
    ]

# 加载初始订单数据
orders = []
orders_file = Path(__file__).parent / "demo_data" / "orders.csv"
if orders_file.exists():
    with open(orders_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["quantity"] = int(row["quantity"])
            orders.append(row)
else:
    # 默认数据
    orders = [
        {"order_id": "ORD001", "product_id": "P001", "quantity": 100, "status": "pending", "created_at": "2025-01-10"},
        {"order_id": "ORD002", "product_id": "P002", "quantity": 50, "status": "completed", "created_at": "2025-01-12"},
    ]

@app.route('/inventory', methods=['GET'])
def get_inventory():
    return jsonify(inventory)

@app.route('/orders', methods=['GET'])
def get_orders():
    return jsonify(orders)

@app.route('/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    new_order = {
        "order_id": f"ORD{len(orders)+1:03d}",
        "product_id": data["product_id"],
        "quantity": data["quantity"],
        "status": "pending",
        "created_at": data.get("created_at", "2025-03-25")
    }
    orders.append(new_order)
    return jsonify(new_order), 201

@app.route('/export/orders', methods=['GET'])
def export_orders():
    # 将订单导出为 CSV
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=["order_id", "product_id", "quantity", "status", "created_at"])
    writer.writeheader()
    writer.writerows(orders)
    output.seek(0)
    return send_file(BytesIO(output.getvalue().encode()), mimetype='text/csv', as_attachment=True, download_name='orders_export.csv')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001)