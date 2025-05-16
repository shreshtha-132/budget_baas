import requests

BASE = "http://127.0.0.1:8000"

def test_flow():
    # 1. Create Categories
    r = requests.post(f"{BASE}/categories/", json={"name": "Groceries", "limit_amount": 10000})
    print("Create Category - Groceries:", r.json())

    r = requests.post(f"{BASE}/categories/", json={"name": "Transport", "limit_amount": 5000})
    print("Create Category - Transport:", r.json())

    # 2. Get All Categories
    r = requests.get(f"{BASE}/categories/")
    print("All Categories:", r.json())

    # 3. Update Category
    r = requests.put(f"{BASE}/categories/1", json={"limit_amount": 12000})
    print("Updated Category 1:", r.json())

    # 4. Get Category by ID
    r = requests.get(f"{BASE}/categories/1")
    print("Category 1 Details:", r.json())

    # 5. Add Expenses
    r = requests.post(f"{BASE}/expenses/", json={"category_id": 1, "amount": 1500, "date": "2025-05-15", "description": "Milk & Bread"})
    print("Add Expense 1:", r.json())

    r = requests.post(f"{BASE}/expenses/", json={"category_id": 2, "amount": 1000, "date": "2025-05-16", "description": "Metro card refill"})
    print("Add Expense 2:", r.json())

    # 6. Get Expense by ID
    r = requests.get(f"{BASE}/expenses/1")
    print("Expense 1:", r.json())

    # 7. Update Expense
    r = requests.put(f"{BASE}/expenses/1", json={"category_id": 1, "amount": 1800, "date": "2025-05-15", "description": "Updated groceries"})
    print("Updated Expense 1:", r.json())

    # 8. Delete Expense
    r = requests.delete(f"{BASE}/expenses/2")
    print("Deleted Expense 2:", r.status_code)

    # 9. Set Income
    r = requests.post(f"{BASE}/income/", json={"month": "2025-05", "amount": 30000})
    print("Set Income:", r.json())

    # 10. Get Income
    r = requests.get(f"{BASE}/income/2025-05")
    print("Get Income:", r.json())

    # 11. Get Summary
    r = requests.get(f"{BASE}/summary/2025-05")
    print("Monthly Summary:", r.json())

    # 12. Delete Category
    r = requests.delete(f"{BASE}/categories/2")
    print("Deleted Category 2:", r.status_code)

if __name__ == "__main__":
    test_flow()
