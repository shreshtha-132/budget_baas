from fastapi import FastAPI,Depends,HTTPException,status, Header   
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from db import database,SessionLocal,engine,Base  # ← import the `Database` instance
from contextlib import asynccontextmanager
import models, schemas
from typing import List, Optional
from sqlalchemy import func
import re
from datetime import date
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
import time
import firebase_admin
from firebase_admin import credentials, auth
from fastapi import APIRouter

#firebase setup

def get_current_user_id(authorization: str = Header(...))->str:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Auth Header")
    
    id_token = authorization.split(" ")[1]
    try:
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token["uid"]
        return uid
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")



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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#request‑logging middleware is a piece of code that sits in front of all routes and does two things
#for each incoming http request
#1) measures how long app takes to handle the request
#2) logs the http method,path,response status, and duration
# This is useful for spotting slow endpoints or just getting basic traffic metrics in console.

@app.middleware("http") # wraps every http request
async def log_requests(request:Request,call_next):
    start = time.time()
    response = await call_next(request)  # <-- this invokes this routes (next piece of flow)
    process_time = (time.time()-start)*1000
    print(f"{request.method}{request.url.path} - {response.status_code} - {process_time:.2f}ms")
    return response

#Catch any unhandled exceptions and return a clean JSON response:
@app.exception_handler(Exception)
async def global_exception_handler(request:Request,exc:Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error-please try again later"},
    )

@app.post("/v1/reset",tags=["Admin"],summary="Reset the entire database")
def reset_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    return JSONResponse(content={"detail":"Database has been reset (all tables dropped and recreated)."})

@app.post("/v1/categories/",tags=["Categories"],summary="Create a new spending category",response_model=schemas.CategoryRead,response_description="The newly created category object", status_code=status.HTTP_201_CREATED)
def create_category(cat: schemas.CategoryCreate, db: Session = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    #check uniqueness
    existing = db.query(models.Category).filter(models.Category.user_id==user_id,models.Category.name==cat.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category Already Exists")
    db_cat = models.Category(**cat.model_dump(), user_id=user_id)
    db.add(db_cat)
    db.commit()
    db.refresh(db_cat)
    return db_cat

@app.get("/v1/categories/",tags=["Categories"],summary="List all spending categories",response_model=List[schemas.CategoryRead])
def read_categories(skip: int =0,limit:int=100,db:Session=Depends(get_db),user_id: str = Depends(get_current_user_id)):
    return db.query(models.Category).filter(models.Category.user_id==user_id).offset(skip).limit(limit).all()

@app.get("/v1/categories/{category_id}",tags=["Categories"],summary="List specific category",response_model=schemas.CategoryRead)
def read_category(category_id:int,db:Session=Depends(get_db),user_id: str = Depends(get_current_user_id)):
    cat = db.query(models.Category).filter(models.Category.id==category_id,models.Category.user_id==user_id).first()
    if not cat:
        raise HTTPException(status_code=404,detail="Category not found")
    return cat

@app.put("/v1/categories/{category_id}",tags=["Categories"],summary="Update specific category",response_model=schemas.CategoryRead)
def update_category(category_id:int,updates:schemas.CategoryUpdate,db:Session=Depends(get_db),user_id: str = Depends(get_current_user_id)):
    cat = db.query(models.Category).filter(models.Category.id==category_id,models.Category.user_id==user_id).first()
    if not cat:
        raise HTTPException(status_code=404,detail="Category not found")
    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(cat,field,value)

    db.commit()
    db.refresh(cat)
    return cat

@app.delete("/v1/categories/{category_id}",tags=["Categories"],summary="Delete specific category",status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id:int,db:Session=Depends(get_db),user_id: str = Depends(get_current_user_id)):
    cat = db.query(models.Category).filter(models.Category.id==category_id,models.Category.user_id==user_id).first()
    if not cat:
        raise HTTPException(status_code=404,detail="Category not found")
    db.delete(cat)
    db.commit()
    return


@app.get("/",tags=["System"],summary="Home")
async def home():
    return JSONResponse(content={"message":"Hi you are welcome to budget maintenance API"})

@app.get("/v1/health",tags=["System"],summary="Health Check")
async def healthcheck():
    return JSONResponse(content={"status":"ok","message":"API is healthy"})

#here
@app.post("/v1/expenses/",tags=["Expenses"], summary="Add an expense",response_model=schemas.ExpenseRead, status_code=status.HTTP_201_CREATED)
def create_expense(exp: schemas.ExpenseCreate, db: Session = Depends(get_db),user_id: str = Depends(get_current_user_id)):
    #ensuring category exists
    category = db.query(models.Category).filter_by(id=exp.category_id, user_id=user_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    #create and commit
    db_exp = models.Expense(**exp.model_dump(), user_id=user_id)
    db.add(db_exp)
    db.commit()
    db.refresh(db_exp)
    return db_exp

@app.get("/v1/expenses/{expense_id}",tags=["Expenses"], summary="Get an specific expense",response_model=schemas.ExpenseRead)
def read_expense(expense_id: int, db:Session = Depends(get_db),user_id: str = Depends(get_current_user_id)):
    exp = db.query(models.Expense).filter_by(id=expense_id, user_id=user_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Expense not found")
    return exp

@app.get("/v1/expenses/",response_model=List[schemas.ExpenseRead],tags=["Expenses"],summary="List expenses, optionally filtered by month")
def read_expenses(month: Optional[str] = None, db: Session = Depends(get_db),user_id: str = Depends(get_current_user_id)):
    query = db.query(models.Expense).filter_by(user_id=user_id)
    if month:
        year, m = map(int, month.split("-"))
        from datetime import date
        start = date(year, m, 1)
        end = date(year + (m == 12), m % 12 + 1, 1)
        query = query.filter(models.Expense.date >= start, models.Expense.date < end)
    return query.all()

@app.put("/v1/expenses/{expense_id}",tags=["Expenses"], summary="Update specific expense", response_model=schemas.ExpenseRead)
def update_expense(expense_id:int, updates:schemas.ExpenseUpdate, db: Session = Depends(get_db),user_id: str = Depends(get_current_user_id)):
    exp = db.query(models.Expense).filter_by(id=expense_id, user_id=user_id).first()
    if not exp:
        raise HTTPException(status_code=404,detail="Expense not found")
    for k,v in updates.model_dump(exclude_unset=True).items():
        setattr(exp,k,v)
    db.commit()
    db.refresh(exp)
    return exp


@app.delete("/v1/expenses/{expense_id}", tags=["Expenses"], summary="Delete specific expense",status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(expense_id:int,db:Session=Depends(get_db),user_id: str = Depends(get_current_user_id)):
    exp = db.query(models.Expense).filter_by(id=expense_id, user_id=user_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Expense not found")
    db.delete(exp)
    db.commit()
    return

@app.post("/v1/income/", tags=["Income"], summary="Set or update monthly income",response_model=schemas.IncomeRead, status_code=status.HTTP_201_CREATED)
def set_income(data: schemas.IncomeCreate, db:Session = Depends(get_db),user_id: str = Depends(get_current_user_id)):
    inc = db.query(models.Income).filter_by(user_id=user_id, month=data.month).first()
    if inc:
        inc.amount = data.amount
    else:
        inc = models.Income(**data.model_dump(),user_id=user_id)
        db.add(inc)
    db.commit()
    return inc

@app.get("/v1/income/{month}",tags=["Income"], summary="Get specific monthly income",response_model=schemas.IncomeRead)
def get_income(month:str,db:Session=Depends(get_db),user_id: str = Depends(get_current_user_id)):
    inc = db.query(models.Income).filter_by(user_id=user_id, month=month).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Income not set for this month")
    return inc

@app.get("/v1/summary/{month}",tags=["Summary"],response_model=schemas.Overview, summary="Monthly Budget Overview")
def monthly_summary(month:str,db:Session=Depends(get_db),user_id: str = Depends(get_current_user_id)):
    
    if not re.match(r"^\d{4}-\d{2}$", month):
        raise HTTPException(status_code=400, detail="Month must be in YYYY-MM format")

    #get total income for month
    income = db.query(models.Income).filter_by(user_id=user_id, month=month).first()
    if not income:
        raise HTTPException(status_code=404,detail="Income not set for this month")
    
    #aggregate expenses

    results = (db.query(
        models.Category.id,
        models.Category.name,
        models.Category.limit_amount,
        func.coalesce(func.sum(models.Expense.amount), 0).label("spent")
    ).outerjoin(models.Expense).filter(models.Category.user_id == user_id).filter(func.strftime("%Y-%m", models.Expense.date) == month).group_by(models.Category.id).all())

    #build the summary response
    categories_summary = []
    total_spent = 0

    for category in results:
        balance = category.limit_amount - category.spent
        total_spent+=category.spent
        categories_summary.append({
            "category":category.name,
            "limit":category.limit_amount,
            "spent":category.spent,
            "balance":balance,
            "over_limit": category.spent > category.limit_amount
            })
        
    return {
        "month":month,
        "income":income.amount,
        "total_spent":total_spent,
        "remaining": income.amount - total_spent,
        "categories": categories_summary
    }


#when user doesnt specify month then return the summary for default month i.e current
@app.get("/v1/summary",tags=["Summary"],summary="Current month budget overview",
    response_model=schemas.Overview,
    response_description="Overview of the current month’s income, spending, and balances",)
def current_month_summary(db: Session = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    today = date.today()
    month = today.strftime("%Y-%m")
    return monthly_summary(month, db, user_id)
