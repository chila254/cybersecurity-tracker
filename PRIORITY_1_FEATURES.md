# Priority 1 Features Implementation Guide

This document describes the **Priority 1 features** implemented for the Cybersecurity Incident Tracker:

1. **Search, Filtering & Pagination** (Incidents & Vulnerabilities)
2. **Email Notifications System**
3. **Webhook/Slack Integration**

---

## 1. Search, Filtering & Pagination

### Frontend Features (Incidents & Vulnerabilities Pages)

#### Search
- **Full-text search** across title, description, and CVE ID
- Search updates results **in real-time** without page reload
- Search box with icon in filter panel

#### Filtering
**Incidents Page:**
- Filter by Status (Open, Investigating, Resolved, Closed)
- Filter by Severity (Critical, High, Medium, Low)
- Filter by Incident Type (Data Breach, Malware, etc.)

**Vulnerabilities Page:**
- Filter by Status (Unpatched, Patched, Mitigated, Monitoring)
- Filter by Severity (Critical, High, Medium, Low, Info)

#### Pagination
- **10 items per page** by default
- Previous/Next buttons
- Display current position (e.g., "Showing 1-10 of 45")
- Automatically resets to page 1 when search/filter changes

### Backend Features

#### Enhanced List Endpoints

**GET /api/incidents**
```bash
curl "http://localhost:8000/api/incidents?search=malware&severity=CRITICAL&status=OPEN&skip=0&limit=10"
```

Parameters:
- `search` - Search title/description
- `severity` - Filter by severity
- `status` - Filter by status
- `incident_type` - Filter by incident type
- `skip` - Pagination offset
- `limit` - Page size (max 100)

**GET /api/vulnerabilities**
```bash
curl "http://localhost:8000/api/vulnerabilities?search=CVE-2024&severity=HIGH&skip=0&limit=10"
```

Parameters:
- `search` - Search CVE ID/title/description
- `severity` - Filter by severity
- `status` - Filter by status
- `skip` - Pagination offset
- `limit` - Page size (max 100)

---

## 2. Email Notifications System

### Setup

#### 1. Configure SMTP in `.env`

For **Gmail**:
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password  # Use app-specific password
FROM_EMAIL=noreply@cybersecurity-tracker.com
```

For **SendGrid**:
```env
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=SG.your-sendgrid-api-key
FROM_EMAIL=noreply@cybersecurity-tracker.com
```

For **AWS SES**:
```env
SMTP_HOST=email-smtp.region.amazonaws.com
SMTP_PORT=587
SMTP_USER=your-ses-username
SMTP_PASSWORD=your-ses-password
FROM_EMAIL=noreply@cybersecurity-tracker.com
```

#### 2. Install Dependencies
```bash
pip install -r backend/requirements.txt
# Includes: aiosmtplib, httpx, slowapi
```

### Notification Types

#### New Incident Alert
Sent when a **new incident is created**.

**Recipients:** Users with `email_on_new_incident=True`

**Email Contains:**
- Incident title and severity
- Description
- Link to view in dashboard
- Formatted HTML email

**Trigger:**
```python
POST /api/incidents
{
  "title": "Unauthorized Access Detected",
  "description": "Admin account accessed from unusual location",
  "severity": "CRITICAL",
  "incident_type": "unauthorized_access"
}
```

#### Critical Vulnerability Alert
Sent when **CRITICAL or HIGH severity vulnerability** is created.

**Recipients:** Users with `email_on_critical_vulnerability=True`

**Email Contains:**
- CVE ID and CVSS score
- Severity level
- Affected systems
- Remediation info
- Link to vulnerability details

**Trigger:**
```python
POST /api/vulnerabilities
{
  "cve_id": "CVE-2024-1234",
  "title": "Remote Code Execution in OpenSSL",
  "severity": "CRITICAL",
  "cvss_score": 9.8,
  "affected_systems": ["web-server-1", "web-server-2"]
}
```

#### Incident Status Update
Sent when **assigned incident is updated**.

**Recipients:** Users with `email_on_incident_update=True`

**Email Contains:**
- Incident title
- Who updated it
- Status change details

### Email Service API

**Location:** `/backend/app/services/email_service.py`

```python
from app.services import email_service

# Send incident alert
await email_service.send_incident_alert(
    recipient_email="analyst@company.com",
    incident_title="Malware Detected",
    severity="HIGH",
    description="...",
    created_at=datetime.utcnow(),
    incident_id="123e4567-e89b-12d3-a456-426614174000"
)

# Send vulnerability alert
await email_service.send_vulnerability_alert(
    recipient_email="analyst@company.com",
    cve_id="CVE-2024-1234",
    title="RCE in OpenSSL",
    severity="CRITICAL",
    cvss_score=9.8,
    affected_systems=["web-server-1"],
    vulnerability_id="123e4567-e89b-12d3-a456-426614174000"
)

# Send incident update
await email_service.send_incident_update(
    recipient_email="analyst@company.com",
    incident_title="Malware Detected",
    old_status="INVESTIGATING",
    new_status="RESOLVED",
    updated_by="John Doe",
    incident_id="123e4567-e89b-12d3-a456-426614174000"
)
```

### User Notification Preferences

Users can control notifications in **Settings → Notifications**:

- ✅ Email on New Incident
- ✅ Critical Vulnerability Alerts
- ✅ Incident Updates
- ✅ Daily Digest

These preferences are stored in the `notification_preferences` table and checked before sending emails.

---

## 3. Webhook/Slack Integration

### Setup

#### 1. Create Webhook URL

Go to **Settings → Integrations → API & Integrations**

Click **"Manage Webhooks"** and create:

```bash
POST /api/integrations/webhooks
{
  "name": "Slack Security Channel",
  "url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
  "events": ["incident", "vulnerability", "all"]
}
```

#### 2. Get Slack Webhook URL

1. Go to Slack Workspace Settings
2. Create or select a channel (e.g., #security-alerts)
3. Go to **Integrations → Incoming Webhooks**
4. Click **"Add New Webhook to Workspace"**
5. Select channel and authorize
6. Copy the webhook URL: `https://hooks.slack.com/services/XXX/YYY/ZZZ`

### Webhook Events

#### 1. Incident Created/Updated

**Event:** `incident.created`

**Payload:**
```json
{
  "event": "incident.created",
  "timestamp": "2024-02-22T10:30:45.123456",
  "data": {
    "incident_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Unauthorized Access Detected",
    "severity": "CRITICAL",
    "description": "Admin account accessed from unusual location",
    "status": "OPEN",
    "dashboard_url": "https://cybersecurity-tracker.vercel.app/incidents?id=550e8400..."
  }
}
```

**Slack Message Preview:**
```
🚨 New Security Incident (CRITICAL)

Title: Unauthorized Access Detected
Severity: CRITICAL
Description: Admin account accessed from unusual location...

[View in Dashboard Button]
```

#### 2. Vulnerability Discovered

**Event:** `vulnerability.discovered`

**Payload:**
```json
{
  "event": "vulnerability.discovered",
  "timestamp": "2024-02-22T10:30:45.123456",
  "data": {
    "vulnerability_id": "550e8400-e29b-41d4-a716-446655440000",
    "cve_id": "CVE-2024-1234",
    "title": "Remote Code Execution in OpenSSL",
    "severity": "CRITICAL",
    "cvss_score": 9.8,
    "affected_systems": ["web-server-1", "web-server-2"],
    "dashboard_url": "https://cybersecurity-tracker.vercel.app/vulnerabilities?id=550e8400..."
  }
}
```

**Slack Message Preview:**
```
⚠️ New Vulnerability Alert (CRITICAL)

CVE ID: CVE-2024-1234
CVSS Score: 9.8/10.0
Title: Remote Code Execution in OpenSSL
Affected Systems: web-server-1, web-server-2

[View Details Button]
```

### Webhook Management

**Get all webhooks:**
```bash
GET /api/integrations/webhooks
```

**Create webhook:**
```bash
POST /api/integrations/webhooks
{
  "name": "Slack Security",
  "url": "https://hooks.slack.com/services/...",
  "events": ["incident", "vulnerability"]
}
```

**Update webhook:**
```bash
PUT /api/integrations/webhooks/{webhook_id}
{
  "name": "Updated Name",
  "is_active": true
}
```

**Delete webhook:**
```bash
DELETE /api/integrations/webhooks/{webhook_id}
```

### Supported Integrations

#### Slack
- Formatted messages with color indicators
- Interactive buttons to view in dashboard
- Support for severity-based colors

#### Microsoft Teams
- Adaptive cards with rich formatting
- Color-coded severity levels
- Action buttons

#### Generic Webhooks
- Standard JSON payloads
- Webhook retries on failure
- 5-second timeout per request

---

## Rate Limiting

All endpoints are protected with **rate limiting** using `slowapi`:

```
Default: 100 requests per minute per IP
Burst: Up to 200 per minute with caching
```

**Example Rate Limit Response:**
```json
{
  "error": "Rate limit exceeded",
  "detail": "100 per 1 minute"
}
```

To adjust, edit `/backend/main.py`:
```python
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per minute"]  # Customize here
)
```

---

## API Documentation

### Test the API

**Swagger UI:**
```
http://localhost:8000/docs
```

**ReDoc:**
```
http://localhost:8000/redoc
```

### Example Requests

#### Search Incidents
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/incidents?search=malware&severity=CRITICAL&skip=0&limit=10"
```

#### Create Incident (triggers email)
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Security Breach",
    "description": "Unauthorized access detected",
    "severity": "CRITICAL",
    "incident_type": "unauthorized_access"
  }' \
  http://localhost:8000/api/incidents
```

#### Create Critical Vulnerability (triggers email + webhook)
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "cve_id": "CVE-2024-1234",
    "title": "Remote Code Execution",
    "severity": "CRITICAL",
    "cvss_score": 9.8,
    "affected_systems": ["web-server"]
  }' \
  http://localhost:8000/api/vulnerabilities
```

---

## Deployment Notes

### Environment Variables Required

**Production `.env`:**
```env
DATABASE_URL=postgresql://user:pass@host/db
SECRET_KEY=your-secure-random-key
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@cybersecurity-tracker.com
CORS_ORIGINS=["https://cybersecurity-tracker.vercel.app"]
ENVIRONMENT=production
```

### Render Deployment

1. Go to **Render Dashboard**
2. Select your **Cybersecurity Tracker** service
3. Go to **Environment**
4. Add/update the env variables above
5. Deploy

### Testing

```bash
# Backend test
curl http://localhost:8000/health

# Check email config (disabled if no SMTP_USER)
tail -f backend/logs/  # Check logs for email send status
```

---

## Troubleshooting

### Emails not sending?

1. Check logs: `docker logs backend`
2. Verify SMTP credentials in `.env`
3. For Gmail: Use [app-specific password](https://myaccount.google.com/apppasswords)
4. Check firewall allows port 587 (SMTP)

### Webhooks not triggering?

1. Verify webhook URL in Settings → Integrations
2. Check webhook is marked as `is_active = true`
3. Look at logs for webhook errors
4. Slack webhook URL format: `https://hooks.slack.com/services/...`

### Rate limit errors?

Adjust `limiter` in `/backend/main.py` or implement API key-based limits.

---

## Next Steps (Priority 2)

- [ ] Reports & PDF export
- [ ] Audit logs page
- [ ] Advanced caching (Redis)
- [ ] Dark mode toggle
- [ ] Bulk actions on incidents/vulnerabilities
- [ ] 2FA authentication
- [ ] API key management UI

---

**Last Updated:** February 22, 2024
**Status:** Production Ready
