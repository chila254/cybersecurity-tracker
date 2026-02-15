"""
Authentication and security utilities
Includes register, login, JWT token handling, and route protection
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID
import os

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr

from passlib.context import CryptContext
from jose import jwt, JWTError

# For database
from app.models import User, Organization
from app.database import SessionLocal
from sqlalchemy.orm import Session

from dotenv import load_dotenv
load_dotenv()

# ===========================================================
# Config
# ===========================================================

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()
router = APIRouter()

# ===========================================================
# Schemas
# ===========================================================

class RegisterSchema(BaseModel):
    name: str
    email: EmailStr
    password: str
    org_name: str

class LoginSchema(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

# ===========================================================
# Database Dependency
# ===========================================================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ===========================================================
# Utilities
# ===========================================================

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# ===========================================================
# Route Protection Dependencies
# ===========================================================

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    token = credentials.credentials
    payload = verify_token(token)

    user_id: str = payload.get("sub")
    org_id: str = payload.get("org_id")
    role: str = payload.get("role")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {
        "user_id": UUID(user_id),
        "org_id": UUID(org_id),
        "role": role
    }

def require_role(required_role: str):
    async def check_role(current_user: dict = Depends(get_current_user)) -> dict:
        if current_user["role"] != required_role and current_user["role"] != "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return check_role

# ===========================================================
# Authentication Routes
# ===========================================================

@router.post("/register", response_model=TokenResponse)
def register_user(user: RegisterSchema, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    org = Organization(name=user.org_name)
    db.add(org)
    db.commit()
    db.refresh(org)

    new_user = User(
        name=user.name,
        email=user.email,
        password_hash=hash_password(user.password),
        role="ADMIN",
        org_id=org.id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token({"sub": str(new_user.id), "org_id": str(org.id), "role": new_user.role})
    return {"access_token": token, "token_type": "bearer"}


@router.post("/login", response_model=TokenResponse)
def login_user(credentials: LoginSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    token = create_access_token({"sub": str(user.id), "org_id": str(user.org_id), "role": user.role})
    return {"access_token": token, "token_type": "bearer"}
