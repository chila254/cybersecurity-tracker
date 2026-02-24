"""
Generate a valid JWT token for testing without database dependency
Run: python3 generate_token.py
"""

import os
from datetime import datetime, timedelta, timezone
from uuid import uuid4
import json

try:
    from jose import jwt
except ImportError:
    print("Installing required package: python-jose...")
    os.system("pip3 install python-jose --break-system-packages -q")
    from jose import jwt

# Token configuration
SECRET_KEY = "your-secret-key-change-this-in-production-cybersecurity-tracker-2026"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 hours

def generate_test_token():
    """Generate a valid JWT token for testing"""
    
    # Create unique IDs for user and organization
    user_id = str(uuid4())
    org_id = str(uuid4())
    
    # Token payload
    payload = {
        "sub": user_id,           # user_id
        "org_id": org_id,         # organization_id
        "role": "ADMIN",          # role
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    
    # Encode token
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    print("\n" + "="*80)
    print("🔐 VALID JWT TOKEN FOR TESTING")
    print("="*80)
    print(f"\n✅ Token successfully generated!\n")
    print(f"Token:\n{token}\n")
    print("="*80)
    print("\n📌 Token Details:")
    print("-"*80)
    print(f"User ID:      {user_id}")
    print(f"Org ID:       {org_id}")
    print(f"Role:         ADMIN")
    print(f"Expires in:   {ACCESS_TOKEN_EXPIRE_MINUTES} minutes")
    print(f"Algorithm:    {ALGORITHM}")
    print("\n" + "-"*80)
    print("\n📌 How to Use:")
    print("-"*80)
    print("\n1. For cURL requests:")
    print(f'   curl -X GET https://cybersecurity-tracker.onrender.com/api/dashboard \\')
    print(f'     -H "Authorization: Bearer {token}"')
    print("\n2. For local testing:")
    print(f'   curl -X GET http://localhost:8000/api/dashboard \\')
    print(f'     -H "Authorization: Bearer {token}"')
    print("\n3. For JavaScript/Frontend:")
    print(f'   const headers = {{')
    print(f'     "Authorization": "Bearer {token}"')
    print(f'   }};')
    print("\n" + "="*80)
    
    return token

if __name__ == "__main__":
    print("\n🚀 Generating JWT token for API testing...\n")
    generate_test_token()
