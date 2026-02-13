"""
Authentication API routes
Register, login, token refresh
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Organization
from app.schemas import UserCreate, LoginRequest, TokenResponse, UserResponse
from app.auth import hash_password, verify_password, create_access_token
from datetime import timedelta
from uuid import uuid4

router = APIRouter(prefix="/auth", tags=["Authentication"])

# ============================================================================
# Register New Organization & Admin User
# ============================================================================

@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register(
    org_name: str,
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new organization with admin user
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    
    try:
        # Create organization
        org = Organization(name=org_name)
        db.add(org)
        db.flush()
        
        # Create admin user
        user = User(
            org_id=org.id,
            email=user_data.email,
            password_hash=hash_password(user_data.password),
            name=user_data.name,
            role="ADMIN"
        )
        db.add(user)
        db.commit()
        
        # Create access token
        access_token = create_access_token(
            data={
                "sub": str(user.id),
                "org_id": str(org.id),
                "email": user.email,
                "role": user.role
            }
        )
        
        return {
            "message": "Organization and admin user created successfully",
            "organization_id": str(org.id),
            "user_id": str(user.id),
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
    current_user: dict = Depends(lambda: None),
    db: Session = Depends(get_db)
):
    """
    Get current authenticated user profile
    Note: Proper dependency injection to be added
    """
    from app.auth import get_current_user
    current_user = await get_current_user(None)
    
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user
