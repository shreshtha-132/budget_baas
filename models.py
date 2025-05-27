from sqlalchemy import Table, Column, Integer, String, Float, Date, ForeignKey, String
from sqlalchemy.orm import relationship
from db import Base
from sqlalchemy import UniqueConstraint,Index


# Define the "categories" table
class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer,primary_key=True,index=True)
    user_id = Column(String, index=True, nullable=False)
    name = Column(String, nullable=False)
    limit_amount = Column(Float, nullable=False)

    __table_args__ = (
        UniqueConstraint('user_id', 'name', name='uq_user_category_name'),
    )

    expenses = relationship(
        "Expense",
        back_populates="category",
        cascade="all, delete-orphan"
    )

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer,primary_key=True,index=True)
    user_id = Column(String, index=True, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable = False)
    amount = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    description = Column(String,nullable=True)

    __table_args__ = (
        Index("ix_expense_user_category", "user_id", "category_id"),
    )

    category = relationship("Category",back_populates="expenses")

class Income(Base):
    __tablename__="incomes"

    user_id = Column(String, index=True, nullable=False, primary_key=True)
    month = Column(String, primary_key=True)
    amount = Column(Float, nullable=False)
