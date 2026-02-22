# Quick Start - Priority 1 Features

Get up and running with search, notifications, and webhooks in 5 minutes.

---

## 1. Backend Setup

### Local Development

```bash
cd backend

# Install new dependencies
pip install -r requirements.txt

# Configure email (.env file)
cp .env.example .env
nano .env  # Add SMTP credentials

# Start backend
python main.py
```

**Required in `.env`:**
```env
DATABASE_URL=postgresql://...  # Your Supabase URL
SECRET_KEY=your-secret-key

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-specific-password
FROM_EMAIL=noreply@cybersecurity-tracker.com

# CORS
CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]
```

### Production (Render)

1. **Update Render environment variables**
   - Go to your Render service
   - Add the SMTP variables above
   - Deploy

2. **Verify it works**
   ```bash
   curl https://your-render-url.onrender.com/health
   ```

---

## 2. Frontend Setup

```bash
# Frontend is already updated - just redeploy
cd ..
npm run build
npm start

# Or just push to GitHub
git add .
git commit -m "Priority 1: Add search, filters, pagination, and notifications"
git push
```

---

## 3. Test Search & Filters

### On Incidents Page

1. Type in search box: `malware`
   - Should filter incidents with "malware" in title/description
   
2. Use dropdowns:
   - Status: Select "OPEN"
   - Severity: Select "CRITICAL"
   - Type: Select "unauthorized_access"
   
3. Try pagination:
   - Create 20+ incidents to see pagination
   - Click "Next" button

### On Vulnerabilities Page

1. Type in search: `CVE-2024`
   - Should filter vulnerabilities with CVE ID
   
2. Filter:
   - Status: "UNPATCHED"
   - Severity: "CRITICAL"
   
3. Pagination works same as incidents

---

## 4. Test Email Notifications

### Setup Gmail

1. Go to [Google Account](https://myaccount.google.com/security)
2. Enable 2-Step Verification
3. Generate [App Password](https://myaccount.google.com/apppasswords)
4. Copy the 16-character password
5. Add to `.env` or Render:
   ```
   SMTP_USER=your-email@gmail.com
   SMTP_PASSWORD=xxxx xxxx xxxx xxxx  # Your app password
   ```

### Create Test Incident

**Via Dashboard:**
1. Go to Incidents page
2. Click "+ New Incident"
3. Fill in details
4. Click "Create"

**Or via API:**
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Security Breach",
    "description": "Testing email notifications",
    "severity": "CRITICAL",
    "incident_type": "unauthorized_access"
  }' \
  http://localhost:8000/api/incidents
```

**Check email:** Should receive alert within 5 seconds

### Create Test Vulnerability

**Via Dashboard:**
1. Go to Vulnerabilities page
2. Click "+ New Vulnerability"
3. Add CVE-2024-TEST (or real CVE)
4. Set severity to CRITICAL or HIGH
5. Click "Create"

**Email:** Should be sent automatically if severity ≥ HIGH

---

## 5. Test Webhooks (Slack)

### Get Slack Webhook URL

1. Go to your Slack workspace
2. Settings → Integrations → Incoming Webhooks
3. Click "Add New Webhook to Workspace"
4. Select a channel (e.g., #security-alerts)
5. Copy the webhook URL

### Setup Webhook in App

1. Go to **Settings → Integrations**
2. Click **"Manage Webhooks"**
3. Click **"Create Webhook"**
4. Fill in:
   - Name: `Slack Security Alerts`
   - URL: `https://hooks.slack.com/services/...`
   - Events: Select `all` or `incident` and `vulnerability`
5. Click **Save**

### Test Webhook

1. Go to Incidents page
2. Create new incident
3. Go to your Slack channel
4. Should see formatted message with incident details

**Slack message includes:**
- Incident title and severity
- Description
- Red button to view in dashboard

---

## 6. API Endpoints Reference

### Search & Filter Incidents

```bash
# All incidents
GET /api/incidents

# Search by title
GET /api/incidents?search=malware

# Filter by status
GET /api/incidents?status=OPEN

# Filter by severity
GET /api/incidents?severity=CRITICAL

# Filter by type
GET /api/incidents?incident_type=data_breach

# Pagination
GET /api/incidents?skip=0&limit=10

# Combined
GET /api/incidents?search=breach&severity=HIGH&status=OPEN&skip=0&limit=10
```

### Search & Filter Vulnerabilities

```bash
# Search CVE
GET /api/vulnerabilities?search=CVE-2024

# Filter by status
GET /api/vulnerabilities?status=UNPATCHED

# Filter by severity
GET /api/vulnerabilities?severity=CRITICAL

# Pagination
GET /api/vulnerabilities?skip=10&limit=10

# Combined
GET /api/vulnerabilities?search=CVE&severity=HIGH&status=UNPATCHED&skip=0&limit=10
```

### Create Incident (Triggers Email)

```bash
POST /api/incidents
{
  "title": "String",
  "description": "String",
  "severity": "CRITICAL|HIGH|MEDIUM|LOW",
  "incident_type": "data_breach|malware|unauthorized_access|...",
  "affected_systems": ["server-1", "server-2"],
  "assigned_to": "user-uuid-optional"
}
```

### Create Vulnerability (Triggers Email if HIGH/CRITICAL)

```bash
POST /api/vulnerabilities
{
  "cve_id": "CVE-2024-1234",
  "title": "String",
  "description": "String",
  "severity": "CRITICAL|HIGH|MEDIUM|LOW|INFO",
  "cvss_score": 8.5,
  "affected_systems": ["system-1"],
  "status": "UNPATCHED|PATCHED|MITIGATED|MONITORING"
}
```

---

## 7. Admin Panel Configuration

### Email Preferences (User Settings)

Users can control their notifications:
1. Go to **Settings → Notifications**
2. Toggle options:
   - ☑️ Email on New Incident
   - ☑️ Critical Vulnerability Alerts
   - ☑️ Incident Updates
   - ☑️ Daily Digest
3. Click **"Save Preferences"**

### Manage Webhooks

1. Go to **Settings → Integrations**
2. Click **"Manage Webhooks"**
3. View, edit, or delete existing webhooks
4. Create new webhook

---

## 8. Verify Deployment

### Check Health

```bash
# Backend health
curl https://your-backend-url/health

# Frontend loads
https://cybersecurity-tracker.vercel.app/

# API docs
https://your-backend-url/docs
```

### Check Features

- [ ] Search box appears on incidents page
- [ ] Filter dropdowns work
- [ ] Pagination controls visible
- [ ] Create incident sends email
- [ ] Create critical vulnerability sends email
- [ ] Webhook message appears in Slack

---

## 9. Troubleshooting

### Email not sending?

```bash
# Check backend logs
tail -f backend/logs/ | grep -i email

# Verify SMTP settings
echo $SMTP_USER
echo $SMTP_PASSWORD

# Test with curl
curl -X POST \
  -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/incidents \
  -d '{"title":"Test","description":"Test","severity":"CRITICAL","incident_type":"other"}'
```

### Search not working?

```bash
# Test API directly
curl "http://localhost:8000/api/incidents?search=malware"

# Check browser network tab (F12 → Network)
# Should see request with ?search=malware parameter
```

### Slack not receiving messages?

```bash
# Test webhook URL with curl
curl -X POST \
  -H 'Content-type: application/json' \
  -d '{"text":"Test message"}' \
  https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Should see "1" response (success)
```

---

## 10. Next Steps

Once working, consider:

1. **Set up proper email alerts** 
   - Configure user notification preferences
   - Test email delivery

2. **Create more webhooks**
   - Slack for security team
   - Teams for ops team
   - Custom webhooks for SIEM integration

3. **Monitor performance**
   - Check response times
   - Set up log aggregation
   - Monitor email delivery rate

4. **Plan Priority 2 features**
   - Reports & PDF export
   - Audit logs viewer
   - Advanced filtering

---

## Support

For issues:

1. Check logs: `Render Logs` or `backend/logs/`
2. Read: `/PRIORITY_1_FEATURES.md` (detailed docs)
3. Review: `/DEPLOYMENT_CHECKLIST.md` (deployment guide)

---

**Version:** 1.0
**Last Updated:** Feb 22, 2024
**Status:** ✅ Production Ready
