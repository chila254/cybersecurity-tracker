# Network Monitoring Feature Guide

## Overview

The Network Monitoring feature allows you to:
- **Track WiFi connected devices** - See who's on your network
- **Monitor DNS queries** - View websites visited by each device
- **Categorize websites** - Automatically categorize websites (social, streaming, work, etc.)
- **Block dangerous sites** - Define network policies to block malicious domains
- **Generate reports** - Analyze network usage patterns

## ⚠️ Important: Legal & Privacy Compliance

**BEFORE DEPLOYING THIS FEATURE:**

1. **Get Written Consent** - Employees must explicitly agree to network monitoring
2. **Have a Monitoring Policy** - Document your monitoring practices
3. **Comply with Laws** - Follow GDPR, CCPA, and local data protection laws
4. **Provide Transparency** - Employees should know they're being monitored
5. **Limited Retention** - Don't keep logs longer than necessary
6. **Restrict Access** - Only admins/security team can view data

### Recommended Privacy Policy Statement

```
"This organization monitors network traffic for security and compliance purposes.
This includes tracking device connections and DNS queries. All monitoring is subject
to applicable privacy laws and company policies. Employee consent is required."
```

## Setup Guide

### Step 1: Install Dependencies

All dependencies are already in `requirements.txt`:
- `httpx==0.28.0` - Async HTTP client for router APIs

### Step 2: Create Database Tables

Run the migration script:

```bash
# Connect to your PostgreSQL database
psql $DATABASE_URL < scripts/02_network_monitoring.sql
```

This creates:
- `connected_devices` - WiFi device tracking
- `dns_logs` - Website visit history
- `site_categories` - Domain categorization
- `wifi_configs` - Router configuration
- `network_policies` - Access control rules

### Step 3: Configure WiFi Router

Go to Network Settings (`/network/settings`):

#### **Ubiquiti UniFi**
1. Get your UniFi controller IP (usually `https://192.168.1.1:8443`)
2. Create an admin account or use existing one
3. Enter URL: `https://192.168.1.1:8443`
4. Enter username and password
5. Click Save

#### **Cisco Meraki**
1. Log in to Meraki dashboard
2. Go to Organization → API keys
3. Create a new API key
4. Use API key as "password"
5. Enter network API URL
6. Click Save

#### **TP-Link**
1. Get your TP-Link router IP (usually `192.168.1.1`)
2. Enable SSH/API access
3. Enter URL: `http://192.168.1.1`
4. Enter username and password
5. Click Save

#### **Mikrotik RouterOS**
1. Get your Mikrotik IP address
2. Enable REST API (System → Packages)
3. Create API token
4. Enter URL: `http://192.168.1.1:8728`
5. Use token as password
6. Click Save

### Step 4: Sync Devices

Click "🔄 Sync Now" on the Network Monitoring dashboard:

```
GET /api/network/wifi-config/sync
```

This will:
1. Connect to your router
2. Fetch all connected devices
3. Store them in the database
4. Update the last sync time

## Features

### 1. Connected Devices List

**Endpoint:**
```
GET /api/network/devices?skip=0&limit=50
```

**Shows:**
- Device name
- MAC address
- IP address
- Device type (laptop, phone, tablet, IoT)
- Connection time
- Data usage
- Signal strength
- Online/Offline status

**UI:** `/network`

### 2. Device History

**Endpoint:**
```
GET /api/network/devices/{device_id}/dns-history?limit=200
```

**Shows:**
- All websites visited by the device
- Domain category (social, streaming, work, etc.)
- Query timestamp
- Blocked/Allowed status
- DNS response code

**UI:** `/network/device/{device_id}`

### 3. DNS Query Logs

**Endpoint:**
```
GET /api/network/dns-logs?skip=0&limit=100&days=7
```

**Filters:**
- `mac_address` - Filter by device
- `domain` - Search specific domain
- `category` - Filter by category
- `is_blocked` - Show blocked only
- `days` - Time range (default: 7 days)

**Category Taxonomy:**
```
- social      : Facebook, Twitter, Instagram, TikTok, etc.
- streaming   : YouTube, Netflix, Twitch, Hulu, etc.
- work        : GitHub, Slack, Notion, Jira, Zoom, etc.
- news        : BBC, CNN, Reuters, NYT, etc.
- shopping    : Amazon, eBay, Etsy, Walmart, etc.
- gambling    : Bet365, PokerStars, Casino, etc.
- adult       : Adult content
- malware     : Known malicious/phishing sites
- unknown     : Unclassified
```

### 4. Network Analytics

**Endpoint:**
```
GET /api/network/stats
```

**Returns:**
- Total devices
- Online devices
- Total DNS queries
- Blocked queries
- Top 10 domains
- Category distribution
- Device type distribution

**Visualization:**
- Stats cards showing key metrics
- Top domains table
- Category breakdown pie chart

### 5. Network Policies

**Create Policy:**
```
POST /api/network/policies
{
  "name": "Block Adult Content",
  "description": "Blocks adult websites",
  "block_categories": ["adult", "gambling"],
  "blocked_domains": ["example-adult.com"]
}
```

**List Policies:**
```
GET /api/network/policies
```

**Update Policy:**
```
PUT /api/network/policies/{policy_id}
```

**Delete Policy:**
```
DELETE /api/network/policies/{policy_id}
```

**Enforcement:**
- Blocked queries get `is_blocked = true` in DNS logs
- Generates alerts for policy violations
- Optionally integrate with DNS sinkhole

## API Reference

### WiFi Configuration

**GET /api/network/wifi-config**
Get current WiFi configuration

**POST /api/network/wifi-config**
Create or update WiFi configuration

```json
{
  "router_type": "unifi",
  "router_url": "https://192.168.1.1:8443",
  "router_username": "admin",
  "router_password": "password",
  "dns_log_source": "cloudflare",
  "dns_log_url": "https://...",
  "dns_api_key": "..."
}
```

**POST /api/network/wifi-config/sync**
Sync devices from router

### Connected Devices

**GET /api/network/devices**
List connected devices

Query parameters:
- `is_online` (bool) - Filter by status
- `device_type` (string) - Filter by type
- `skip` (int) - Pagination offset
- `limit` (int) - Results per page (max 100)

**GET /api/network/devices/{device_id}**
Get device details

**GET /api/network/devices/{device_id}/dns-history**
Get device's DNS query history

### DNS Logs

**GET /api/network/dns-logs**
List all DNS queries

Query parameters:
- `mac_address` - Filter by device
- `domain` - Search domain
- `category` - Filter by category
- `is_blocked` - Filter blocked queries
- `skip` - Pagination
- `limit` - Results per page
- `days` - Time range in days

**GET /api/network/dns-logs/blocked**
List blocked queries only

**POST /api/network/dns-logs/import**
Import DNS logs in bulk

```json
[
  {
    "mac_address": "AA:BB:CC:DD:EE:FF",
    "domain": "example.com",
    "timestamp": "2024-02-22T10:30:00Z",
    "is_blocked": false
  }
]
```

### Statistics

**GET /api/network/stats**
Get network analytics

Returns:
```json
{
  "total_devices": 25,
  "online_devices": 18,
  "total_dns_queries": 5234,
  "blocked_queries": 12,
  "top_domains": [
    {
      "domain": "google.com",
      "count": 234,
      "category": "work"
    }
  ],
  "top_categories": [
    {
      "category": "work",
      "count": 2100
    }
  ],
  "device_types": {
    "laptop": 10,
    "phone": 8,
    "tablet": 2
  }
}
```

## Frontend Pages

### Network Dashboard
**Path:** `/network`

**Features:**
- Key metrics (devices, queries, blocked)
- Connected devices table
- Top domains list
- Sync devices button
- Link to device history

### Device History
**Path:** `/network/device/{device_id}`

**Features:**
- Device information
- DNS query history (timestamped)
- Category filter
- Blocked vs. allowed stats
- Export DNS log option

### Network Settings
**Path:** `/network/settings`

**Features:**
- WiFi router configuration form
- Network policy creation
- Policy management (enable/disable)
- Configuration guide

## Database Schema

### connected_devices
```sql
- id (UUID)
- org_id (UUID) - Organization
- mac_address (VARCHAR) - Device identifier
- ip_address (VARCHAR)
- device_name (VARCHAR)
- device_type (VARCHAR) - laptop, phone, tablet, iot
- user_name (VARCHAR) - Owner name if available
- manufacturer (VARCHAR) - OUI/Vendor
- connected_at (TIMESTAMP)
- disconnected_at (TIMESTAMP)
- data_sent_bytes (VARCHAR)
- data_received_bytes (VARCHAR)
- signal_strength (INTEGER) - dBm
- is_online (BOOLEAN)
- router_model (VARCHAR) - Source router
- created_at, updated_at
```

### dns_logs
```sql
- id (UUID)
- org_id (UUID)
- device_id (UUID) - Reference to device
- mac_address (VARCHAR)
- domain (VARCHAR) - Website queried
- domain_category (VARCHAR) - Auto-categorized
- query_type (VARCHAR) - A, AAAA, MX, etc
- response_code (VARCHAR) - NOERROR, BLOCKED
- is_blocked (BOOLEAN)
- timestamp (TIMESTAMP)
- created_at
```

### site_categories
```sql
- id (UUID)
- domain (VARCHAR) - Unique
- category (VARCHAR)
- risk_level (VARCHAR) - low, medium, high
- is_blocked (BOOLEAN)
- created_at, updated_at
```

### wifi_configs
```sql
- id (UUID)
- org_id (UUID) - Unique
- router_type (VARCHAR)
- router_url (VARCHAR)
- router_username (VARCHAR)
- router_password (VARCHAR) - Encrypted
- dns_log_source (VARCHAR)
- dns_log_url (VARCHAR)
- dns_api_key (VARCHAR) - Encrypted
- is_enabled (BOOLEAN)
- last_sync_at (TIMESTAMP)
- created_at, updated_at
```

### network_policies
```sql
- id (UUID)
- org_id (UUID)
- name (VARCHAR)
- description (TEXT)
- block_categories (ARRAY)
- allow_categories (ARRAY)
- blocked_domains (ARRAY)
- allowed_domains (ARRAY)
- is_active (BOOLEAN)
- created_at, updated_at
```

## Service Classes

### WiFiService
Located in `app/services/wifi_service.py`

**Supported Routers:**
- `unifi` - Ubiquiti UniFi
- `meraki` - Cisco Meraki
- `tp_link` - TP-Link
- `mikrotik` - Mikrotik RouterOS

**Methods:**
- `get_connected_devices()` - Fetch devices from router
- `save_devices_to_db()` - Store devices in database
- Device type detection
- Manufacturer lookup from MAC

### DNSService
Located in `app/services/dns_service.py`

**Methods:**
- `categorize_domain()` - Auto-categorize website
- `add_dns_log()` - Record DNS query
- `import_dns_logs()` - Bulk import
- `get_user_dns_history()` - Query device history
- `get_blocked_queries()` - Query blocked sites
- `get_top_domains()` - Analytics
- `get_category_distribution()` - Analytics
- `get_high_risk_domains()` - Security alerts
- `sync_categories()` - Load category database

## Troubleshooting

### Router Connection Fails
- ✅ Check router URL is correct and accessible
- ✅ Verify username/password are correct
- ✅ Ensure SSH/API access is enabled on router
- ✅ Check firewall allows connections to router

### DNS Logs Not Appearing
- ✅ Wait a few minutes for queries to be logged
- ✅ Verify devices are actively browsing
- ✅ Check network policy isn't blocking all queries
- ✅ Verify DNS source is configured (local router)

### Categories Not Showing
- ✅ Custom categories are loaded from `DOMAIN_CATEGORIES` dict
- ✅ Add more domains to categorize them
- ✅ Unknown domains appear as "unknown" category
- ✅ Risk levels are auto-assigned per category

### Database Errors
- ✅ Run migration: `psql $DATABASE_URL < scripts/02_network_monitoring.sql`
- ✅ Check all indexes were created
- ✅ Verify org_id references are valid

## Performance Notes

**Optimization:**
- Indexes on `mac_address`, `domain`, `timestamp` for fast queries
- Device syncs are asynchronous (doesn't block API)
- DNS imports support bulk operations
- Pagination limits prevent loading entire datasets

**Scaling:**
- For large networks (>500 devices):
  - Archive old DNS logs monthly
  - Use time-series database (InfluxDB) for metrics
  - Implement caching layer (Redis)
  - Add data retention policies

## Integration Examples

### Slack Alerts for High-Risk Activity
```python
if category in ["malware", "adult", "gambling"]:
    await send_slack_alert(
        f"Device {device_name} attempted to access {domain} ({category})"
    )
```

### Auto-Block Malware
```python
if category == "malware":
    dns_log.is_blocked = True
    # Trigger firewall rule to block
```

### Daily Summary Report
```python
# Get yesterday's stats
stats = get_network_stats(org_id, days=1)
send_email_report(org_id, stats)
```

### SIEM Integration
```python
# Export DNS logs to Splunk/ELK
export_to_siem(
    dns_logs=get_dns_logs(org_id, days=7),
    format="json",
    endpoint="https://splunk.example.com"
)
```

## Security Considerations

1. **Encryption**
   - Router password stored encrypted at rest (use `cryptography` library)
   - API keys stored encrypted at rest
   - DNS logs transmitted over HTTPS only

2. **Access Control**
   - Only ADMIN role can view network monitoring
   - Only org admins can configure WiFi
   - Read-only access for ANALYST role

3. **Data Retention**
   - DNS logs auto-deleted after 90 days (configurable)
   - Device history kept for 30 days
   - Audit log all network policy changes

4. **Network Isolation**
   - Separate database user for network monitoring
   - Restrict API endpoints to authenticated users
   - Rate limit DNS log imports

## Next Steps

1. ✅ Deploy database migration
2. ✅ Configure your WiFi router
3. ✅ Click "Sync Now" to discover devices
4. ✅ Review device history
5. ✅ Create network policies
6. ✅ Monitor for policy violations
7. ✅ Generate reports

## Support & Resources

- API Documentation: `/api/docs` (Swagger UI)
- Database Schema: `scripts/02_network_monitoring.sql`
- Service Code: `backend/app/services/`
- Routes: `backend/app/routes/network.py`
- Frontend: `app/network/`

---

**⚠️ Remember:** This is a powerful feature. Use responsibly and legally.
