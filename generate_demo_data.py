import csv
import pandas as pd
from pathlib import Path

# 确保 demo_data 目录存在
DEMO_DIR = Path(__file__).parent / "demo_data"
DEMO_DIR.mkdir(exist_ok=True)

# 1. 生成库存数据 inventory.csv
inventory_data = [
    {"product_id": "P001", "name": "螺栓", "quantity": 85},
    {"product_id": "P002", "name": "螺母", "quantity": 230},
    {"product_id": "P003", "name": "垫圈", "quantity": 500},
]
with open(DEMO_DIR / "inventory.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["product_id", "name", "quantity"])
    writer.writeheader()
    writer.writerows(inventory_data)
print("已生成 inventory.csv")

# 2. 生成订单数据 orders.csv
orders_data = [
    {"order_id": "ORD001", "product_id": "P001", "quantity": 100, "status": "pending", "created_at": "2025-01-10"},
    {"order_id": "ORD002", "product_id": "P002", "quantity": 50, "status": "completed", "created_at": "2025-01-12"},
]
with open(DEMO_DIR / "orders.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["order_id", "product_id", "quantity", "status", "created_at"])
    writer.writeheader()
    writer.writerows(orders_data)
print("已生成 orders.csv")

# 3. 生成待导入 Excel sample_order.xlsx
df = pd.DataFrame([
    {"product_id": "P001", "quantity": 200},
    {"product_id": "P002", "quantity": 80},
    {"product_id": "P003", "quantity": 100},
])
df.to_excel(DEMO_DIR / "sample_order.xlsx", index=False)
print("已生成 sample_order.xlsx")