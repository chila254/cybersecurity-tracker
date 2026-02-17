"""
Authentication API routes
Register, login, token refresh
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Organization
from app.schemas import UserCreate, LoginRequest, TokenResponse, UserResponse
from pydantic import BaseModel
from app.auth import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(tags=["Authentication"])

# ============================================================================
# Request/Response Schemas
# ============================================================================

class RegisterRequest(BaseModel):
    org_name: str
    name: str
    email: str
    password: str

# ============================================================================
# Register New Organization & Admin User
# ============================================================================

@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register(
    data: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new organization with admin user
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    
    try:
        # Create organization
        org = Organization(name=data.org_name)
        db.add(org)
        db.flush()  # ensures org.id is available

        # Create admin user
        user = User(
            org_id=org.id,               # UUID
            email=data.email,
            password_hash=hash_password(data.password),
            name=data.name,
            role="ADMIN"
        )
        db.add(user)
        db.commit()
        db.refresh(user)  # get auto-incremented id

        # Create access token
        access_token = create_access_token(
            data={
                "sub": str(user.id),     # integer id as string
                "org_id": str(org.id),
                "email": user.email,
                "role": user.role
            }
        )
        
        return {
            "message": "Organization and admin user created successfully",
            "organization_id": str(org.id),
            "user_id": user.id,  # keep integer
            "access_token": access_token,
            "token_type": "bearer"
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# ============================================================================
# Login
# ============================================================================

@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login with email and password
    """
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "org_id": str(user.org_id),
            "email": user.email,
            "role": user.role
        }
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=30 * 60  # 30 minutes
    )

# ============================================================================
# Get Current User Profile
# ============================================================================

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current authenticated user profile
    """
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user
