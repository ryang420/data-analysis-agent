from sqlalchemy import DateTime, Double, Integer, PrimaryKeyConstraint, String, text
import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """ORM declarative base."""


class SalesData(Base):
    __tablename__ = 'sales_data'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='sales_data_pkey'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    customer_id: Mapped[int] = mapped_column(Integer, nullable=False, comment='顾客编号')
    big_category_code: Mapped[int] = mapped_column(Integer, nullable=False, comment='大类编码')
    big_category_name: Mapped[str] = mapped_column(String(100), nullable=False, comment='大类名称')
    mid_category_code: Mapped[int] = mapped_column(Integer, nullable=False, comment='中类编码')
    mid_category_name: Mapped[str] = mapped_column(String(100), nullable=False, comment='中类名称')
    small_category_code: Mapped[int] = mapped_column(Integer, nullable=False, comment='小类编码')
    small_category_name: Mapped[str] = mapped_column(String(100), nullable=False, comment='小类名称')
    sale_date: Mapped[str] = mapped_column(String(20), nullable=False, comment='销售日期')
    sale_month: Mapped[str] = mapped_column(String(20), nullable=False, comment='销售月份')
    product_code: Mapped[str] = mapped_column(String(100), nullable=False, comment='商品编码')
    spec_model: Mapped[str] = mapped_column(String(200), nullable=False, comment='规格型号')
    product_type: Mapped[str] = mapped_column(String(50), nullable=False, comment='商品类型')
    unit: Mapped[str] = mapped_column(String(20), nullable=False, comment='单位')
    sale_quantity: Mapped[float] = mapped_column(Double(53), nullable=False, comment='销售数量')
    sale_amount: Mapped[float] = mapped_column(Double(53), nullable=False, comment='销售金额')
    unit_price: Mapped[float] = mapped_column(Double(53), nullable=False, comment='商品单价')
    is_promotion: Mapped[str] = mapped_column(String(10), nullable=False, comment='是否促销')
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'), comment='创建时间')
