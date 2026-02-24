#!/usr/bin/env python3
"""
Generate a valid JWT token using your SECRET_KEY from Render
Run: python3 generate_jwt_token.py
"""

from datetime import datetime, timedelta, timezone
from uuid import uuid4
import sys
import os

# Install PyJWT if needed
try:
    import jwt
except ImportError:
    print("Installing required package...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "PyJWT", "--break-system-packages", "-q"])
    import jwt

# Your actual SECRET_KEY from Render environment
# Get this from your Render service environment variables
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 hours

def generate_token():
    """Generate a valid JWT token using your SECRET_KEY"""
    
    # Create unique IDs for user and organization
    user_id = str(uuid4())
    org_id = str(uuid4())
    
    # Token payload - must match what your backend expects
    payload = {
        "sub": user_id,           # subject (user_id)
        "org_id": org_id,         # organization_id
        "role": "ADMIN",          # user role
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    
    # Encode token with your SECRET_KEY
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    print("\n" + "="*90)
    print("✅ VALID JWT TOKEN FOR YOUR RENDER BACKEND")
    print("="*90)
    print(f"\n🔐 Token:\n{token}\n")
    print("="*90)
    print("\n📋 Token Details:")
    print("-"*90)
    print(f"  User ID:      {user_id}")
    print(f"  Org ID:       {org_id}")
    print(f"  Role:         ADMIN")
    print(f"  Expires in:   {ACCESS_TOKEN_EXPIRE_MINUTES} minutes")
    print(f"  Algorithm:    {ALGORITHM}")
    print(f"  Secret Key:   {SECRET_KEY[:20]}..." if SECRET_KEY != "your-secret-key-here" else f"  Secret Key:   (not set - configure on Render)")
    print("\n" + "-"*90)
    
    print("\n📌 Usage Examples:\n")
    
    print("1️⃣  cURL - Get Dashboard:")
    print("-"*90)
    print(f'curl -X GET "https://cybersecurity-tracker.onrender.com/api/dashboard" \\')
    print(f'  -H "Authorization: Bearer {token}"')
    
    print("\n2️⃣  cURL - Get Incidents:")
    print("-"*90)
    print(f'curl -X GET "https://cybersecurity-tracker.onrender.com/api/incidents?limit=10" \\')
    print(f'  -H "Authorization: Bearer {token}"')
    
    print("\n3️⃣  cURL - Get Network Devices:")
    print("-"*90)
    print(f'curl -X GET "https://cybersecurity-tracker.onrender.com/api/network/devices?limit=20" \\')
    print(f'  -H "Authorization: Bearer {token}"')
    
    print("\n4️⃣  JavaScript/Frontend:")
    print("-"*90)
    print(f"""const token = "{token}";
const headers = {{
  "Authorization": `Bearer ${{token}}`,
  "Content-Type": "application/json"
}};

// Example: Get dashboard
fetch("https://cybersecurity-tracker.onrender.com/api/dashboard", {{
  method: "GET",
  headers: headers
}})
.then(res => res.json())
.then(data => console.log(data));
""")
    
    print("-"*90)
    print("\n" + "="*90)
    
    return token

if __name__ == "__main__":
    generate_token()
