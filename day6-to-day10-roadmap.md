## 📆 Day 6 – Firebase Authentication Integration 🔐

### 🎯 Goal:
Integrate Firebase Authentication (e.g. Google Sign-In) to secure your FastAPI backend.

### ✅ Steps:

1. **Firebase Setup**
   - Go to [firebase.google.com](https://firebase.google.com) → Create a new project.
   - Navigate to **Authentication > Sign-in Method** → Enable **Google** provider.
   - Go to **Project Settings > Service Accounts** → Generate new private key → download `serviceAccountKey.json`.

2. **Install Firebase Dependencies**
   ```bash
   pip install firebase-admin python-jose
   ```

3. **Create `firebase_auth.py`**
   - Initialize Firebase using the downloaded JSON.
   - Write a `verify_token(id_token)` function to validate user tokens.

4. **Protect Routes**
   - Use FastAPI’s `Depends` to wrap `verify_token()` in protected endpoints.
   - Example usage:
     ```python
     from fastapi import Depends

     @app.get("/v1/categories/")
     async def get_categories(user=Depends(verify_token)):
         return ...
     ```

5. **Testing**
   - Use Postman or frontend to send a valid Firebase ID token in header:
     ```http
     Authorization: Bearer <your_firebase_id_token>
     ```

---

## 🌍 Day 7 – Production Deployment (Railway/Render) 🚀

### 🎯 Goal:
Deploy Dockerized FastAPI app to a live server using Railway or Render.

### ✅ Steps:

1. **Push to GitHub** if not already done.

2. **Deploy on Railway**
   - Go to [railway.app](https://railway.app) → Start New Project → GitHub Repo.
   - Set environment variables:
     - `DATABASE_URL`
     - `FIREBASE_PROJECT_ID`
     - Any other custom configs

3. **Set Build & Start Commands**
   - Build:  
     ```bash
     pip install -r requirements.txt
     ```
   - Start:
     ```bash
     uvicorn main:app --host 0.0.0.0 --port 8000
     ```

4. **Test Production Deployment**
   - Visit `https://your-app-name.up.railway.app/v1/health`.

5. **Secure with Firebase Auth**
   - Test `/v1/expenses`, `/v1/income`, etc. using token-based headers.

---

## 🐘 Day 8 – Migrate from SQLite to PostgreSQL 🧩

### 🎯 Goal:
Upgrade from SQLite to PostgreSQL for better performance and scaling.

### ✅ Steps:

1. **Provision PostgreSQL**
   - Use Railway, Render, Supabase, or Docker.
   - Get the connection URL:
     ```text
     postgresql+asyncpg://<user>:<pass>@<host>:<port>/<db>
     ```

2. **Install Packages**
   ```bash
   pip install asyncpg psycopg2-binary
   ```

3. **Update `database.py`**
   - Replace SQLite URL with PostgreSQL.
   - Test DB connection on app startup.

4. **Initialize Tables**
   - Use `Base.metadata.create_all()` for auto-schema.
   - Or integrate Alembic for versioned migrations later.

5. **Optional: Data Migration**
   - Write a script to transfer old data from SQLite to PostgreSQL using SQLAlchemy.

6. **Docker Compose (Optional)**
   ```yaml
   services:
     db:
       image: postgres:15
       ports:
         - "5432:5432"
       environment:
         POSTGRES_USER: user
         POSTGRES_PASSWORD: pass
         POSTGRES_DB: budget
   ```

---

## 💬 Day 9 – Add Feedback System from Testers 💡

### 🎯 Goal:
Allow users/testers to submit feedback from the frontend or Postman.

### ✅ Steps:

1. **Create Feedback Model**
   ```python
   class Feedback(Base):
       id = Column(Integer, primary_key=True)
       user_email = Column(String)
       suggestion = Column(Text)
       created_at = Column(DateTime, default=datetime.utcnow)
   ```

2. **Endpoints**
   - `POST /v1/feedback/` – Accept suggestion from user.
   - `GET /v1/feedback/summary` – Admin view for all suggestions.

3. **Auth + Validation**
   - Extract email from Firebase token.
   - Add admin check based on allowed email list.

4. **Optional**
   - Add length check (min chars).
   - Log timestamps and request source IPs.

---

## 🔀 Day 10 – Prepare Parallel Development for v2 💻

### 🎯 Goal:
Start working on a new version (v2) while users continue testing v1.

### ✅ Steps:

1. **Create v2 Branch**
   ```bash
   git checkout -b v2-dev
   ```

2. **Create V2 Directory Structure**
   ```text
   v2/
     ├── main.py
     ├── models/
     ├── routes/
     ├── schemas/
     ├── db/
     └── utils/
   ```

3. **Set Up v2 Roadmap**
   Create a file `v2-roadmap.md` with:
   ```markdown
   ## V2 Feature Roadmap

   - [ ] Multi-user budgeting with Firebase UID
   - [ ] Category coloring & custom icons
   - [ ] Expense recurrence (monthly/weekly)
   - [ ] Budget carry-forward to next month
   - [ ] Email summaries (SendGrid)
   - [ ] PostgreSQL performance tuning
   - [ ] Admin roles and analytics
   ```

4. **Start Development**
   - Reuse models and schemas.
   - Improve DB schema with foreign keys, constraints, enums.

5. **Deploy Preview Build (Optional)**
   - Use Railway preview deployment for `v2-dev` branch.