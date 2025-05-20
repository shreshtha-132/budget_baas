import os, sys
from fastapi.testclient import TestClient
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))

# 1) Point to an ephemeral SQLite file
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

# 2) Import & recreate schema directly
from db import engine, Base
import models  # registers Category, Expense, Income on Base
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

from main import app  # now that env and schema are set

client = TestClient(app)

def test_category_expense_income_summary():
    # 1) Create category
    r = client.post("/categories/", json={"name": "TestCat", "limit_amount": 100})
    assert r.status_code == 201
    cat_id = r.json()["id"]

    # 2) Expense that exceeds limit
    r = client.post("/expenses/", json={
        "category_id": cat_id,
        "amount": 150,
        "date": "2025-05-10",
        "description": "Overspend test"
    })
    assert r.status_code == 201

    # 3) Set income
    r = client.post("/income/", json={"month": "2025-05", "amount": 500})
    assert r.status_code == 201

    # 4) Fetch summary
    r = client.get("/summary/2025-05")
    assert r.status_code == 200
    data = r.json()

    # Overall checks
    assert data["month"] == "2025-05"
    assert data["income"] == 500
    assert data["total_spent"] == 150
    assert data["remaining"] == 350

    # Category summary
    cs = data["categories"][0]
    assert cs["category"] == "TestCat"
    assert cs["limit"] == 100
    assert cs["spent"] == 150
    assert cs["balance"] == -50
    assert cs["over_limit"] is True


def test_category_crud_and_404():
    #create
    r = client.post("/categories/",json={"name":"CatA","limit_amount":500})
    assert r.status_code == 201
    cat = r.json()
    cat_id = cat["id"]
    assert cat["name"]=="CatA"

    #duplicate ->400
    r = client.post("/categories/",json={"name":"CatA","limit_amount":500})
    assert r.status_code == 400

    #list
    r = client.get("/categories/")
    assert r.status_code == 200 and any(c["id"]== cat_id for c in r.json())

    #get by id
    r = client.get(f"/categories/{cat_id}")
    assert r.status_code==200 and r.json()["id"]==cat_id

    #404 on non existing
    r = client.get("/categories/9999")
    assert r.status_code == 404

    #update
    r = client.put(f"/categories/{cat_id}",json={"limit_amount":750})
    assert r.status_code == 200 and r.json()["limit_amount"]==750

    #delete
    r = client.delete(f"/categories/{cat_id}")
    assert r.status_code == 204

    #now gone
    r = client.get(f"/categories/{cat_id}")
    assert r.status_code == 404

def test_expense_crud_and_filter_404():
    #setup a category
    r = client.post("/categories/",json={"name":"CatB","limit_amount":100})
    cid = r.json()["id"]

    #create
    exp = {"category_id":cid,"amount":20,"date":"2025-06-01","description":"T"}
    r = client.post("/expenses/",json=exp)
    assert r.status_code==201
    exp_id = r.json()["id"]

    #404 for bad category
    r = client.post("/expenses/", json={**exp, "category_id":9999})
    assert r.status_code==404

    #read by id
    r = client.get(f"/expenses/{exp_id}")
    assert r.status_code == 200

    #404 for missing
    r = client.get("/expenses/9999")
    assert r.status_code == 404

    #update
    r = client.put(f"/expenses/{exp_id}", json={"amount":30})
    assert r.status_code == 200 and r.json()["amount"]==30

    #filter by month
    r=client.get("/expenses/",params={"month":"2025-06"})
    assert r.status_code==200 and any(e["id"]==exp_id for e in r.json())

    #delete
    r = client.delete(f"/expenses/{exp_id}")
    assert r.status_code == 204

    #gone
    r = client.get(f"/expenses/{exp_id}")
    assert r.status_code==404

def test_income_crud_and_404():
    #create
    r = client.post("/income/",json={"month":"2025-07","amount":2000})
    assert r.status_code == 201 and r.json()["amount"] == 2000

    #update
    r = client.post("/income/",json={"month":"2025-07","amount":2500})
    assert r.status_code == 201 and r.json()["amount"] == 2500

    #read
    r = client.get("/income/2025-07")
    assert r.status_code == 200

    #404
    r = client.get("/income/1999-01")
    assert r.status_code == 404

def test_summary_and_current_month_default():
    
    r = client.post("/categories/",json={"name":"CatC", "limit_amount":200})
    cid = r.json()["id"]
    client.post("/expenses/",json={
        "category_id":cid,
        "amount":60,
        "date":"2025-05-10"
    })
    client.post("/income/", json={"month":"2025-05","amount":800})

    #summary for may
    r = client.get("/summary/2025-05")
    assert r.status_code == 200
    data = r.json()
    assert any(c["category"] == "CatC" for c in data["categories"])

    #default summary (no month param)
    r = client.get("/summary")
    assert r.status_code == 200

def test_reset_endpoint_clears_data():
    #create some data

    r = client.post("/categories/", json={"name":"CatX","limit_amount":10})
    cid = r.json()["id"]
    client.post("/expenses/",json={
        "category_id":cid,
        "amount":5,
        "date":"2025-05-01"
    })
    client.post("/income/",json={"month":"2025-05","amount":100})

    #reset
    r = client.post("/reset")
    assert r.status_code == 200

    #all gone

    assert client.get("/categories/").json() == []
    assert client.get("/expenses/").json() == []
    assert client.get("/income/2025-05").status_code == 404