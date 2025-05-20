from pydantic import BaseModel, Field
from typing import Optional, List
import datetime

class CategoryBase(BaseModel):
    name:str = Field(...,example="Fruits")
    limit_amount:float = Field(...,ge=0,example=500)
    #ge : greater than or equals to

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    #update schema where fields can be empty.
    # for ex name can be string or empty
    name: Optional[str] = Field(None, example="Groceries")
    limit_amount: Optional[float] = Field(None, ge=0, example=750)


class CategoryRead(CategoryBase):
    id:int

    class Config:
        #tells Pydantic it can read SQLAlchemy objects directly.
        from_attributes = True

class CategorySummary(BaseModel):
    category: str
    limit: float
    spent: float
    balance: float
    over_limit: bool

    class Config:
        from_attributes = True

class Overview(BaseModel):
    month: str
    income:float
    total_spent: float
    remaining: float
    categories: List[CategorySummary]

    class Config:
        from_attributes = True
        

# —— Expense Schemas ——

class ExpenseBase(BaseModel):
    category_id: int = Field(...,example=1)
    amount:float=Field(...,ge=0,example=250.75)
    date:datetime.date=Field(..., example="2025-05-14")
    description:Optional[str]=Field(None,example="Lunch at canteen")

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseRead(ExpenseBase):
    id:int

    class Config:
        from_attributes = True

class ExpenseUpdate(BaseModel):
    category_id: Optional[int] = Field(None, example=1)
    amount: Optional[float]    = Field(None, ge=0, example=250.75)
    date: Optional[datetime.date] = Field(None, example="2025-05-14")
    description: Optional[str] = Field(None, example="Lunch at canteen")
    
    class Config:
        from_attributes = True


#income schemas
class IncomeBase(BaseModel):
    month: str = Field(...,example="2025-05")
    amount: float = Field(...,ge=0,example=40800)

class IncomeCreate(IncomeBase):
    pass

class IncomeRead(IncomeBase):
    class Config:
        from_attributes=True
