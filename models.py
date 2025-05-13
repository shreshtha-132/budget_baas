from sqlalchemy import Table, Column, Integer, String, Float
from db import Base


# Define the "categories" table
class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer,primary_key=True,index=True)
    name = Column(String, unique=True, nullable=False)
    limit_amount = Column(Float, nullable=False)