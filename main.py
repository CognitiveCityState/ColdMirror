#!/usr/bin/env python3
"""
ColdMirror ERP PoC Unified Entry
Provides interactive menu for data generation, service startup, and test scripts.
"""

import subprocess
import sys
import os
from pathlib import Path

# Project root directory
BASE_DIR = Path(__file__).parent

def generate_data():
    """Generate demo data (inventory.csv, orders.csv, sample_order.xlsx)"""
    print("\n=== Generate Demo Data ===")
    try:
        import pandas as pd
    except ImportError:
        print("Error: pandas and openpyxl required. Please install:")
        print("  pip install pandas openpyxl")
        return

    demo_dir = BASE_DIR / "demo_data"
    demo_dir.mkdir(exist_ok=True)

    # 1. Inventory data
    inventory = [
        {"product_id": "P001", "name": "Bolt", "quantity": 85},
        {"product_id": "P002", "name": "Nut", "quantity": 230},
        {"product_id": "P003", "name": "Washer", "quantity": 500},
    ]
    import csv
    with open(demo_dir / "inventory.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["product_id", "name", "quantity"])
        writer.writeheader()
        writer.writerows(inventory)
    print("[OK] inventory.csv generated")

    # 2. Orders data
    orders = [
        {"order_id": "ORD001", "product_id": "P001", "quantity": 100, "status": "pending", "created_at": "2025-01-10"},
        {"order_id": "ORD002", "product_id": "P002", "quantity": 50, "status": "completed", "created_at": "2025-01-12"},
    ]
    with open(demo_dir / "orders.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["order_id", "product_id", "quantity", "status", "created_at"])
        writer.writeheader()
        writer.writerows(orders)
    print("[OK] orders.csv generated")

    # 3. Sample Excel file
    df = pd.DataFrame([
        {"product_id": "P001", "quantity": 200},
        {"product_id": "P002", "quantity": 80},
        {"product_id": "P003", "quantity": 100},
    ])
    df.to_excel(demo_dir / "sample_order.xlsx", index=False)
    print("[OK] sample_order.xlsx generated")
    print("Data generation completed.\n")

def start_cage():
    """Start CAGE service (runs in foreground)"""
    print("\n=== Start CAGE Service ===")
    print("CAGE service will run in this terminal. Press Ctrl+C to stop.")
    print("After starting, open another terminal to run other features.")
    input("Press Enter to continue...")
    subprocess.run([sys.executable, "cage_server.py"], cwd=BASE_DIR)

def start_erp():
    """Start ERP simulator (runs in foreground)"""
    print("\n=== Start ERP Simulator ===")
    print("ERP simulator will run in this terminal. Press Ctrl+C to stop.")
    print("After starting, open another terminal to run other features.")
    input("Press Enter to continue...")
    subprocess.run([sys.executable, "erp_simulator.py"], cwd=BASE_DIR)

def run_query_agent():
    """Run query assistant script"""
    print("\n=== Run Query Assistant ===")
    print("Please ensure CAGE service and ERP simulator are already running (in other terminals).")
    input("Press Enter to continue...")
    subprocess.run([sys.executable, "query_agent.py"], cwd=BASE_DIR)

def run_excel_importer():
    """Run Excel importer script"""
    print("\n=== Run Excel Importer ===")
    print("Please ensure CAGE service and ERP simulator are already running (in other terminals).")
    input("Press Enter to continue...")
    subprocess.run([sys.executable, "excel_importer.py"], cwd=BASE_DIR)

def show_menu():
    """Display main menu"""
    print("\n" + "="*50)
    print("ColdMirror ERP PoC Toolbox")
    print("="*50)
    print("1. Generate demo data (inventory.csv, orders.csv, sample_order.xlsx)")
    print("2. Start CAGE service")
    print("3. Start ERP simulator")
    print("4. Run query assistant")
    print("5. Run Excel importer")
    print("0. Exit")
    print("="*50)

def main():
    while True:
        show_menu()
        choice = input("Select an option: ").strip()
        if choice == "1":
            generate_data()
        elif choice == "2":
            start_cage()
        elif choice == "3":
            start_erp()
        elif choice == "4":
            run_query_agent()
        elif choice == "5":
            run_excel_importer()
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    main()