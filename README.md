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
- Real-time statistics with 6 key metrics (incidents, vulnerabilities, patch coverage)
- Patch coverage progress bar visualization
- Incident trends (30-day history)
- Severity distribution analysis
- Critical vulnerabilities highlighting
- Professional icon-based design with color coding

### Incident Management
- Full CRUD operations with search, filter, pagination
- Severity levels (Critical, High, Medium, Low)
- Status tracking (Open, Investigating, Resolved, Closed)
- Team assignments and collaboration
- Comments and timeline
- Multi-tenant isolation

### Vulnerability Management
- CVE tracking with CVSS scores
- Patch status management with coverage tracking
- Remediation tracking
- Link vulnerabilities to incidents
- Filter by severity and status
- Bulk actions support

### Network Monitoring (NEW)
- **WiFi Device Tracking**
  - Auto-detect router (Tenda, TP-Link, UniFi, Meraki, Mikrotik)
  - List connected devices with MAC/IP addresses
  - Device type detection (laptop, phone, tablet, IoT)
  - Connection time and signal strength tracking
  - Real-time online/offline status

- **DNS Query Logging**
  - Track websites visited by each device
  - Auto-categorization (social, streaming, work, news, adult, malware)
  - Block/allow filtering
  - DNS query history per user/device
  - Top domains analytics

- **Network Policies**
  - Block content categories
  - Create custom access rules
  - Enable/disable policies on demand

- **Advanced Monitoring Options**
  - Device Discovery automation
  - Real-time alerts for suspicious activity
  - Bandwidth usage monitoring
  - Content filtering configuration
  - Data retention policies

### Email Notifications & Webhooks
- Email alerts for new incidents and critical vulnerabilities
- Slack integration with formatted messages
- Microsoft Teams adaptive cards
- Webhook management UI
- Async notification delivery (non-blocking)

### Reports & Analytics
- PDF report generation
- Audit logs with full change history
- User activity tracking
- Compliance reporting

### Security Features
- JWT authentication with token refresh
- Bcrypt password hashing
- Role-based access control (ADMIN, ANALYST, VIEWER)
- Comprehensive audit logging
- Multi-tenant with organization isolation
- Row-Level Security policies
- Rate limiting (100 req/min per IP)
- SQL injection prevention (parameterized queries)

### API Features
- RESTful API design with 40+ endpoints
- Interactive API documentation (Swagger)
- Full error handling
- Request/response validation
- Search, filter, pagination support
- Async operations

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
- `GET /incidents` - List all incidents with search/filter/pagination
- `POST /incidents` - Create incident
- `GET /incidents/{id}` - Get incident details
- `PUT /incidents/{id}` - Update incident
- `DELETE /incidents/{id}` - Delete incident
- `GET /incidents/{id}/comments` - Get comments
- `POST /incidents/{id}/comments` - Add comment

### Vulnerabilities
- `GET /vulnerabilities` - List vulnerabilities with search/filter/pagination
- `POST /vulnerabilities` - Create vulnerability
- `GET /vulnerabilities/{id}` - Get vulnerability details
- `PUT /vulnerabilities/{id}` - Update vulnerability
- `DELETE /vulnerabilities/{id}` - Delete vulnerability
- `POST /vulnerabilities/{id}/incidents/{incident_id}` - Link to incident

### Dashboard
- `GET /dashboard` - Complete dashboard data with stats and trends
- `GET /dashboard/stats` - Statistics only
- `GET /dashboard/trends` - Incident trends (30-day history)
- `GET /dashboard/severity-distribution` - Severity breakdown

### Network Monitoring
- `POST /network/wifi-config/detect` - Auto-detect router
- `POST /network/wifi-config/test-connection` - Test router credentials
- `POST /network/wifi-config` - Setup router configuration
- `GET /network/wifi-config` - Get current router config
- `POST /network/wifi-config/sync` - Sync devices from router
- `GET /network/devices` - List connected devices
- `GET /network/devices/{id}` - Get device details
- `GET /network/devices/{id}/dns-history` - Get device DNS history
- `GET /network/dns-logs` - Get all DNS queries
- `GET /network/dns-logs/blocked` - Get blocked queries
- `POST /network/dns-logs/import` - Import DNS logs
- `GET /network/stats` - Get network analytics
- `POST /network/policies` - Create network policy
- `GET /network/policies` - List policies
- `PUT /network/policies/{id}` - Update policy
- `DELETE /network/policies/{id}` - Delete policy

### Alerts & Notifications
- `GET /alerts` - List alerts
- `PUT /alerts/{id}` - Mark alert as read
- `DELETE /alerts/{id}` - Delete alert

### Webhooks
- `POST /integrations/webhooks` - Create webhook
- `GET /integrations/webhooks` - List webhooks
- `PUT /integrations/webhooks/{id}` - Update webhook
- `DELETE /integrations/webhooks/{id}` - Delete webhook

### Reports & Audit
- `GET /reports` - Generate reports
- `GET /audit-logs` - Get audit log history

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
- **incident_vulnerabilities** - Relationship mapping

### Network Monitoring (NEW)
- **connected_devices** - WiFi connected devices with stats
- **dns_logs** - DNS query history with categorization
- **site_categories** - Domain categorization database
- **wifi_configs** - Router configuration storage
- **network_policies** - Network access control rules

### Audit & Compliance
- **audit_logs** - Full change history for compliance
- **alerts** - Notification system
- **api_keys** - Integration API keys
- **webhooks** - External service integrations
- **notification_preferences** - User notification settings

**Total Tables:** 16 with proper indexes, foreign keys, and multi-tenant isolation

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

## 🌐 Network Monitoring Setup

### Supported Routers
1. **Tenda F3** - Home routers with web interface
2. **Ubiquiti UniFi** - Enterprise WiFi controllers
3. **Cisco Meraki** - Cloud-managed WiFi
4. **TP-Link** - Popular budget routers
5. **Mikrotik RouterOS** - Advanced routing

### Quick Setup
1. Go to `/network/settings`
2. Click "🔍 Detect My Router" or "📝 Enter Manually"
3. Enter your router admin password
4. Click "Test & Save"
5. Go to `/network` and click "Sync Now"

### Features
- Auto-discover connected devices
- Track websites visited (DNS logs)
- Block content categories via policies
- View per-device internet history
- Monitor bandwidth usage
- Real-time device status

## 🔐 Security Best Practices

✅ Implemented:
- Bcrypt password hashing (cost factor 12)
- JWT token authentication with refresh
- CORS protection with origin validation
- SQL injection prevention (parameterized queries)
- Environment variable secrets management
- Row-Level Security (RLS) for multi-tenant isolation
- HTTPS ready (automatic with Vercel/Render)
- Audit logging for compliance
- Rate limiting (100 req/min per IP)
- Network monitoring with user consent

## 🎓 Learning Value

This project demonstrates:
- Full-stack production architecture
- Modern Python web framework (FastAPI)
- React with Next.js best practices
- PostgreSQL advanced features with proper indexing
- Cloud deployment patterns (Vercel, Render, Supabase)
- Security-first development approach
- Team collaboration features
- Real-world incident management
- Network monitoring and device tracking
- Email and webhook integrations
- Rate limiting and API security
- Multi-tenant application design
- Async operations and non-blocking requests
- Professional UI with proper iconography

Perfect for:
- Portfolio showcase of full-stack development
- Learning modern web development best practices
- Understanding security operations and monitoring
- Enterprise application design patterns
- Network security and monitoring implementation
- Integration with real hardware (WiFi routers)

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
