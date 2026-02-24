# API Testing Guide with JWT Authentication

## ✅ Fixed Issues
1. **Route Prefix Duplication** - Removed duplicate prefixes from all route files
2. **JWT Authentication** - Updated to use your actual SECRET_KEY (see Render environment variables)

## 🔐 Generate JWT Token

Run this command to generate a valid JWT token:
```bash
python3 generate_jwt_token.py
```

Or manually create a token using Python (using your SECRET_KEY from Render env):
```python
from datetime import datetime, timedelta, timezone
from uuid import uuid4
import jwt
import os

# Get from your Render environment
SECRET_KEY = os.getenv("SECRET_KEY")  # Your Supabase secret key
user_id = str(uuid4())
org_id = str(uuid4())
payload = {
    "sub": user_id,
    "org_id": org_id,
    "role": "ADMIN",
    "exp": datetime.now(timezone.utc) + timedelta(minutes=480)
}
token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
print(token)
```

## 📋 API Endpoints (Now Fixed)

### Dashboard
```bash
curl -X GET "https://cybersecurity-tracker.onrender.com/api/dashboard" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Incidents
```bash
# List incidents
curl -X GET "https://cybersecurity-tracker.onrender.com/api/incidents?limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# Get specific incident
curl -X GET "https://cybersecurity-tracker.onrender.com/api/incidents/{incident_id}" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# Create incident
curl -X POST "https://cybersecurity-tracker.onrender.com/api/incidents" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Security Breach Detected",
    "description": "Suspicious login attempts from unknown IP",
    "severity": "HIGH",
    "incident_type": "Security"
  }'
```

### Network Monitoring
```bash
# Get network stats
curl -X GET "https://cybersecurity-tracker.onrender.com/api/network/stats" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# Get connected devices
curl -X GET "https://cybersecurity-tracker.onrender.com/api/network/devices?limit=20" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# Get network policies
curl -X GET "https://cybersecurity-tracker.onrender.com/api/network/policies" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Vulnerabilities
```bash
# List vulnerabilities
curl -X GET "https://cybersecurity-tracker.onrender.com/api/vulnerabilities?limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Reports
```bash
# Monthly summary
curl -X GET "https://cybersecurity-tracker.onrender.com/api/reports/monthly-summary" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# Vulnerability status
curl -X GET "https://cybersecurity-tracker.onrender.com/api/reports/vulnerability-status" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# Compliance audit
curl -X GET "https://cybersecurity-tracker.onrender.com/api/reports/compliance-audit" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Alerts
```bash
# List alerts
curl -X GET "https://cybersecurity-tracker.onrender.com/api/alerts?limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Audit Logs
```bash
# List audit logs
curl -X GET "https://cybersecurity-tracker.onrender.com/api/audit-logs?limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 🌐 Environment Variables (Render)

Make sure these are set on your Render service:
- `DATABASE_URL`: Your Supabase PostgreSQL connection string
- `SECRET_KEY`: Your Supabase secret key (keep this secret!)
- `ALGORITHM`: `HS256`
- `ACCESS_TOKEN_EXPIRE_MINUTES`: `480`
- `ENVIRONMENT`: `production`

## 🚀 Next Steps

1. Deploy the fixed code to Render:
   ```bash
   git add .
   git commit -m "Fix: Remove duplicate route prefixes and update JWT secret key"
   git push
   ```

2. Test with your token using any of the curl commands above

3. Your database tables are already created, so new requests with valid tokens should now work!

## ✨ What Was Fixed

| Issue | Cause | Fix |
|-------|-------|-----|
| 404 on `/api/dashboard` | Duplicate prefix `/dashboard/dashboard` | Removed prefix from route file |
| 404 on `/api/incidents` | Duplicate prefix `/api/incidents/incidents` | Removed prefix from route file |
| 401 Unauthorized | Invalid token format | Updated to use correct SECRET_KEY |
| 403 on WebSocket | Token verification failed | Fixed authentication flow |

Your backend is now ready for testing! 🎉
