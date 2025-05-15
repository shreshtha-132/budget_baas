from fastapi import FastAPI,Depends,HTTPException,status
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from db import database,SessionLocal,engine,Base  # ← import the `Database` instance
from contextlib import asynccontextmanager
import models, schemas
from typing import List, Optional
from sqlalchemy import func




@asynccontextmanager
async def lifespan(app:FastAPI):
    # Connect to the DB on startup
    await database.connect()
    yield
    # Disconnect on shutdown
    await database.disconnect()

Base.metadata.create_all(bind=engine)

#dependency

def get_db():
    #Instantiates a new DB session
    db = SessionLocal()
    try:
        #Gives this session to your route handler.
        yield db
    finally:
        #The finally block ensures db.close() runs, releasing the connection.
        db.close()
    
app = FastAPI(title="Budget Maintenance BaaS",lifespan=lifespan)

@app.post("/categories/",response_model=schemas.CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(cat: schemas.CategoryCreate, db: Session = Depends(get_db)):
    #check uniqueness
    existing = db.query(models.Category).filter(models.Category.name==cat.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category Already Exists")
    db_cat = models.Category(**cat.model_dump())
    db.add(db_cat)
    db.commit()
    db.refresh(db_cat)
    return db_cat

@app.get("/categories/",response_model=List[schemas.CategoryRead])
def read_categories(skip: int =0,limit:int=100,db:Session=Depends(get_db)):
    return db.query(models.Category).offset(skip).limit(limit).all()

@app.get("/categories/{category_id}",response_model=schemas.CategoryRead)
def read_category(category_id:int,db:Session=Depends(get_db)):
    cat = db.query(models.Category).get(category_id)
    if not cat:
        raise HTTPException(status_code=404,detail="Category not found")
    return cat

@app.put("/categories/{category_id}",response_model=schemas.CategoryRead)
def update_category(category_id:int,updates:schemas.CategoryUpdate,db:Session=Depends(get_db)):
    cat = db.query(models.Category).get(category_id)
    if not cat:
        raise HTTPException(status_code=404,detail="Category not found")
    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(cat,field,value)

    db.commit()
    db.refresh(cat)
    return cat

@app.delete("/categories/{category_id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id:int,db:Session=Depends(get_db)):
    cat = db.query(models.Category).get(category_id)
    if not cat:
        raise HTTPException(status_code=404,detail="Category not found")
    db.delete(cat)
    db.commit()
    return


@app.get("/",summary="Home")
async def home():
    return JSONResponse(content={"message":"Hi you are welcome to budget maintenance API"})

@app.get("/health",summary="Health Check")
async def healthcheck():
    return JSONResponse(content={"status":"ok","message":"API is healthy"})

@app.post("/expenses/",response_model=schemas.ExpenseRead, status_code=status.HTTP_201_CREATED)
def create_expense(exp: schemas.ExpenseCreate, db: Session = Depends(get_db)):
    #ensuring category exists
    if not db.get(models.Category, exp.category_id):
        raise HTTPException(status_code=404, detail="Category not found")
    #create and commit
    db_exp = models.Expense(**exp.model_dump())
    db.add(db_exp)
    db.commit()
    db.refresh(db_exp)
    return db_exp

@app.get("/expenses/{expense_id}",response_model=schemas.ExpenseRead)
def read_expense(expense_id: int, db:Session = Depends(get_db)):
    exp = db.get(models.Expense, expense_id)
    if not exp:
        raise HTTPException(status_code=404, detail="Expense not found")
    return exp

@app.put("/expenses/{expense_id}", response_model=schemas.ExpenseRead)
def update_expense(expense_id:int, updates:schemas.ExpenseCreate, db: Session = Depends(get_db)):
    exp = db.get(models.Expense, expense_id)
    if not exp:
        raise HTTPException(status_code=404,detail="Expense not found")
    for k,v in updates.model_dump(exclude_unset=True).items():
        setattr(exp,k,v)
    db.commit()
    db.refresh(exp)
    return exp


@app.delete("/expenses/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(expense_id:int,db:Session=Depends(get_db)):
    exp = db.get(models.Expense, expense_id)
    if not exp:
        raise HTTPException(status_code=404, detail="Expense not found")
    db.delete(exp)
    db.commit()
    return

@app.post("/income/", response_model=schemas.IncomeRead, status_code=status.HTTP_201_CREATED)
def set_income(data: schemas.IncomeCreate, db:Session = Depends(get_db)):
    inc = db.get(models.Income,data.month)
    if inc:
        inc.amount = data.amount
    else:
        inc = models.Income(**data.model_dump())
        db.add(inc)
    db.commit()
    return inc

@app.get("/income/{month}",response_model=schemas.IncomeRead)
def get_income(month:str,db:Session=Depends(get_db)):
    inc = db.get(models.Income,month)
    if not inc:
        raise HTTPException(status_code=404, detail="Income not set for this month")
    return inc
