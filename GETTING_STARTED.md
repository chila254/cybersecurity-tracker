# Getting Started with Incident Tracker

This guide will help you get the Cybersecurity Incident Tracker up and running in 15 minutes.

## Quick Start (Local Development)

### Prerequisites

Ensure you have installed:
- **Node.js 18+**: https://nodejs.org/
- **Python 3.10+**: https://python.org/
- **PostgreSQL 12+**: https://www.postgresql.org/ (or use Supabase)

### 1. Clone and Setup Database

#### Option A: Using Supabase (Recommended)

1. Create a Supabase account: https://supabase.com
2. Create a new project
3. In SQL Editor, run the script from `/scripts/01_init_schema.sql`
4. Copy your database URL from Database Settings

#### Option B: Local PostgreSQL

```bash
# Create database
createdb incident_tracker

# Run schema
psql incident_tracker < scripts/01_init_schema.sql
```

### 2. Setup Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env with your database URL
# DATABASE_URL=postgresql://user:password@localhost:5432/incident_tracker
# SECRET_KEY=your-secret-key

# Start server
python main.py
```

Backend running at: http://localhost:8000
API docs: http://localhost:8000/docs

### 3. Setup Frontend

In a new terminal:

```bash
cd .. # Go to root

# Install dependencies
npm install

# Create .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api" > .env.local

# Start development server
npm run dev
```

Frontend running at: http://localhost:3000

## 4. Create Your First Account

1. Open http://localhost:3000
2. Click "Get Started"
3. Fill in organization name, your name, email, and password
4. Click "Create Account"
5. You're logged in! Explore the dashboard

## 5. Create Your First Incident

1. Click "Incidents" in the sidebar
2. Click "+ New Incident"
3. Fill in:
   - **Title**: "Server misconfiguration detected"
   - **Description**: "SQL Server credentials found in production logs"
   - **Severity**: CRITICAL
4. Click "Create"
5. Check the dashboard - your incident appears!

## 6. Create a Vulnerability

1. Click "Vulnerabilities" in the sidebar
2. Click "+ New Vulnerability"
3. Fill in:
   - **Title**: "CVE-2024-1234 - Critical RCE"
   - **CVE ID**: CVE-2024-1234
   - **Severity**: CRITICAL
   - **Status**: UNPATCHED
4. Click "Create"

## Project Structure

```
incident-tracker/
├── app/                          # Next.js frontend
│   ├── page.tsx                  # Landing page
│   ├── login/page.tsx            # Login page
│   ├── register/page.tsx         # Registration
│   ├── dashboard/                # Dashboard pages
│   │   ├── page.tsx              # Main dashboard
│   │   └── layout.tsx            # Dashboard layout
│   ├── incidents/page.tsx        # Incidents management
│   ├── vulnerabilities/page.tsx  # Vulnerabilities management
│   ├── reports/page.tsx          # Reports generation
│   └── settings/page.tsx         # Settings/preferences
│
├── components/
│   ├── dashboard/                # Dashboard components
│   │   ├── sidebar.tsx           # Navigation sidebar
│   │   └── stats-card.tsx        # Statistics cards
│   └── ui/                       # shadcn/ui components
│
├── lib/
│   ├── api-client.ts            # API client utilities
│   └── auth-context.tsx         # Authentication context
│
├── backend/                      # FastAPI Python backend
│   ├── main.py                  # FastAPI app entry
│   ├── requirements.txt          # Python dependencies
│   ├── app/
│   │   ├── database.py          # Database config
│   │   ├── models.py            # SQLAlchemy models
│   │   ├── schemas.py           # Pydantic schemas
│   │   ├── auth.py              # Authentication utilities
│   │   └── routes/              # API routes
│   │       ├── auth.py          # Authentication endpoints
│   │       ├── incidents.py     # Incident management
│   │       ├── vulnerabilities.py
│   │       ├── dashboard.py     # Dashboard analytics
│   │       ├── alerts.py        # Notifications
│   │       └── integrations.py  # API keys & webhooks
│   └── Dockerfile               # Docker configuration
│
├── scripts/
│   └── 01_init_schema.sql      # Database schema
│
├── README.md                    # Project overview
├── DEPLOYMENT.md               # Deployment guide
├── GETTING_STARTED.md         # This file
└── docker-compose.yml         # Docker Compose setup
```

## Key Features Overview

### Authentication
- Sign up with organization name, email, password
- Automatic JWT token generation
- Role-based access (ADMIN, ANALYST, VIEWER)

### Dashboard
- Real-time incident statistics
- 30-day incident trends
- Severity distribution charts
- Recent incidents feed

### Incident Management
- Create incidents with severity levels
- Track status (OPEN, INVESTIGATING, RESOLVED, CLOSED)
- Assign to team members
- Add comments and timeline
- Link vulnerabilities to incidents

### Vulnerability Management
- Track CVEs with CVSS scores
- Patch status management
- Affected systems tracking
- Remediation notes

### Reports
- Monthly security summaries
- Incident analysis reports
- Vulnerability status reports
- Compliance audit logs
- Team performance metrics
- CSV/JSON export

### Settings
- Profile management
- Notification preferences
- Security settings
- API key generation
- Webhook configuration

## API Reference

### Authentication Endpoints

```bash
# Register
POST /api/auth/register
{
  "org_name": "ACME Corp",
  "user_data": {
    "email": "user@acme.com",
    "password": "SecurePassword123",
    "name": "John Doe"
  }
}

# Login
POST /api/auth/login
{
  "email": "user@acme.com",
  "password": "SecurePassword123"
}
```

### Incidents Endpoints

```bash
# List incidents
GET /api/incidents?status=OPEN&severity=CRITICAL

# Create incident
POST /api/incidents
{
  "title": "Incident title",
  "description": "Detailed description",
  "severity": "CRITICAL",
  "incident_type": "data_breach"
}

# Update incident
PUT /api/incidents/{incident_id}
{
  "status": "RESOLVED",
  "severity": "HIGH"
}

# Add comment
POST /api/incidents/{incident_id}/comments
{
  "content": "Team response initiated..."
}
```

### Vulnerabilities Endpoints

```bash
# List vulnerabilities
GET /api/vulnerabilities?severity=CRITICAL&status=UNPATCHED

# Create vulnerability
POST /api/vulnerabilities
{
  "cve_id": "CVE-2024-1234",
  "title": "Critical RCE",
  "severity": "CRITICAL",
  "cvss_score": 9.8
}

# Link to incident
POST /api/vulnerabilities/{vuln_id}/incidents/{incident_id}
```

### Dashboard Endpoints

```bash
# Get all dashboard data
GET /api/dashboard

# Get statistics only
GET /api/dashboard/stats

# Get trends
GET /api/dashboard/trends?days=30

# Get severity distribution
GET /api/dashboard/severity-distribution
```

## Common Tasks

### Adding Team Members

1. Note: Currently, users self-register
2. Future: Admin can invite team members
3. Assign roles in Settings (requires Admin access)

### Setting Up Email Notifications

1. Go to Settings → Notifications
2. Enable desired notification types:
   - Email on new incidents
   - Critical vulnerability alerts
   - Incident updates
   - Daily digest
3. Save preferences

### Connecting to Slack

1. Go to Settings → Integrations
2. Click "Generate API Key"
3. Copy the key
4. In Slack app settings: Add incoming webhook
5. Use API key to authenticate

### Generating Reports

1. Click "Reports"
2. Select report type
3. Click "Generate"
4. Download as PDF

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 3000
lsof -i :3000

# Kill process
kill -9 <PID>
```

### Database Connection Error

```
Error: connect ECONNREFUSED 127.0.0.1:5432
```

**Solution**: 
- Check PostgreSQL is running
- Verify DATABASE_URL in .env
- Test connection: `psql [CONNECTION_STRING]`

### API Not Responding

```
Error: Failed to fetch from http://localhost:8000
```

**Solution**:
- Check backend is running: `python main.py`
- Check CORS settings in backend
- Verify NEXT_PUBLIC_API_URL in .env.local

### Login Fails

```
Error: Invalid email or password
```

**Solution**:
- Verify credentials
- Check database has users table
- Check password hashing is working

## Development Tips

### Debugging

#### Frontend
```javascript
// Add to any component
console.log("[v0] Component state:", state)
```

#### Backend
```python
# Add to any route
print("[v0] Variable value:", variable)
```

### Hot Reload

- Frontend: Automatic with Next.js dev server
- Backend: Automatic with Uvicorn --reload flag

### Database Inspection

#### With Supabase
1. Go to Table Editor
2. Browse tables directly
3. View and edit records

#### With PostgreSQL
```bash
# Connect to database
psql incident_tracker

# List tables
\dt

# View records
SELECT * FROM incidents LIMIT 10;
```

## Performance Tips

1. **Database**: Indexes already added on common queries
2. **API**: Connection pooling enabled
3. **Frontend**: Images optimized, code split by route
4. **Caching**: Implement Redis for sessions (optional)

## Security Checklist

- ✅ Passwords hashed with bcrypt
- ✅ JWT tokens with 30-minute expiration
- ✅ CORS protection enabled
- ✅ SQL injection prevention (parameterized queries)
- ✅ Role-based access control
- ✅ Audit logging enabled
- ⬜ Rate limiting (recommended to add)
- ⬜ Two-factor authentication (future feature)

## Next Steps

1. **Customize**: Update colors, logo, branding in Settings
2. **Integrate**: Connect to Slack, Jira, or email
3. **Deploy**: Follow DEPLOYMENT.md for production setup
4. **Scale**: Monitor performance and optimize as needed
5. **Train**: Onboard team members

## Learning Resources

- **FastAPI**: https://fastapi.tiangolo.com/
- **Next.js**: https://nextjs.org/learn
- **PostgreSQL**: https://www.postgresql.org/docs/
- **SQLAlchemy**: https://docs.sqlalchemy.org/
- **React**: https://react.dev/
- **Tailwind CSS**: https://tailwindcss.com/docs

## Support

For issues:
1. Check the code comments
2. Review the API documentation at `/docs`
3. Check GitHub issues
4. Ask in discussions

## Contributing

Found a bug? Want to contribute?
1. Create a new branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

---

**Happy incident tracking! 🚀**

For production deployment, see [DEPLOYMENT.md](./DEPLOYMENT.md)
