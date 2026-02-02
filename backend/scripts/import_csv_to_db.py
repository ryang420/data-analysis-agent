#!/usr/bin/env python3
"""
Import CSV data to database. Run from project root:
  PYTHONPATH=backend/src python backend/scripts/import_csv_to_db.py
"""
import os
import sys

# Backend dir (parent of scripts/) and src path
_script_dir = os.path.dirname(os.path.abspath(__file__))
_backend_dir = os.getenv("PROJECT_ROOT", os.getenv("WORKSPACE_PATH", os.path.dirname(_script_dir)))
_src = os.path.join(_backend_dir, "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

import pandas as pd
from storage.database.db import get_session
from storage.database.shared.model import SalesData

# Read CSV file
csv_path = os.path.join(_backend_dir, "assets", "sales_data.csv")
df = pd.read_csv(csv_path)

# Print basic info
print(f"Total rows: {len(df)}")
print(f"Columns: {df.columns.tolist()}")
print(f"First few rows:\n{df.head()}")

# Create column name mapping (Chinese to English)
column_mapping = {
    "顾客编号": "customer_id",
    "大类编码": "big_category_code",
    "大类名称": "big_category_name",
    "中类编码": "mid_category_code",
    "中类名称": "mid_category_name",
    "小类编码": "small_category_code",
    "小类名称": "small_category_name",
    "销售日期": "sale_date",
    "销售月份": "sale_month",
    "商品编码": "product_code",
    "规格型号": "spec_model",
    "商品类型": "product_type",
    "单位": "unit",
    "销售数量": "sale_quantity",
    "销售金额": "sale_amount",
    "商品单价": "unit_price",
    "是否促销": "is_promotion",
}

# Rename columns
df.rename(columns=column_mapping, inplace=True)

# Convert data types
integer_fields = [
    "customer_id",
    "big_category_code",
    "mid_category_code",
    "small_category_code",
]
string_fields = ["sale_date", "sale_month", "is_promotion"]

# Handle NaN values for integer fields (fill with 0 or drop)
for field in integer_fields:
    df[field] = df[field].fillna(0).astype(int)

# Handle NaN values for string fields (fill with empty string)
for field in string_fields:
    df[field] = df[field].fillna("").astype(str)

# Convert to list of dictionaries
records = df.to_dict("records")

# Insert to database
db = get_session()
try:
    # Batch insert
    db.bulk_insert_mappings(SalesData, records)
    db.commit()
    print(f"Successfully inserted {len(records)} records into sales_data table")
except Exception as e:
    db.rollback()
    print(f"Error inserting data: {e}")
    raise
finally:
    db.close()
