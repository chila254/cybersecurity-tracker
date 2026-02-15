"""
Authentication and security routes
Includes register, login, and JWT token handling
"""

from datetime import timedelta, timezone, datetime
from typing import Optional
from uuid import UUID, uuid4
import os

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr

from app.models import User, Organization
from app.database import SessionLocal
from sqlalchemy.orm import Session

from passlib.context import CryptContext
from jose import jwt, JWTError

# Load environment variables
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
# Pydantic Schemas
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
# Utility Functions
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

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ===========================================================
# Routes
# ===========================================================

@router.post("/register", response_model=TokenResponse)
def register_user(user: RegisterSchema, db: Session = Depends(get_db)):
    # Check if email exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create organization
    org = Organization(name=user.org_name)
    db.add(org)
    db.commit()
    db.refresh(org)

    # Create user
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

    # Create JWT token
    token = create_access_token({"sub": str(new_user.id), "org_id": str(org.id), "role": new_user.role})
    return {"access_token": token, "token_type": "bearer"}


@router.post("/login", response_model=TokenResponse)
def login_user(credentials: LoginSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    token = create_access_token({"sub": str(user.id), "org_id": str(user.org_id), "role": user.role})
    return {"access_token": token, "token_type": "bearer"}


# Optional protected route example
@router.get("/me")
def get_me(current_user: dict = Depends(security)):
    token = current_user.credentials
    payload = verify_token(token)
    return {"user_id": payload.get("sub"), "org_id": payload.get("org_id"), "role": payload.get("role")}
