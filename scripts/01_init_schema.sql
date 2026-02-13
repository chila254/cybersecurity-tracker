-- Cybersecurity Incident Tracker Database Schema
-- PostgreSQL setup with Row-Level Security for multi-tenant isolation

-- ============================================================================
-- 1. ORGANIZATIONS (Multi-tenant base)
-- ============================================================================
CREATE TABLE IF NOT EXISTS organizations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  description TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- 2. USERS (with role-based access)
-- ============================================================================
CREATE TYPE user_role AS ENUM ('ADMIN', 'ANALYST', 'VIEWER');

CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  email VARCHAR(255) NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  name VARCHAR(255) NOT NULL,
  role user_role DEFAULT 'VIEWER',
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(org_id, email)
);

-- ============================================================================
-- 3. INCIDENTS (core security incidents)
-- ============================================================================
CREATE TYPE incident_severity AS ENUM ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW');
CREATE TYPE incident_status AS ENUM ('OPEN', 'INVESTIGATING', 'RESOLVED', 'CLOSED');
CREATE TYPE incident_type AS ENUM (
  'data_breach',
  'malware',
  'unauthorized_access',
  'denial_of_service',
  'social_engineering',
  'configuration_error',
  'supply_chain',
  'other'
);

CREATE TABLE IF NOT EXISTS incidents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  title VARCHAR(500) NOT NULL,
  description TEXT NOT NULL,
  severity incident_severity DEFAULT 'MEDIUM',
  status incident_status DEFAULT 'OPEN',
  incident_type incident_type DEFAULT 'other',
  created_by UUID NOT NULL REFERENCES users(id),
  assigned_to UUID REFERENCES users(id),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  resolved_at TIMESTAMP WITH TIME ZONE,
  affected_systems TEXT[],
  external_reference_id VARCHAR(255),
  INDEX idx_org_id (org_id),
  INDEX idx_status (status),
  INDEX idx_severity (severity),
  INDEX idx_created_at (created_at DESC)
);

-- ============================================================================
-- 4. VULNERABILITIES (CVE tracking)
-- ============================================================================
CREATE TYPE vuln_severity AS ENUM ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO');
CREATE TYPE vuln_status AS ENUM ('UNPATCHED', 'PATCHED', 'MITIGATED', 'MONITORING');

CREATE TABLE IF NOT EXISTS vulnerabilities (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  cve_id VARCHAR(50) UNIQUE,
  title VARCHAR(500) NOT NULL,
  description TEXT,
  cvss_score DECIMAL(3, 1),
  cvss_vector VARCHAR(255),
  severity vuln_severity DEFAULT 'MEDIUM',
  status vuln_status DEFAULT 'UNPATCHED',
  source VARCHAR(50) DEFAULT 'manual',
  affected_systems TEXT[],
  remediation TEXT,
  discovered_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  patch_available_date TIMESTAMP WITH TIME ZONE,
  patched_date TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  created_by UUID REFERENCES users(id),
  INDEX idx_org_id (org_id),
  INDEX idx_cve_id (cve_id),
  INDEX idx_status (status),
  INDEX idx_severity (severity)
);

-- ============================================================================
-- 5. INCIDENT-VULNERABILITY RELATIONS (many-to-many)
-- ============================================================================
CREATE TABLE IF NOT EXISTS incident_vulnerabilities (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  incident_id UUID NOT NULL REFERENCES incidents(id) ON DELETE CASCADE,
  vulnerability_id UUID NOT NULL REFERENCES vulnerabilities(id) ON DELETE CASCADE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(incident_id, vulnerability_id)
);

-- ============================================================================
-- 6. COMMENTS/TIMELINE (team collaboration)
-- ============================================================================
CREATE TABLE IF NOT EXISTS comments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  incident_id UUID NOT NULL REFERENCES incidents(id) ON DELETE CASCADE,
  author_id UUID NOT NULL REFERENCES users(id),
  content TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  INDEX idx_incident_id (incident_id),
  INDEX idx_created_at (created_at DESC)
);

-- ============================================================================
-- 7. ALERTS & NOTIFICATIONS
-- ============================================================================
CREATE TYPE alert_type AS ENUM ('email', 'webhook', 'in_app');
CREATE TYPE alert_status AS ENUM ('pending', 'sent', 'failed');

CREATE TABLE IF NOT EXISTS alerts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id),
  incident_id UUID REFERENCES incidents(id) ON DELETE CASCADE,
  vulnerability_id UUID REFERENCES vulnerabilities(id) ON DELETE CASCADE,
  alert_type alert_type DEFAULT 'email',
  status alert_status DEFAULT 'pending',
  recipient_email VARCHAR(255),
  subject VARCHAR(255),
  body TEXT,
  sent_at TIMESTAMP WITH TIME ZONE,
  failed_reason TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  INDEX idx_org_id (org_id),
  INDEX idx_status (status),
  INDEX idx_created_at (created_at DESC)
);

-- ============================================================================
-- 8. AUDIT LOGS (compliance & tracking)
-- ============================================================================
CREATE TYPE audit_action AS ENUM (
  'CREATE', 'READ', 'UPDATE', 'DELETE', 'STATUS_CHANGE', 'ASSIGNMENT', 'COMMENT'
);

CREATE TABLE IF NOT EXISTS audit_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES users(id),
  action audit_action NOT NULL,
  resource_type VARCHAR(50) NOT NULL,
  resource_id UUID NOT NULL,
  old_values JSONB,
  new_values JSONB,
  ip_address VARCHAR(45),
  user_agent TEXT,
  timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  INDEX idx_org_id (org_id),
  INDEX idx_user_id (user_id),
  INDEX idx_resource_type (resource_type),
  INDEX idx_timestamp (timestamp DESC)
);

-- ============================================================================
-- 9. API KEYS (for integrations)
-- ============================================================================
CREATE TABLE IF NOT EXISTS api_keys (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES users(id),
  name VARCHAR(255) NOT NULL,
  key_hash VARCHAR(255) NOT NULL UNIQUE,
  last_used_at TIMESTAMP WITH TIME ZONE,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  expires_at TIMESTAMP WITH TIME ZONE,
  INDEX idx_org_id (org_id),
  INDEX idx_key_hash (key_hash)
);

-- ============================================================================
-- 10. WEBHOOK CONFIGURATIONS
-- ============================================================================
CREATE TABLE IF NOT EXISTS webhooks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  url VARCHAR(500) NOT NULL,
  events VARCHAR(50)[],
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  INDEX idx_org_id (org_id)
);

-- ============================================================================
-- 11. NOTIFICATION PREFERENCES
-- ============================================================================
CREATE TABLE IF NOT EXISTS notification_preferences (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
  org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  email_on_new_incident BOOLEAN DEFAULT TRUE,
  email_on_critical_vulnerability BOOLEAN DEFAULT TRUE,
  email_on_incident_update BOOLEAN DEFAULT TRUE,
  email_digest BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- ROW-LEVEL SECURITY (Multi-tenant isolation)
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE incidents ENABLE ROW LEVEL SECURITY;
ALTER TABLE vulnerabilities ENABLE ROW LEVEL SECURITY;
ALTER TABLE incident_vulnerabilities ENABLE ROW LEVEL SECURITY;
ALTER TABLE comments ENABLE ROW LEVEL SECURITY;
ALTER TABLE alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_keys ENABLE ROW LEVEL SECURITY;
ALTER TABLE webhooks ENABLE ROW LEVEL SECURITY;
ALTER TABLE notification_preferences ENABLE ROW LEVEL SECURITY;

-- RLS Policy: Users can only see their own organization
CREATE POLICY org_isolation_policy ON users
  FOR ALL USING (auth.uid()::text = id::text OR EXISTS (
    SELECT 1 FROM organizations WHERE id = org_id
  ));

-- Additional policies can be added in a separate migration after auth setup
-- These will be more comprehensive after JWT validation is implemented

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_users_org_id ON users(org_id);
CREATE INDEX IF NOT EXISTS idx_incidents_org_id ON incidents(org_id);
CREATE INDEX IF NOT EXISTS idx_incidents_assigned_to ON incidents(assigned_to);
CREATE INDEX IF NOT EXISTS idx_vulnerabilities_org_id ON vulnerabilities(org_id);
CREATE INDEX IF NOT EXISTS idx_comments_author_id ON comments(author_id);
CREATE INDEX IF NOT EXISTS idx_alerts_org_id ON alerts(org_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_org_id ON audit_logs(org_id);

-- ============================================================================
-- COMMENTS & SCHEMA NOTES
-- ============================================================================
-- Organization: Root tenant container
-- Users: Employees/team members with role-based access
-- Incidents: Security incidents with full lifecycle tracking
-- Vulnerabilities: CVE tracking with patch management
-- Comments: Incident discussions for team collaboration
-- Alerts: Email/webhook notifications
-- Audit Logs: Full change history for compliance
-- API Keys: For integration with external security tools
-- Webhooks: Receive events from external tools (SIEM, scanners)
-- Notification Preferences: User-specific notification settings
