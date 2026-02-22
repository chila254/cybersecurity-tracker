# Deployment Checklist - Priority 1 Features

## Backend Deployment (Render)

### Step 1: Update Dependencies
- [x] Added `httpx==0.28.0` for async HTTP requests
- [x] Added `slowapi==0.1.9` for rate limiting
- [x] Kept `aiosmtplib==3.0.2` for email

**Action:** Push `backend/requirements.txt` changes

```bash
git add backend/requirements.txt
git commit -m "Add new dependencies for webhooks and rate limiting"
git push
```

### Step 2: Configure Email (SMTP)

Go to **Render Dashboard** → Your Backend Service → **Environment**

Add these variables:
```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@cybersecurity-tracker.com
```

**For Gmail Users:**
1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable "2-Step Verification" (if not already)
3. Generate [App Password](https://myaccount.google.com/apppasswords)
4. Use the 16-character password in `SMTP_PASSWORD`

**For SendGrid Users:**
1. Get API key from SendGrid dashboard
2. Set `SMTP_USER=apikey`
3. Set `SMTP_PASSWORD=SG.your-api-key`

### Step 3: Update CORS Origins
Make sure `CORS_ORIGINS` includes your frontend:
```
CORS_ORIGINS=["https://cybersecurity-tracker.vercel.app","http://localhost:3000"]
```

### Step 4: Deploy
- Go to **Render Dashboard**
- Click **Manual Deploy** on your backend service
- Or: Push to main branch and let auto-deploy handle it

**Verify Deployment:**
```bash
# Health check
curl https://your-render-url.onrender.com/health

# API docs
https://your-render-url.onrender.com/docs
```

---

## Frontend Deployment (Vercel)

### Step 1: Verify API Configuration
Make sure `.env.local` or Vercel env variables have:
```
NEXT_PUBLIC_API_URL=https://your-render-backend-url/api
```

### Step 2: Push Frontend Changes
```bash
git add app/incidents/page.tsx
git add app/vulnerabilities/page.tsx
git commit -m "Add search, filters, and pagination"
git push
```

Vercel will auto-deploy on push.

### Step 3: Test Features
Visit your deployed site:
- Search bar on incidents/vulnerabilities pages
- Filters (Status, Severity, Type)
- Pagination controls
- Create incident/vulnerability (should send email + webhook)

---

## Database (Supabase)

### Verify Tables Exist
Supabase should already have these tables:

- ✅ `organizations`
- ✅ `users`
- ✅ `incidents`
- ✅ `vulnerabilities`
- ✅ `comments`
- ✅ `audit_logs`
- ✅ `notification_preferences`
- ✅ `webhooks`
- ✅ `alerts`
- ✅ `api_keys`

**If tables are missing:**
1. Go to Supabase Dashboard
2. Run the SQL from `/scripts/01_init_schema.sql`

---

## Testing & Verification

### Test Email Notifications

1. **Create Test Incident:**
   ```bash
   curl -X POST \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "Test Security Incident",
       "description": "This is a test",
       "severity": "CRITICAL",
       "incident_type": "other"
     }' \
     https://your-backend-url/api/incidents
   ```

2. **Check Email:** Look in your inbox for incident alert email

3. **Create Test Vulnerability:**
   ```bash
   curl -X POST \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "cve_id": "CVE-2024-TEST",
       "title": "Test Vulnerability",
       "severity": "HIGH",
       "cvss_score": 8.5
     }' \
     https://your-backend-url/api/vulnerabilities
   ```

4. **Check Email:** Should receive vulnerability alert

### Test Search & Pagination

1. Go to Incidents page
2. Type in search box → Should filter results
3. Use dropdowns to filter by status/severity
4. Click pagination buttons
5. Create multiple incidents to test pagination

### Test Webhooks

1. Create webhook in **Settings → Integrations**
2. Use [webhook.site](https://webhook.site) for testing:
   - Click "Create New"
   - Copy your unique URL
   - Add to webhook in settings
3. Create incident/vulnerability
4. Check webhook.site for received payload

---

## Troubleshooting

### Emails not sending?
- [ ] Check SMTP credentials in Render env
- [ ] Verify from Gmail app password is correct
- [ ] Check Render logs: `Logs` tab
- [ ] Verify `email_on_new_incident=true` for user

### Search not working?
- [ ] Verify API includes `?search=` parameter
- [ ] Check browser DevTools → Network tab
- [ ] Verify backend is responding with results

### Pagination not working?
- [ ] Check `skip` and `limit` parameters
- [ ] Verify results count < page size
- [ ] Clear browser cache

### Webhooks failing?
- [ ] Verify webhook URL is accessible (test with curl)
- [ ] Check webhook is `is_active=true`
- [ ] Verify JSON payload format
- [ ] Check firewall allows outbound HTTPS

---

## Monitoring

### Backend Health
```bash
# Check every 5 minutes
curl https://your-backend-url/health
```

### Email Success Rate
Check logs for failures:
```
grep "Email sent to" logs/  # Success
grep "Failed to send email" logs/  # Failures
```

### Webhook Status
View in database:
```sql
SELECT * FROM webhooks WHERE org_id = 'your-org-id';
```

---

## Rollback Plan

If something breaks:

### Revert Backend
```bash
git revert HEAD
git push
# Render will auto-deploy previous version
```

### Revert Frontend
```bash
git revert HEAD
git push
# Vercel will auto-deploy previous version
```

---

## Completed Tasks ✅

- [x] Email notification service (`/backend/app/services/email_service.py`)
- [x] Webhook service (`/backend/app/services/webhook_service.py`)
- [x] Search functionality (incidents + vulnerabilities)
- [x] Pagination controls (frontend)
- [x] Filter enhancements (incident type, etc.)
- [x] Rate limiting middleware
- [x] Frontend UI updates (search bar, filters)
- [x] Documentation (PRIORITY_1_FEATURES.md)

---

## Still TODO (Priority 2)

- [ ] Reports & PDF export
- [ ] Audit logs viewing interface
- [ ] Email digest (daily/weekly summary)
- [ ] Advanced webhook filtering
- [ ] Slack app integration (native)
- [ ] Jira integration

---

**Deployment Status:** 🟢 Ready for Production

Push changes and deploy!
