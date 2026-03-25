import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
import json
import threading

# CAGE 服务地址
CAGE_URL = "http://127.0.0.1:5000"

def request_cage_token(action, params=None):
    """向 CAGE 申请令牌"""
    resp = requests.post(f"{CAGE_URL}/request_token", json={"action": action, "params": params or {}})
    if resp.status_code != 200:
        raise Exception(resp.json().get("error"))
    return resp.json()["token"]

def execute_cage_token(token):
    """执行令牌对应的操作"""
    resp = requests.post(f"{CAGE_URL}/execute", json={"token": token})
    if resp.status_code != 200:
        raise Exception(resp.json().get("error"))
    return resp.json()["result"]

def query_inventory():
    """查询库存（只读）"""
    token = request_cage_token("erp_query_inventory")
    result = execute_cage_token(token)
    return json.loads(result)

def query_orders():
    """查询订单（只读）"""
    token = request_cage_token("erp_query_orders")
    result = execute_cage_token(token)
    return json.loads(result)

def export_orders():
    """导出订单报表（只读）"""
    token = request_cage_token("erp_export_orders", {"format": "csv"})
    result = execute_cage_token(token)
    return result

def create_order(product_id, quantity):
    """创建订单（写入，需人工确认）"""
    token = request_cage_token("erp_create_order", {"product_id": product_id, "quantity": quantity})
    result = execute_cage_token(token)
    return json.loads(result)

class ColdMirrorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ColdMirror ERP 智能助手")
        self.root.geometry("800x600")

        # 创建菜单栏
        menubar = tk.Menu(root)
        root.config(menu=menubar)

        # 操作菜单
        action_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="操作", menu=action_menu)
        action_menu.add_command(label="查询库存", command=self.show_inventory)
        action_menu.add_command(label="查询订单", command=self.show_orders)
        action_menu.add_command(label="导出报表", command=self.export_orders)
        action_menu.add_separator()
        action_menu.add_command(label="从 Excel 导入订单", command=self.import_from_excel)

        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于", command=self.show_about)

        # 主显示区域：使用 Notebook 分页
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 库存页
        self.inventory_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.inventory_frame, text="库存")
        self.inventory_tree = ttk.Treeview(self.inventory_frame, columns=("ID", "名称", "数量"), show="headings")
        self.inventory_tree.heading("ID", text="产品ID")
        self.inventory_tree.heading("名称", text="产品名称")
        self.inventory_tree.heading("数量", text="库存数量")
        self.inventory_tree.pack(fill=tk.BOTH, expand=True)

        # 订单页
        self.orders_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.orders_frame, text="订单")
        self.orders_tree = ttk.Treeview(self.orders_frame, columns=("ID", "产品ID", "数量", "状态", "日期"), show="headings")
        self.orders_tree.heading("ID", text="订单号")
        self.orders_tree.heading("产品ID", text="产品ID")
        self.orders_tree.heading("数量", text="数量")
        self.orders_tree.heading("状态", text="状态")
        self.orders_tree.heading("日期", text="创建日期")
        self.orders_tree.pack(fill=tk.BOTH, expand=True)

        # 日志页
        self.log_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.log_frame, text="日志")
        self.log_text = scrolledtext.ScrolledText(self.log_frame, wrap=tk.WORD, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # 状态栏
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.log("ColdMirror GUI 已启动，请确保 CAGE 服务和 ERP 模拟器正在运行。")

    def log(self, msg):
        """在日志页添加消息"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def show_inventory(self):
        """显示库存"""
        self.status_var.set("正在查询库存...")
        self.root.update()
        try:
            data = query_inventory()
            self.inventory_tree.delete(*self.inventory_tree.get_children())
            for item in data:
                self.inventory_tree.insert("", tk.END, values=(item["product_id"], item["name"], item["quantity"]))
            self.log(f"查询库存成功，共 {len(data)} 条记录。")
        except Exception as e:
            messagebox.showerror("错误", f"查询库存失败：{e}")
            self.log(f"查询库存失败：{e}")
        finally:
            self.status_var.set("就绪")

    def show_orders(self):
        """显示订单"""
        self.status_var.set("正在查询订单...")
        self.root.update()
        try:
            data = query_orders()
            self.orders_tree.delete(*self.orders_tree.get_children())
            for item in data:
                self.orders_tree.insert("", tk.END, values=(item["order_id"], item["product_id"], item["quantity"], item["status"], item["created_at"]))
            self.log(f"查询订单成功，共 {len(data)} 条记录。")
        except Exception as e:
            messagebox.showerror("错误", f"查询订单失败：{e}")
            self.log(f"查询订单失败：{e}")
        finally:
            self.status_var.set("就绪")

    def export_orders(self):
        """导出订单报表"""
        self.status_var.set("正在导出报表...")
        self.root.update()
        try:
            result = export_orders()
            messagebox.showinfo("导出成功", result)
            self.log(f"导出报表成功：{result}")
        except Exception as e:
            messagebox.showerror("错误", f"导出报表失败：{e}")
            self.log(f"导出报表失败：{e}")
        finally:
            self.status_var.set("就绪")

    def import_from_excel(self):
        """从 Excel 文件导入订单（需确认）"""
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="选择 Excel 文件",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        if not file_path:
            return

        # 尝试导入 pandas（如果未安装则提示）
        try:
            import pandas as pd
        except ImportError:
            messagebox.showerror("错误", "请安装 pandas 和 openpyxl 以支持 Excel 导入：\npip install pandas openpyxl")
            return

        self.status_var.set("正在读取 Excel...")
        self.root.update()
        try:
            df = pd.read_excel(file_path)
            if "product_id" not in df.columns or "quantity" not in df.columns:
                messagebox.showerror("格式错误", "Excel 必须包含 product_id 和 quantity 两列")
                return
            orders = df[["product_id", "quantity"]].to_dict('records')
            # 确认对话框
            msg = f"即将导入 {len(orders)} 条订单，请确认：\n"
            for o in orders:
                msg += f"产品 {o['product_id']} 数量 {o['quantity']}\n"
            if not messagebox.askyesno("确认导入", msg):
                return

            # 逐条创建订单
            for o in orders:
                self.status_var.set(f"正在创建订单：产品 {o['product_id']} 数量 {o['quantity']}")
                self.root.update()
                result = create_order(o["product_id"], o["quantity"])
                self.log(f"已创建订单 {result['order_id']}: 产品 {o['product_id']} 数量 {o['quantity']}")
            messagebox.showinfo("导入完成", f"成功导入 {len(orders)} 条订单")
            # 刷新订单显示
            self.show_orders()
        except Exception as e:
            messagebox.showerror("错误", f"导入失败：{e}")
            self.log(f"导入失败：{e}")
        finally:
            self.status_var.set("就绪")

    def show_about(self):
        messagebox.showinfo("关于", "ColdMirror ERP 智能助手\n基于 CAGE 安全隔离框架\n演示版本\n\n操作原则：只读优先、确认至上、沙箱隔离")

if __name__ == "__main__":
    root = tk.Tk()
    app = ColdMirrorGUI(root)
    root.mainloop()