"""
Database connection and session management
Uses SQLAlchemy with PostgreSQL/Supabase
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session, declarative_base

# Load environment variables from .env
load_dotenv()

# ----------------------------------------------------------------------
# Database URL
# ----------------------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Ensure correct PostgreSQL dialect
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# ----------------------------------------------------------------------
# SQLAlchemy Engine
# ----------------------------------------------------------------------
engine = create_engine(
    DATABASE_URL,
    echo=os.getenv("SQL_ECHO", "false").lower() == "true",
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,   # Test connections before using
    pool_recycle=3600,    # Recycle connections every hour
)

# ----------------------------------------------------------------------
# Session factory
# ----------------------------------------------------------------------
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for models
Base = declarative_base()

# ----------------------------------------------------------------------
# FastAPI Dependency
# ----------------------------------------------------------------------
def get_db() -> Session:
    """
    FastAPI dependency to get DB session.
    Usage: def route(db: Session = Depends(get_db))
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ----------------------------------------------------------------------
# Optional Event Listeners (PostgreSQL-specific if needed)
# ----------------------------------------------------------------------
@event.listens_for(engine, "connect")
def on_connect(dbapi_connection, connection_record):
    """
    Run custom SQL when a connection is established.
    Example: set timezone, session variables, etc.
    """
    # For PostgreSQL, you could do:
    # cursor = dbapi_connection.cursor()
    # cursor.execute("SET TIME ZONE 'UTC';")
    # cursor.close()
    pass
