-- 建表脚本：sales_data（超市销售数据）
-- 使用方式：psql -h localhost -U your_user -d your_db -f scripts/create_sales_data_table.sql
-- 或：PGPASSWORD=xxx psql -h localhost -U your_user -d your_db -f scripts/create_sales_data_table.sql

-- 若表已存在则先删除（可选，初次建表可注释掉）
-- DROP TABLE IF EXISTS sales_data;

CREATE TABLE IF NOT EXISTS sales_data (
    id              SERIAL PRIMARY KEY,
    customer_id      INTEGER NOT NULL,                    -- 顾客编号
    big_category_code   INTEGER NOT NULL,                 -- 大类编码
    big_category_name   VARCHAR(100) NOT NULL,           -- 大类名称
    mid_category_code   INTEGER NOT NULL,                 -- 中类编码
    mid_category_name   VARCHAR(100) NOT NULL,            -- 中类名称
    small_category_code INTEGER NOT NULL,                 -- 小类编码
    small_category_name VARCHAR(100) NOT NULL,            -- 小类名称
    sale_date        VARCHAR(20) NOT NULL,                -- 销售日期 YYYYMMDD
    sale_month       VARCHAR(20) NOT NULL,                -- 销售月份 YYYYMM
    product_code     VARCHAR(100) NOT NULL,                -- 商品编码
    spec_model       VARCHAR(200) NOT NULL,              -- 规格型号
    product_type     VARCHAR(50) NOT NULL,               -- 商品类型
    unit             VARCHAR(20) NOT NULL,               -- 单位
    sale_quantity    DOUBLE PRECISION NOT NULL,          -- 销售数量
    sale_amount      DOUBLE PRECISION NOT NULL,          -- 销售金额
    unit_price       DOUBLE PRECISION NOT NULL,          -- 商品单价
    is_promotion     VARCHAR(10) NOT NULL,               -- 是否促销：是/否
    created_at       TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()  -- 创建时间
);

-- 可选：常用查询索引
CREATE INDEX IF NOT EXISTS idx_sales_data_sale_month ON sales_data (sale_month);
CREATE INDEX IF NOT EXISTS idx_sales_data_sale_date ON sales_data (sale_date);
CREATE INDEX IF NOT EXISTS idx_sales_data_big_category ON sales_data (big_category_code);
CREATE INDEX IF NOT EXISTS idx_sales_data_product_code ON sales_data (product_code);

COMMENT ON TABLE sales_data IS '超市销售数据';
COMMENT ON COLUMN sales_data.customer_id IS '顾客编号';
COMMENT ON COLUMN sales_data.big_category_code IS '大类编码';
COMMENT ON COLUMN sales_data.big_category_name IS '大类名称';
COMMENT ON COLUMN sales_data.mid_category_code IS '中类编码';
COMMENT ON COLUMN sales_data.mid_category_name IS '中类名称';
COMMENT ON COLUMN sales_data.small_category_code IS '小类编码';
COMMENT ON COLUMN sales_data.small_category_name IS '小类名称';
COMMENT ON COLUMN sales_data.sale_date IS '销售日期 YYYYMMDD';
COMMENT ON COLUMN sales_data.sale_month IS '销售月份 YYYYMM';
COMMENT ON COLUMN sales_data.product_code IS '商品编码';
COMMENT ON COLUMN sales_data.spec_model IS '规格型号';
COMMENT ON COLUMN sales_data.product_type IS '商品类型';
COMMENT ON COLUMN sales_data.unit IS '单位';
COMMENT ON COLUMN sales_data.sale_quantity IS '销售数量';
COMMENT ON COLUMN sales_data.sale_amount IS '销售金额';
COMMENT ON COLUMN sales_data.unit_price IS '商品单价';
COMMENT ON COLUMN sales_data.is_promotion IS '是否促销';
COMMENT ON COLUMN sales_data.created_at IS '创建时间';
