"""
Create a test user and generate a valid JWT token for testing
Run: python3 create_test_user.py
"""

import os
import sys
from uuid import uuid4
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import User, Organization, NotificationPreference
from app.auth import hash_password, create_access_token

def create_test_user():
    """Create a test user and organization"""
    db = SessionLocal()
    
    try:
        # Check if org already exists
        org = db.query(Organization).filter(
            Organization.name == "Test Organization"
        ).first()
        
        if not org:
            org = Organization(name="Test Organization")
            db.add(org)
            db.commit()
            db.refresh(org)
            print(f"✅ Created organization: {org.name} (ID: {org.id})")
        else:
            print(f"✅ Organization already exists: {org.name} (ID: {org.id})")
        
        # Check if test user already exists
        test_email = "test@cybersecurity-tracker.com"
        user = db.query(User).filter(User.email == test_email).first()
        
        if not user:
            user = User(
                name="Test User",
                email=test_email,
                password_hash=hash_password("TestPassword123!"),
                role="ADMIN",
                org_id=org.id,
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"✅ Created test user: {user.email} (ID: {user.id})")
            print(f"   Password: TestPassword123!")
        else:
            print(f"✅ Test user already exists: {user.email} (ID: {user.id})")
        
        # Create notification preferences
        existing_pref = db.query(NotificationPreference).filter(
            NotificationPreference.user_id == user.id
        ).first()
        
        if not existing_pref:
            pref = NotificationPreference(
                user_id=user.id,
                email_on_new_incident=True,
                email_on_incident_update=True,
                email_on_new_vulnerability=True
            )
            db.add(pref)
            db.commit()
            print("✅ Created notification preferences")
        
        # Generate JWT token
        token = create_access_token({
            "sub": str(user.id),
            "org_id": str(org.id),
            "role": user.role
        })
        
        print("\n" + "="*70)
        print("🔐 VALID JWT TOKEN (Use this for API requests)")
        print("="*70)
        print(f"\nToken:\n{token}\n")
        print("="*70)
        print("\n📌 Usage Example:")
        print("-"*70)
        print("curl -X GET http://localhost:8000/api/dashboard \\")
        print(f'  -H "Authorization: Bearer {token}"')
        print("\n" + "-"*70)
        print("\n📌 Login Credentials:")
        print("-"*70)
        print(f"Email: {test_email}")
        print(f"Password: TestPassword123!")
        print("\n" + "="*70)
        
        return token
    
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Creating test user and generating JWT token...\n")
    create_test_user()
