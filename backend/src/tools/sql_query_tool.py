"""
SQL Query Tool for data analysis.
"""
import json
from langchain.tools import tool, ToolRuntime
from storage.database.db import get_session
from sqlalchemy import text
from sqlalchemy.orm import Session


@tool
def execute_sql_query(sql: str, runtime: ToolRuntime) -> str:
    """
    Execute SQL query on the database and return results.

    This tool allows you to dynamically query the sales_data table in the database.
    The database contains supermarket sales data with the following schema:

    Table: sales_data
    - id: Integer, Primary Key
    - customer_id: Integer, Customer ID (顾客编号)
    - big_category_code: Integer, Big category code (大类编码)
    - big_category_name: String(100), Big category name (大类名称)
    - mid_category_code: Integer, Medium category code (中类编码)
    - mid_category_name: String(100), Medium category name (中类名称)
    - small_category_code: Integer, Small category code (小类编码)
    - small_category_name: String(100), Small category name (小类名称)
    - sale_date: String(20), Sale date in format YYYYMMDD (销售日期)
    - sale_month: String(20), Sale month in format YYYYMM (销售月份)
    - product_code: String(100), Product code (商品编码)
    - spec_model: String(200), Specification model (规格型号)
    - product_type: String(50), Product type (商品类型)
    - unit: String(20), Unit (单位)
    - sale_quantity: Double, Sale quantity (销售数量)
    - sale_amount: Double, Sale amount (销售金额)
    - unit_price: Double, Unit price (商品单价)
    - is_promotion: String(10), Whether on promotion (是否促销) - "是" or "否"
    - created_at: DateTime, Creation timestamp

    Args:
        sql: The SQL query to execute. Should be a SELECT statement.

    Returns:
        Query results as a formatted string (JSON or table format).

    Examples:
        - Get total sales by month:
          SELECT sale_month, SUM(sale_amount) as total_sales
          FROM sales_data
          GROUP BY sale_month
          ORDER BY sale_month;

        - Get top 10 products by sales amount:
          SELECT product_code, spec_model, SUM(sale_amount) as total_sales
          FROM sales_data
          GROUP BY product_code, spec_model
          ORDER BY total_sales DESC
          LIMIT 10;

        - Get sales by category:
          SELECT big_category_name, SUM(sale_amount) as total_sales,
                 SUM(sale_quantity) as total_quantity
          FROM sales_data
          GROUP BY big_category_name
          ORDER BY total_sales DESC;

    Notes:
        - Only use SELECT queries. Do not use INSERT, UPDATE, DELETE, or DROP.
        - The tool will format results as JSON for easy parsing.
        - Large result sets may be limited for performance.
    """
    # Validate SQL to prevent dangerous operations
    sql_upper = sql.strip().upper()
    if not sql_upper.startswith('SELECT'):
        return "Error: Only SELECT queries are allowed for data analysis."

    db: Session = get_session()
    try:
        # Execute the SQL query
        result = db.execute(text(sql))
        rows = result.fetchall()
        columns = result.keys()

        # Convert to list of dicts
        result_data = []
        for row in rows:
            row_dict = {}
            for i, col in enumerate(columns):
                value = row[i]
                # Convert datetime and other types to string
                if value is not None:
                    row_dict[col] = str(value)
                else:
                    row_dict[col] = None
            result_data.append(row_dict)

        # Format as JSON
        if not result_data:
            return "Query returned no results."

        return json.dumps({
            "columns": list(columns),
            "row_count": len(result_data),
            "data": result_data
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        return f"Error executing SQL query: {str(e)}\n\nPlease check your SQL syntax and try again."
    finally:
        db.close()


@tool
def get_table_schema(runtime: ToolRuntime) -> str:
    """
    Get the schema information of the sales_data table.

    Returns:
        A detailed description of the table structure including column names, data types, and descriptions.

    Use this tool to understand the database structure before writing SQL queries.
    """
    schema_info = """
Table: sales_data
Description: Supermarket sales data with detailed transaction information

Columns:
1. id (Integer, Primary Key)
   - Unique identifier for each record

2. customer_id (Integer)
   - Customer ID
   - Description: 顾客编号

3. big_category_code (Integer)
   - Big category code
   - Description: 大类编码

4. big_category_name (String, 100 chars)
   - Big category name
   - Description: 大类名称
   - Examples: 粮油, 日配, 冲调, 洗化, 休闲, 蔬果, etc.

5. mid_category_code (Integer)
   - Medium category code
   - Description: 中类编码

6. mid_category_name (String, 100 chars)
   - Medium category name
   - Description: 中类名称
   - Examples: 袋装速食面, 调味酱, 冷藏乳品, etc.

7. small_category_code (Integer)
   - Small category code
   - Description: 小类编码

8. small_category_name (String, 100 chars)
   - Small category name
   - Description: 小类名称
   - Examples: 猪肉口味, 番茄酱, 冷藏果粒酸乳, etc.

9. sale_date (String, 20 chars)
   - Sale date
   - Description: 销售日期
   - Format: YYYYMMDD (e.g., 20150101)

10. sale_month (String, 20 chars)
    - Sale month
    - Description: 销售月份
    - Format: YYYYMM (e.g., 201501)

11. product_code (String, 100 chars)
    - Product code
    - Description: 商品编码
    - Examples: DW-2001020021

12. spec_model (String, 200 chars)
    - Specification model
    - Description: 规格型号
    - Examples: 82.6g, 340g, 260g

13. product_type (String, 50 chars)
    - Product type
    - Description: 商品类型
    - Examples: 一般商品, 生鲜

14. unit (String, 20 chars)
    - Unit
    - Description: 单位
    - Examples: 袋, 瓶, 盒, KG, 千克

15. sale_quantity (Double)
    - Sale quantity
    - Description: 销售数量
    - Unit depends on product

16. sale_amount (Double)
    - Sale amount
    - Description: 销售金额
    - Total amount for the transaction

17. unit_price (Double)
    - Unit price
    - Description: 商品单价
    - Price per unit

18. is_promotion (String, 10 chars)
    - Whether on promotion
    - Description: 是否促销
    - Values: "是" (Yes) or "否" (No)

19. created_at (DateTime)
    - Creation timestamp
    - Description: Record creation time

Data Overview:
- Total records: 42,816
- Date range: 2015 data
- Categories: Multiple product categories including food, daily products, etc.
"""
    return schema_info
