# create_tables.py

from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime

# ---- STEP 1: Load your database URL ----
# You can also set this in your environment variables
DATABASE_URL = os.getenv(
    "POSTGRES_URL_NON_POOLING",
    "postgres://postgres.dtjfhdcclrccqyvnkxdh:1HGoXYAkN710dOFH@aws-1-us-east-1.pooler.supabase.com:5432/postgres?sslmode=require"
)

# ---- STEP 2: Create SQLAlchemy engine ----
engine = create_engine(DATABASE_URL, echo=True)

# ---- STEP 3: Define Base ----
Base = declarative_base()

# ---- STEP 4: Define your tables ----
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, nullable=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    name = Column(String, nullable=True)
    role = Column(String, nullable=True, default="user")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# ---- STEP 5: Create tables in the database ----
def create_tables():
    Base.metadata.create_all(bind=engine)
    print("✅ All tables created successfully!")

if __name__ == "__main__":
    create_tables()
