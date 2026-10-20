
import random
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

random.seed(42)

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "ecommerce.db"

products = [
    ("Laptop", "Electronics", 850),
    ("Headphones", "Electronics", 75),
    ("Smartphone", "Electronics", 600),
    ("Office Chair", "Furniture", 180),
    ("Desk", "Furniture", 250),
    ("Coffee Maker", "Home", 65),
    ("Backpack", "Accessories", 45),
    ("Watch", "Accessories", 120),
    ("Running Shoes", "Fashion", 90),
    ("Jacket", "Fashion", 110),
]

regions = ["North", "South", "East", "West", "Central"]
statuses = ["Delivered", "Delivered", "Delivered", "Cancelled", "Returned"]

start_date = datetime(2025, 1, 1)
orders = []

for order_id in range(1, 2001):
    product_id = random.randint(0, len(products) - 1)
    product_name, category, price = products[product_id]

    quantity = random.randint(1, 4)
    discount = random.choice([0, 0, 0.05, 0.10, 0.15])
    order_date = start_date + timedelta(days=random.randint(0, 364))
    status = random.choice(statuses)

    orders.append({
        "order_id": order_id,
        "order_date": order_date.strftime("%Y-%m-%d"),
        "customer_id": random.randint(1001, 1500),
        "product_name": product_name,
        "category": category,
        "region": random.choice(regions),
        "quantity": quantity,
        "unit_price": price,
        "discount": discount,
        "status": status,
        "revenue": round(quantity * price * (1 - discount), 2),
    })

df = pd.DataFrame(orders)

with sqlite3.connect(DB_PATH) as conn:
    df.to_sql("orders", conn, if_exists="replace", index=False)

    result = pd.read_sql_query(
        """
        SELECT
            COUNT(*) AS total_orders,
            ROUND(SUM(revenue), 2) AS total_revenue,
            COUNT(DISTINCT customer_id) AS unique_customers
        FROM orders
        WHERE status = 'Delivered'
        """,
        conn,
    )

print(f"Database created: {DB_PATH}")
print(f"Rows inserted: {len(df)}")
print("\nDelivered-order summary:")
print(result.to_string(index=False))
