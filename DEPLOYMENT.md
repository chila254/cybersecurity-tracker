# Deployment Guide

Comprehensive guide for deploying the Cybersecurity Incident Tracker to production.

## Overview

The system consists of three main components:
1. **Frontend**: Next.js app (deployed to Vercel)
2. **Backend**: FastAPI Python service (deployed to Render)
3. **Database**: PostgreSQL (via Supabase)

## Prerequisites

- Supabase account (https://supabase.com)
- Vercel account (https://vercel.com)
- Render account (https://render.com)
- GitHub repository with this code

## Step 1: Setup Database (Supabase)

### 1.1 Create Supabase Project

1. Go to https://supabase.com and sign up
2. Create a new project (choose a region close to your users)
3. Wait for the project to initialize (2-3 minutes)
4. Note down:
   - Project URL
   - Project Reference ID
   - anon/public key
   - service_role key

### 1.2 Create Database Tables

1. Go to SQL Editor in Supabase dashboard
2. Copy the entire content from `/scripts/01_init_schema.sql`
3. Paste into SQL Editor
4. Click "Run"
5. Verify all tables are created by checking the Tables section

### 1.3 Configure RLS (Row-Level Security)

Already configured in the SQL schema. No additional setup needed.

### 1.4 Get Connection String

1. Go to Project Settings → Database
2. Find "Connection String" → PostgreSQL
3. Copy the connection string
4. Replace:
   - `[YOUR-PASSWORD]` with your database password
   - `[YOUR-PROJECT-ID]` with your project reference

Example format:
```
postgresql://postgres:[password]@db.xxxxx.supabase.co:5432/postgres
```

## Step 2: Deploy Backend (Render)

### 2.1 Prepare Repository

1. Push your code to GitHub
2. Ensure `backend/` directory is at the root level
3. Ensure `backend/requirements.txt` exists

### 2.2 Create Render Web Service

1. Go to https://render.com and sign in
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Configure:

**Settings:**
```
Name: incident-tracker-api
Runtime: Python 3.11
Build Command: pip install -r backend/requirements.txt
Start Command: cd backend && uvicorn main:app --host 0.0.0.0 --port 8000
```

### 2.3 Add Environment Variables

In Render dashboard, go to Environment → Add Variable for each:

```
DATABASE_URL=postgresql://postgres:[password]@db.xxxxx.supabase.co:5432/postgres
SECRET_KEY=generate-a-random-secure-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=["https://yourdomain.com"]
ENVIRONMENT=production
```

Generate a random SECRET_KEY:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2.4 Deploy

1. Click "Create Web Service"
2. Wait for deployment (5-10 minutes)
3. Once deployed, you'll get a URL like: `https://incident-tracker-api.onrender.com`
4. Test the API: `https://incident-tracker-api.onrender.com/docs`

### 2.5 Note Backend URL

Copy the Render URL for frontend configuration:
- Example: `https://incident-tracker-api.onrender.com/api`

## Step 3: Deploy Frontend (Vercel)

### 3.1 Connect GitHub Repository

1. Go to https://vercel.com and sign in
2. Click "Add New" → "Project"
3. Select your GitHub repository
4. Vercel will auto-detect Next.js

### 3.2 Configure Environment Variables

In Vercel dashboard, go to Settings → Environment Variables:

```
NEXT_PUBLIC_API_URL=https://incident-tracker-api.onrender.com/api
```

### 3.3 Deploy

1. Click "Deploy"
2. Wait for build to complete (3-5 minutes)
3. You'll get a Vercel URL like: `https://incident-tracker.vercel.app`

### 3.4 Custom Domain (Optional)

1. In Vercel, go to Settings → Domains
2. Add your custom domain
3. Follow DNS configuration instructions

## Step 4: Update Backend CORS

Now that you have the frontend URL, update the backend:

1. Go to Render dashboard
2. Find your web service
3. Go to Environment → Edit `CORS_ORIGINS`
4. Update to:
```
["https://incident-tracker.vercel.app", "https://yourdomain.com"]
```

## Step 5: Verify Deployment

### Test Backend

```bash
curl https://incident-tracker-api.onrender.com/health
# Should return: {"status":"healthy","service":"incident-tracker-api","environment":"production"}
```

### Test Frontend

1. Go to https://incident-tracker.vercel.app
2. Create an account
3. Login and verify dashboard loads

### Test Database Connection

1. Login to your account
2. Create an incident
3. Check it appears in the dashboard

## SSL/TLS Certificates

- **Vercel**: Automatic HTTPS (provided by Vercel)
- **Render**: Automatic HTTPS (provided by Render)
- Both use Let's Encrypt certificates

## Monitoring & Logs

### Vercel Logs

1. Go to Deployment → Logs
2. View real-time logs during API requests

### Render Logs

1. Go to your web service → Logs
2. Monitor application and runtime logs

### Supabase Logs

1. Go to Database → Logs
2. View SQL query logs for debugging

## Scaling

### Database Scaling (Supabase)

1. Upgrade to paid plan for more storage
2. Automatic scaling included
3. Read replicas available on Pro+ plan

### API Scaling (Render)

1. Go to Service → Environment → Scaling
2. Increase instance size or upgrade plan
3. Auto-scaling available on paid plans

### Frontend Scaling (Vercel)

1. Automatic edge network scaling
2. No manual configuration needed
3. Built-in CDN included

## Backup Strategy

### Database Backups

Supabase provides:
- Daily automated backups
- 7-day backup retention on free tier
- 30-day retention on paid tiers
- Point-in-time recovery available

To manually backup:
1. Go to Database → Backups
2. Click "Create backup"

### Code Backups

GitHub serves as your code backup:
1. Ensure all changes are committed
2. Push to main branch
3. Both Vercel and Render auto-deploy

## Security Best Practices

### 1. Environment Variables
- Never commit `.env` files to Git
- Use Render/Vercel environment variable management
- Rotate SECRET_KEY quarterly

### 2. Database
- Enable Row-Level Security (already done)
- Use strong password for PostgreSQL
- Restrict database access to Render IP only

### 3. API
- Keep JWT tokens short-lived (30 minutes)
- Implement rate limiting for authentication endpoints
- Monitor failed login attempts

### 4. Frontend
- Enable Content Security Policy headers
- Use HTTPS only (automatic)
- Keep dependencies updated

### 5. Monitoring
- Set up error tracking (Sentry recommended)
- Monitor API response times
- Alert on failed deployments

## Troubleshooting

### Backend Won't Start

**Error**: `ModuleNotFoundError: No module named 'fastapi'`
- Solution: Ensure `pip install -r backend/requirements.txt` runs in build

**Error**: `connection to database failed`
- Solution: Check DATABASE_URL is correct in Render environment

### API Calls Fail

**Error**: `CORS error in browser console`
- Solution: Update CORS_ORIGINS in Render to include frontend URL

**Error**: `401 Unauthorized`
- Solution: Token might be expired, user needs to login again

### Database Errors

**Error**: `relation "organizations" does not exist`
- Solution: Run SQL script from `/scripts/01_init_schema.sql` in Supabase

**Error**: `permission denied`
- Solution: Check user privileges, verify RLS policies aren't blocking access

## Rollback Procedure

### Revert Frontend

1. Go to Vercel → Deployments
2. Find the previous successful deployment
3. Click "Redeploy"

### Revert Backend

1. Go to Render → Deployments
2. Find the previous successful deployment
3. Click "Deploy"

### Revert Database

1. Go to Supabase → Database → Backups
2. Restore from backup point
3. Note: May lose recent changes

## Performance Optimization

### Frontend (Next.js)

- Images optimized with `next/image`
- Automatic code splitting
- CSS minification
- Implement lazy loading for routes

### Backend (FastAPI)

- Connection pooling enabled
- Query optimization with indexes
- Caching with Cache-Control headers
- Consider Redis for session storage

### Database (PostgreSQL)

- Indexes on frequently queried columns (already added)
- Regular VACUUM/ANALYZE
- Monitor slow queries
- Consider read replicas for read-heavy workloads

## Cost Estimates (Monthly)

### Supabase
- Free tier: $0 (up to 500MB)
- Pro tier: $25/month (recommended for production)

### Render
- Web Service: $7/month (starter)
- Free tier: $0 (limited)

### Vercel
- Free tier: $0
- Pro tier: $20/month (recommended for production)

**Total**: ~$52/month for production setup

## Support & Resources

- Supabase Docs: https://supabase.com/docs
- Render Docs: https://render.com/docs
- Vercel Docs: https://vercel.com/docs
- FastAPI Docs: https://fastapi.tiangolo.com
- Next.js Docs: https://nextjs.org/docs

## Next Steps After Deployment

1. Set up monitoring and alerting
2. Configure email notifications
3. Create team members and assign roles
4. Set up integrations (Slack, Jira, etc.)
5. Create sample incidents for testing
6. Document incident response procedures
7. Train team on platform usage

---

**Congratulations! Your incident tracker is now live.**
