from sqlalchemy import Table, Column, Integer, String, Float, Date, ForeignKey, String
from sqlalchemy.orm import relationship
from db import Base


# Define the "categories" table
class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer,primary_key=True,index=True)
    name = Column(String, unique=True, nullable=False)
    limit_amount = Column(Float, nullable=False)

    expenses = relationship(
        "Expense",
        back_populates="category",
        cascade="all, delete-orphan"
    )

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer,primary_key=True,index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable = False)
    amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    description = Column(String,nullable=True)

    category = relationship("Category",back_populates="expenses")
