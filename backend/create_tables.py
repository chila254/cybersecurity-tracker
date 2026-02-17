# create_tables.py
"""
Database table creation script that uses the models from app/models.py
This ensures the database schema matches the ORM models
"""

import os
import sys
from sqlalchemy import create_engine

# Add parent directory to path to import app module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.models import Base  # Import the Base from models which has all table definitions
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ---- STEP 1: Load your database URL ----
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Ensure correct PostgreSQL dialect
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# ---- STEP 2: Create SQLAlchemy engine ----
engine = create_engine(DATABASE_URL, echo=True)

# ---- STEP 3: Create all tables from models ----
def create_tables():
    """Create all tables defined in app/models.py"""
    Base.metadata.create_all(bind=engine)
    print("✅ All tables created successfully!")
    print("✅ Database tables created successfully")

if __name__ == "__main__":
    create_tables()
