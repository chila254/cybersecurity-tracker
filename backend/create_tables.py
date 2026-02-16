# create_tables.py

from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
import uuid
from sqlalchemy.dialects.postgresql import UUID

# ---- STEP 1: Load your database URL ----
DATABASE_URL = os.getenv(
    "POSTGRES_URL_NON_POOLING",
    "postgresql://postgres.dtjfhdcclrccqyvnkxdh:1HGoXYAkN710dOFH@aws-1-us-east-1.pooler.supabase.com:5432/postgres?sslmode=require"
)

# Fix old postgres:// URLs if they exist
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# ---- STEP 2: Create SQLAlchemy engine ----
engine = create_engine(DATABASE_URL, echo=True)

# ---- STEP 3: Define Base ----
Base = declarative_base()

# ---- STEP 4: Define your tables ----
class Organization(Base):
    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(UUID(as_uuid=True), nullable=True)
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
