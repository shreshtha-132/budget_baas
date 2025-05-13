from db import engine, Base
import models

def main():
    print("🔍 Tables registered on Base.metadata:", list(Base.metadata.tables.keys()))
    Base.metadata.create_all(bind=engine)
    from sqlalchemy import inspect
    inspector = inspect(engine)
    print("Tables now in database:", inspector.get_table_names())
    print("✅ All tables created successfully.")

if __name__ == "__main__":
    main()