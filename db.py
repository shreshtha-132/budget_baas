from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base
from databases import Database

# 1) Database URL
DATABASE_URL = "sqlite:///./budget.db"

# 2) Async Database instance (to be injected into FastAPI)
database = Database(DATABASE_URL)


# 3) SQLAlchemy engine (for migrations / table creation)
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # required by SQLite + threads
)

SessionLocal = sessionmaker(bind=engine,autoflush=False,autocommit=False)
# ORM Base class
Base = declarative_base()

# metadata = MetaData()