# create_tables.py

from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os
import uuid
from datetime import datetime

# ---- STEP 1: Load your database URL ----
DATABASE_URL = os.getenv(
    "POSTGRES_URL_NON_POOLING",
    "postgresql://postgres.dtjfhdcclrccqyvnkxdh:1HGoXYAkN710dOFH@aws-1-us-east-1.pooler.supabase.com:5432/postgres?sslmode=require"
)

# ---- STEP 2: Create SQLAlchemy engine ----
engine = create_engine(DATABASE_URL, echo=True)

# ---- STEP 3: Create Session ----
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ---- STEP 4: Define Base ----
Base = declarative_base()

# ---- STEP 5: Define your tables ----
class Organization(Base):
    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    users = relationship("User", back_populates="organization")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    name = Column(String, nullable=True)
    role = Column(String, nullable=True, default="user")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    organization = relationship("Organization", back_populates="users")

# ---- STEP 6: Create tables in the database ----
def create_tables():
    Base.metadata.create_all(bind=engine)
    print("✅ All tables created successfully!")

if __name__ == "__main__":
    create_tables()
