from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base
from app.db.schemas import ProductInDB


class Product(Base):
    __tablename__ = "product"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    artikul = Column(Integer, index=True)
    price = Column(Float)
    rating = Column(Float)
    count = Column(Integer)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<Product(name={self.name}, artikul={self.artikul}, price={self.price}, rating={self.rating}, count={self.count})>"


async def create_product(db: AsyncSession, product_db: ProductInDB):
    db_item = Product(
        name=product_db.name,
        artikul=product_db.artikul,
        price=product_db.price,
        rating=product_db.rating,
        count=product_db.count
    )
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item
