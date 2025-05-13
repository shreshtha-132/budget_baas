Here’s a focused 5-day, \~2 hours/day roadmap to build your Budget Maintenance backend. Each day you’ll spend \~30 min on a targeted crash-course video segment and \~90 min coding your project. Under each feature, you’ll see the **tech/skill** you’ll learn or use.

---

## Day 1 – Project Kick-off & Core Setup

**Crash-Course (30 min):**
• FastAPI basics: project layout, `uvicorn`, routing.
• Python virtual environments & `pip` package management.

**Project Work (90 min):**

1. **Repo Init & Env**

   * Create `venv`, install `fastapi`, `uvicorn`, `sqlalchemy`, `pydantic`, `databases` (async DB support).
   * Set up GitHub repo with `.gitignore`.
   * **Tech:** Python, FastAPI, Git.

2. **App Skeleton**

   * `main.py` with FastAPI instance.
   * Health-check endpoint (`GET /health`).
   * Test via browser/`curl`.
   * **Tech:** FastAPI routing.

3. **Database Config**

   * Choose **SQLite** for month-1 prototyping.
   * Create `database.py` with SQLAlchemy + `databases` URL (`sqlite:///./budget.db`).
   * Initialize connection on app startup/shutdown.
   * **Tech:** SQLAlchemy core, async DB.

---

## Day 2 – Category Management (Add/Edit/Delete)

**Crash-Course (30 min):**
• Pydantic models for request/response schemas.
• SQLAlchemy declarative ORM: defining tables.

**Project Work (90 min):**

1. **Define Models**

   * **ORM Model**: `Category(id, name, limit_amount)`.
   * **Pydantic Schemas**:

     * `CategoryCreate(name: str, limit: float)`
     * `CategoryRead(id: int, name: str, limit: float)`
     * `CategoryUpdate(name: str | None, limit: float | None)`
   * **Tech:** Pydantic, SQLAlchemy ORM.

2. **CRUD Endpoints**

   * `POST /categories/` → create a new category.
   * `GET /categories/` → list all.
   * `PUT /categories/{id}` → update name/limit.
   * `DELETE /categories/{id}` → delete.
   * **Tech:** FastAPI dependency injection (DB session), HTTP status codes.

---

## Day 3 – Expense Tracking & Monthly Income

**Crash-Course (30 min):**
• FastAPI request bodies & validation.
• Aggregations with SQLAlchemy (SUM, GROUP BY).

**Project Work (90 min):**

1. **Expense Model & Schemas**

   * **ORM Model**: `Expense(id, category_id → Category, amount, date, description)`.
   * **Schemas**: `ExpenseCreate`, `ExpenseRead`.
   * **Tech:** SQLAlchemy relationships, Pydantic.

2. **Endpoints for Expenses**

   * `POST /expenses/` → add expense to a category.
   * `GET /expenses/?month=YYYY-MM` → list all in that month.
   * **Tech:** Query params, date parsing.

3. **Total Income Endpoint**

   * `POST /income/` → set total monthly income (store in a singleton table or config).
   * `GET /income/{month}` → retrieve.
   * **Tech:** Simple table + CRUD.

4. **Aggregate Usage**

   * `GET /summary/{month}` → return for each category: allotted, used (sum of expenses), balance; plus total income vs total spent.
   * Use SQLAlchemy query with `func.sum()`.
   * **Tech:** SQLAlchemy aggregation.

---

## Day 4 – Validation, Middleware & Error Handling

**Crash-Course (30 min):**
• FastAPI exception handling & `HTTPException`.
• Adding Middleware (e.g. CORS, logging).

**Project Work (90 min):**

1. **Input Validation**

   * Ensure limits/amounts ≥ 0, dates valid, category exists.
   * Use Pydantic field validators.
   * **Tech:** Pydantic validation.

2. **Error Handling**

   * Raise `404` if category/expense not found.
   * Global handler for `500` errors with custom JSON.
   * **Tech:** FastAPI exception handlers.

3. **Middleware**

   * Add CORS (so future front-end can call).
   * Optional request-logging middleware (timing).
   * **Tech:** FastAPI Middleware.

---

## Day 5 – Testing, Docs & Deployment

**Crash-Course (30 min):**
• Writing tests with `pytest` & FastAPI’s `TestClient`.
• Auto-docs customization (Swagger UI).

**Project Work (90 min):**

1. **Automated Tests**

   * Test category CRUD, expense creation, summary.
   * Mock in-memory DB or use a temporary SQLite file.
   * **Tech:** pytest, FastAPI TestClient.

2. **Documentation**

   * Visit `/docs` and `/redoc`.
   * Add `tags`, `summary`, `description` to each route.
   * **Tech:** FastAPI OpenAPI metadata.

3. **Containerization & Deploy**

   * Write a `Dockerfile` (base: `python:3.11-slim`, copy code, `pip install`, `CMD uvicorn main:app`).
   * Build & test locally.
   * Push image to Docker Hub / deploy to Railway or Heroku.
   * **Tech:** Docker, basic CI/CD.

---

### Tech/Skill Stack by Feature

| Feature                     | Tech/Skills                                  |
| --------------------------- | -------------------------------------------- |
| Project setup & routing     | Python, FastAPI, Uvicorn, Git                |
| Category CRUD               | Pydantic models, SQLAlchemy ORM, FastAPI DI  |
| Expense logging & querying  | SQLAlchemy relationships, date handling      |
| Monthly income tracking     | Simple table design, CRUD                    |
| Summary & aggregation       | SQLAlchemy `func.sum()`, GROUP BY            |
| Validation & error handling | Pydantic validators, FastAPI `HTTPException` |
| Middleware (CORS/logging)   | FastAPI Middleware                           |
| Testing endpoints           | pytest, FastAPI TestClient                   |
| Documentation               | FastAPI OpenAPI, Swagger UI, Redoc           |
| Deployment                  | Docker, basic PaaS (Heroku/Railway)          |

By the end of Day 5 you’ll have a fully-functional, tested, documented, and deployed Budget Maintenance API—ready for a front-end or mobile client to hook into!
