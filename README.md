# Cybersecurity Incident Tracker + Vulnerability Dashboard

Enterprise-grade incident and vulnerability management platform built with modern, production-ready technologies.

## 🏗️ Architecture

### Frontend
- **Framework**: Next.js 16 (App Router)
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui
- **State Management**: React Context + SWR
- **Deployment**: Vercel

### Backend
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL (Supabase)
- **Auth**: JWT + Bcrypt
- **ORM**: SQLAlchemy
- **Deployment**: Render

### Database
- **Provider**: Supabase (PostgreSQL)
- **Security**: Row-Level Security (RLS), Multi-tenant isolation
- **Tables**: Organizations, Users, Incidents, Vulnerabilities, Comments, Audit Logs, and more

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.10+
- PostgreSQL database (Supabase account)
- Vercel and Render accounts

### 1. Setup Database

The database schema has already been created in your Supabase project. The SQL migrations are in `/scripts/01_init_schema.sql`.

**Tables created:**
- organizations, users, incidents, vulnerabilities
- incident_vulnerabilities, comments, alerts
- audit_logs, api_keys, webhooks, notification_preferences

### 2. Setup Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env with your Supabase credentials
# DATABASE_URL=postgresql://user:password@host:port/database
# SECRET_KEY=your-secret-key

# Run server
python main.py
```

Backend will be available at `http://localhost:8000`
API docs: `http://localhost:8000/docs`

### 3. Setup Frontend

```bash
cd .. # Go back to root

# Install dependencies
npm install

# Create .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api" > .env.local

# Run development server
npm run dev
```

Frontend will be available at `http://localhost:3000`

## 📋 Features Implemented

### Dashboard
- 📊 Real-time statistics and KPIs
- 📈 Incident trends (30-day history)
- 🎯 Severity distribution charts
- 🔴 Critical vulnerabilities highlighting

### Incident Management
- ✅ Full CRUD operations
- 🏷️ Severity levels (Critical, High, Medium, Low)
- 📊 Status tracking (Open, Investigating, Resolved, Closed)
- 👥 Team assignments and collaboration
- 💬 Comments and timeline
- 🏢 Multi-tenant isolation

### Vulnerability Management
- ✅ CVE tracking with CVSS scores
- 📋 Patch status management
- 🛠️ Remediation tracking
- 🔗 Link vulnerabilities to incidents
- 🔍 Filter by severity and status

### Security Features
- 🔐 JWT authentication
- 🔑 Bcrypt password hashing
- 👤 Role-based access control (ADMIN, ANALYST, VIEWER)
- 📝 Comprehensive audit logging
- 🏗️ Multi-tenant with organization isolation
- 🔒 Row-Level Security policies

### API Features
- 🔌 RESTful API design
- 📚 Interactive API documentation
- 🔄 Full error handling
- 📊 Request/response validation

## 🔐 Authentication

### Registration Flow
1. Create organization and admin account
2. Receive JWT token
3. Token stored in localStorage
4. Automatically included in API requests

### Login Flow
1. Email and password authentication
2. JWT token issued on success
3. Token refreshed automatically

### Roles
- **ADMIN**: Full access, user management, settings
- **ANALYST**: Create/update incidents and vulnerabilities
- **VIEWER**: Read-only access to incidents and data

## 📦 API Endpoints

### Authentication
- `POST /auth/register` - Create org and admin user
- `POST /auth/login` - Login with credentials
- `GET /auth/me` - Get current user profile

### Incidents
- `GET /incidents` - List all incidents
- `POST /incidents` - Create incident
- `GET /incidents/{id}` - Get incident details
- `PUT /incidents/{id}` - Update incident
- `DELETE /incidents/{id}` - Delete incident
- `GET /incidents/{id}/comments` - Get comments
- `POST /incidents/{id}/comments` - Add comment

### Vulnerabilities
- `GET /vulnerabilities` - List vulnerabilities
- `POST /vulnerabilities` - Create vulnerability
- `GET /vulnerabilities/{id}` - Get vulnerability details
- `PUT /vulnerabilities/{id}` - Update vulnerability
- `DELETE /vulnerabilities/{id}` - Delete vulnerability
- `POST /vulnerabilities/{id}/incidents/{incident_id}` - Link to incident

### Dashboard
- `GET /dashboard` - Complete dashboard data
- `GET /dashboard/stats` - Statistics only
- `GET /dashboard/trends` - Incident trends
- `GET /dashboard/severity-distribution` - Severity breakdown

## 🚢 Production Deployment

### Frontend (Vercel)

```bash
# Push to Git
git push origin main

# Vercel auto-deploys on push
# Set environment variables in Vercel dashboard:
NEXT_PUBLIC_API_URL=https://api.yourdomain.com/api
```

### Backend (Render)

1. Create new Web Service on Render
2. Connect GitHub repository
3. Set build command: `pip install -r backend/requirements.txt`
4. Set start command: `cd backend && python main.py`
5. Add environment variables:
   - `DATABASE_URL` - Supabase connection string
   - `SECRET_KEY` - Secure random key
   - `CORS_ORIGINS` - Your frontend domain

### Database (Supabase)

Already configured with:
- PostgreSQL 15
- Automatic backups
- Row-Level Security
- Real-time capabilities

## 📊 Database Schema

### Core Tables
- **organizations** - Multi-tenant base
- **users** - Team members with roles
- **incidents** - Security incidents
- **vulnerabilities** - CVE tracking
- **comments** - Team collaboration

### Audit & Compliance
- **audit_logs** - Full change history
- **alerts** - Notifications
- **api_keys** - Integration keys
- **webhooks** - External integrations
- **notification_preferences** - User settings

## 🔧 Configuration

### Backend (.env)
```
DATABASE_URL=postgresql://user:password@host:port/db
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=["http://localhost:3000", "https://yourdomain.com"]
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

## 🧪 Testing

### Backend Health Check
```bash
curl http://localhost:8000/health
```

### Frontend Health Check
```bash
curl http://localhost:3000
```

## 📚 Stack Benefits

### Why This Stack?

1. **Next.js**
   - Server-side rendering + static generation
   - API routes optional
   - Excellent SEO
   - Used by 30,000+ companies
   - Easy deployment to Vercel

2. **FastAPI**
   - 3x faster than Flask
   - Automatic API documentation (Swagger)
   - Built-in data validation (Pydantic)
   - Async/await support
   - Used heavily in cybersecurity tools

3. **PostgreSQL + Supabase**
   - Enterprise-grade reliability
   - Row-Level Security built-in
   - Real-time capabilities
   - Managed service (no DevOps needed)
   - Free tier available

4. **Tailwind CSS + shadcn/ui**
   - Modern design system
   - Fast development
   - Highly customizable
   - Professional appearance
   - Accessibility built-in

## 📈 Performance

- Frontend: Optimized with Next.js caching, compression, code splitting
- Backend: FastAPI is 3x faster than Flask, connection pooling enabled
- Database: Indexed queries, prepared statements, connection pooling

## 🔐 Security Best Practices

✅ Implemented:
- Bcrypt password hashing (cost factor 12)
- JWT token authentication
- CORS protection
- SQL injection prevention (parameterized queries)
- Environment variable secrets management
- Row-Level Security (RLS) for multi-tenant isolation
- HTTPS ready (automatic with Vercel/Render)
- Audit logging for compliance

## 🎓 Learning Value

This project demonstrates:
- Full-stack production architecture
- Modern Python web framework (FastAPI)
- React with Next.js best practices
- PostgreSQL advanced features
- Cloud deployment patterns
- Security-first development
- Team collaboration features
- Real-world incident management

Perfect for:
- Portfolio showcase
- Learning modern web development
- Understanding security operations
- Enterprise application design

## 📞 Support

For issues or questions:
1. Check the API documentation: `http://localhost:8000/docs`
2. Review the code comments
3. Check environment variables are set correctly
4. Verify database connection

## 📄 License

MIT License - Use for commercial and personal projects

---

**Built with ❤️ for security teams worldwide**
