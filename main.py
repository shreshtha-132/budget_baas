from fastapi import FastAPI,Depends,HTTPException,status
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from db import database,SessionLocal,engine,Base  # ← import the `Database` instance
from contextlib import asynccontextmanager
import models, schemas
from typing import List




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

