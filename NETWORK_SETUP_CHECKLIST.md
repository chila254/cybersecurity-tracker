# Network Monitoring Setup Checklist

## Pre-Deployment (LEGAL & COMPLIANCE)

- [ ] **Get Written Consent**
  - Employees acknowledge network monitoring
  - Signed agreement on file
  - Policy distributed and acknowledged

- [ ] **Privacy Policy Updated**
  - Document what's being monitored
  - Explain data retention period
  - State compliance with GDPR/CCPA
  - Publish to employees

- [ ] **Data Retention Policy Defined**
  - DNS logs: Keep for __ days (recommend 90)
  - Device data: Keep for __ days (recommend 30)
  - Audit logs: Keep for __ days (recommend 365)
  - Auto-delete old data

- [ ] **Access Control Established**
  - Only IT/Security admins can view data
  - Restrict to ADMIN role only
  - Document who has access
  - Regular access reviews

- [ ] **Legal Review Completed**
  - Legal team reviewed feature
  - Compliance with employment laws verified
  - HR approval obtained
  - Documented in compliance file

## Database Setup

- [ ] **Run Migration Script**
  ```bash
  psql $DATABASE_URL < scripts/02_network_monitoring.sql
  ```
  
- [ ] **Verify Tables Created**
  ```bash
  psql $DATABASE_URL -c "\dt" | grep -E "connected_devices|dns_logs|site_categories|wifi_configs|network_policies"
  ```
  Should show 5 tables

- [ ] **Check Indexes**
  ```bash
  psql $DATABASE_URL -c "\di" | grep idx_
  ```
  Should show 12+ indexes

- [ ] **Test Connectivity**
  ```bash
  psql $DATABASE_URL -c "SELECT COUNT(*) FROM connected_devices;"
  ```
  Should return 0 (no errors)

## Backend Setup

- [ ] **Verify Dependencies Installed**
  ```bash
  python -c "import httpx; print(httpx.__version__)"
  ```
  httpx==0.28.0 should be installed

- [ ] **Test Backend Routes**
  ```bash
  curl -H "Authorization: Bearer $TOKEN" \
    http://localhost:8000/api/network/stats
  ```
  Should return valid JSON or 404 (config not yet)

- [ ] **Check API Documentation**
  - Go to http://localhost:8000/docs
  - Look for `/api/network` section
  - Should show 14 new endpoints

## Frontend Setup

- [ ] **Network Pages Accessible**
  - [ ] `/network` - Dashboard loads
  - [ ] `/network/settings` - Settings form loads
  - [ ] Sidebar shows "🌐 Network Monitor" link

- [ ] **UI Components Render**
  - [ ] Stats cards display
  - [ ] Device table shows (or "Sync Now" message)
  - [ ] Form fields are editable

## WiFi Router Configuration

### Step 1: Ubiquiti UniFi
- [ ] Get controller IP (usually https://192.168.1.1:8443)
- [ ] Create/get admin credentials
- [ ] Test SSH access
  ```bash
  ssh admin@192.168.1.1
  ```
- [ ] Go to `/network/settings`
  - [ ] Select "Ubiquiti UniFi"
  - [ ] Enter URL: https://192.168.1.1:8443
  - [ ] Enter username
  - [ ] Enter password
  - [ ] Click "Save Configuration"

### Step 2: Cisco Meraki
- [ ] Log in to Meraki dashboard
- [ ] Generate API key (Organization → API keys)
- [ ] Note the API key
- [ ] Go to `/network/settings`
  - [ ] Select "Cisco Meraki"
  - [ ] Enter Meraki API URL
  - [ ] Enter API key as password
  - [ ] Click "Save Configuration"

### Step 3: TP-Link
- [ ] Get router IP (usually http://192.168.1.1)
- [ ] Enable SSH/API access in settings
- [ ] Create/get admin credentials
- [ ] Go to `/network/settings`
  - [ ] Select "TP-Link"
  - [ ] Enter URL: http://192.168.1.1
  - [ ] Enter username
  - [ ] Enter password
  - [ ] Click "Save Configuration"

### Step 4: Mikrotik
- [ ] Get RouterOS IP address
- [ ] Enable REST API (System → Packages)
- [ ] Create API token
- [ ] Go to `/network/settings`
  - [ ] Select "Mikrotik RouterOS"
  - [ ] Enter API URL: http://192.168.1.1:8728
  - [ ] Enter username
  - [ ] Enter token as password
  - [ ] Click "Save Configuration"

## Device Sync

- [ ] **Sync Connected Devices**
  - Go to `/network`
  - Click "🔄 Sync Now" button
  - Wait for sync to complete
  - Should show "Devices synced successfully"

- [ ] **Verify Devices Appear**
  - Go to `/network`
  - Check "Connected Devices" table
  - Should see at least 1 device
  - Check device names, MACs, IPs appear

- [ ] **Test Device History**
  - Click "View History" on a device
  - Go to `/network/device/{device_id}`
  - Should load device details
  - May show "No DNS data available" (that's ok for now)

## Network Policies

- [ ] **Create Test Policy**
  - Go to `/network/settings`
  - Scroll to "Create New Policy"
  - Name: "Test Policy"
  - Block: Check "Adult Content"
  - Click "Create Policy"

- [ ] **Verify Policy Created**
  - Should show in policy list
  - Shows as "Active"
  - Can delete if needed

- [ ] **Test Policy Enforcement** (optional)
  - Create policy blocking "social"
  - Try accessing facebook.com
  - Should be blocked (if using pfSense/Cloudflare)

## DNS Logs (Optional but Recommended)

- [ ] **Configure DNS Source** (in `/network/settings`)
  - [ ] Cloudflare: Add API key
  - [ ] Quad9: Set to "local"
  - [ ] Local: Enable on router

- [ ] **Wait for DNS Data**
  - Wait 5-10 minutes
  - Devices should generate DNS queries
  - Go to `/network` → "Top Domains"
  - Should see websites visited

- [ ] **View Device History**
  - Click device → "View History"
  - Should show DNS queries
  - Click category filters
  - Verify categorization works

## Monitoring & Testing

- [ ] **Test Search Functionality**
  - Go to `/network/dns-logs`
  - Search for domain: google.com
  - Should return results
  - Filter by category: work
  - Filter by blocked: false

- [ ] **Verify Statistics**
  - Go to `/network`
  - Check stats cards
  - Total devices > 0
  - DNS queries > 0 (if waited for data)

- [ ] **Test Pagination**
  - DNS logs page
  - Change limit to 10
  - Click through pages
  - All data loads correctly

- [ ] **Check Device Type Detection**
  - Look at device types
  - Should show: laptop, phone, tablet, or unknown
  - Verify accuracy for known devices

## Security Hardening

- [ ] **Restrict Access**
  - Only ADMIN role can access /network
  - Verify ANALYST role cannot access
  - Verify VIEWER role cannot access

- [ ] **Enable HTTPS**
  - Vercel: Automatic (done)
  - Render: Enable SSL certificate
  - Database: Use SSL connections

- [ ] **Encrypt Sensitive Data**
  - [ ] Router passwords encrypted at rest
  - [ ] API keys encrypted at rest
  - [ ] Use environment variables for secrets
  - [ ] Never log passwords/keys

- [ ] **Regular Backups**
  - Verify Supabase auto-backup enabled
  - Test backup restore procedure
  - Document retention period

## Monitoring & Alerts

- [ ] **Set Up Logging**
  - Check Render logs for errors
  - Monitor database query performance
  - Alert on sync failures

- [ ] **Create Dashboard Alerts**
  - Alert if sync fails 2x in a row
  - Alert if unusual device count change
  - Alert if high-risk domain accessed

- [ ] **Monitor Performance**
  - Check response times: < 1s for device list
  - Check sync time: < 2 minutes
  - Check database size: Growth is normal

## Compliance & Auditing

- [ ] **Audit Logging**
  - Verify audit logs record:
    - [ ] Policy creation/deletion
    - [ ] Config changes
    - [ ] Admin views of logs

- [ ] **Data Export**
  - [ ] Can export device list as CSV
  - [ ] Can export DNS logs as CSV
  - [ ] Reports include compliance data

- [ ] **Retention Enforcement**
  - [ ] Old DNS logs auto-deleted after 90 days
  - [ ] Device history cleared after 30 days
  - [ ] Verify deletion happening

- [ ] **GDPR/CCPA Compliance**
  - [ ] Can identify devices by user
  - [ ] Can export user data
  - [ ] Can delete user data
  - [ ] Privacy notices are clear

## Deployment

### Development
- [ ] All checks pass locally
- [ ] No errors in logs
- [ ] All tests passing
- [ ] Documentation reviewed

### Staging (if applicable)
- [ ] Deploy to staging environment
- [ ] Run full test suite
- [ ] Test with real router (if possible)
- [ ] Get stakeholder approval

### Production
- [ ] Final legal/compliance review
- [ ] Employee communications sent
- [ ] Monitoring alerts configured
- [ ] On-call team briefed
- [ ] Rollback plan documented
- [ ] Deploy to production
- [ ] Monitor for 24 hours
- [ ] Get final sign-off

## Post-Deployment

- [ ] **Monitor First 24 Hours**
  - Check error logs
  - Verify sync working
  - Check performance metrics
  - Monitor database growth

- [ ] **Gather Feedback**
  - From IT team: Issues?
  - From security: Data quality?
  - From compliance: Any gaps?
  - From users: Any concerns?

- [ ] **Document Setup**
  - Record router configurations
  - Document API keys (encrypted)
  - Document admin procedures
  - Create runbook for on-call

- [ ] **Train Team**
  - IT team: How to use dashboard
  - Security: How to analyze data
  - Admins: How to manage policies
  - Compliance: How to audit logs

## Troubleshooting Guide

| Issue | Solution |
|-------|----------|
| Sync fails | Check router credentials, firewall, API access |
| No devices shown | Click "Sync Now", wait 30 seconds, refresh |
| DNS logs empty | Wait 5 min for queries, check DNS source config |
| Policies not blocking | Verify DNS source is configured, firewall enabled |
| Slow performance | Check database indexes, limit query range |
| Access denied errors | Verify user is ADMIN role, JWT token valid |

## Sign-Off

- [ ] **Development Team**
  - Name: ________________
  - Date: ________________
  - Signature: ________________

- [ ] **Security Team**
  - Name: ________________
  - Date: ________________
  - Signature: ________________

- [ ] **Compliance/Legal**
  - Name: ________________
  - Date: ________________
  - Signature: ________________

- [ ] **Management Approval**
  - Name: ________________
  - Date: ________________
  - Signature: ________________

---

## Quick Start (Summary)

1. Run migration: `psql $DATABASE_URL < scripts/02_network_monitoring.sql`
2. Configure router: `/network/settings`
3. Sync devices: `/network` → "Sync Now"
4. View devices: `/network` dashboard
5. Check history: `/network/device/{id}`
6. Create policies: `/network/settings` → Create Policy

**⏱️ Estimated Setup Time:** 30 minutes

**⚠️ Legal Review:** Required before production deployment

---

**Last Updated:** 2024-02-22
**Version:** 1.0.0
