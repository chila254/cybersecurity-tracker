-- ============================================================================
-- Network Monitoring Tables
-- ============================================================================

-- Connected Devices Table
CREATE TABLE IF NOT EXISTS connected_devices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    mac_address VARCHAR(17) NOT NULL,
    ip_address VARCHAR(45),
    device_name VARCHAR(255),
    device_type VARCHAR(50),  -- laptop, phone, tablet, iot
    user_name VARCHAR(255),
    manufacturer VARCHAR(255),
    connected_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    disconnected_at TIMESTAMP,
    data_sent_bytes VARCHAR(50),
    data_received_bytes VARCHAR(50),
    signal_strength INTEGER,  -- -0 to -100 dBm
    is_online BOOLEAN DEFAULT true,
    router_model VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT device_unique UNIQUE(org_id, mac_address)
);

CREATE INDEX idx_connected_devices_org_id ON connected_devices(org_id);
CREATE INDEX idx_connected_devices_mac_address ON connected_devices(mac_address);
CREATE INDEX idx_connected_devices_ip_address ON connected_devices(ip_address);
CREATE INDEX idx_connected_devices_is_online ON connected_devices(is_online);

-- DNS Logs Table
CREATE TABLE IF NOT EXISTS dns_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    device_id UUID REFERENCES connected_devices(id) ON DELETE CASCADE,
    mac_address VARCHAR(17) NOT NULL,
    domain VARCHAR(500) NOT NULL,
    domain_category VARCHAR(50),  -- social, streaming, work, news, adult, malware, etc
    query_type VARCHAR(10),  -- A, AAAA, MX, etc
    response_code VARCHAR(10),  -- NOERROR, BLOCKED, etc
    is_blocked BOOLEAN DEFAULT false,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT dns_log_domain_length CHECK (length(domain) <= 500)
);

CREATE INDEX idx_dns_logs_org_id ON dns_logs(org_id);
CREATE INDEX idx_dns_logs_device_id ON dns_logs(device_id);
CREATE INDEX idx_dns_logs_mac_address ON dns_logs(mac_address);
CREATE INDEX idx_dns_logs_domain ON dns_logs(domain);
CREATE INDEX idx_dns_logs_timestamp ON dns_logs(timestamp);
CREATE INDEX idx_dns_logs_category ON dns_logs(domain_category);

-- Site Categories Table
CREATE TABLE IF NOT EXISTS site_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    domain VARCHAR(500) NOT NULL UNIQUE,
    category VARCHAR(50) NOT NULL,  -- social, streaming, work, news, adult, malware
    risk_level VARCHAR(20),  -- low, medium, high
    is_blocked BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_site_categories_domain ON site_categories(domain);
CREATE INDEX idx_site_categories_category ON site_categories(category);
CREATE INDEX idx_site_categories_risk_level ON site_categories(risk_level);

-- WiFi Configuration Table
CREATE TABLE IF NOT EXISTS wifi_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL UNIQUE REFERENCES organizations(id) ON DELETE CASCADE,
    router_type VARCHAR(50) NOT NULL,  -- unifi, meraki, tp_link, mikrotik
    router_url VARCHAR(500) NOT NULL,
    router_username VARCHAR(255) NOT NULL,
    router_password VARCHAR(500) NOT NULL,  -- encrypted in production
    dns_log_source VARCHAR(50),  -- cloudflare, quad9, local
    dns_log_url VARCHAR(500),
    dns_api_key VARCHAR(500),  -- encrypted in production
    is_enabled BOOLEAN DEFAULT true,
    last_sync_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_wifi_configs_org_id ON wifi_configs(org_id);

-- Network Policies Table
CREATE TABLE IF NOT EXISTS network_policies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    block_categories TEXT[],  -- stored as array
    allow_categories TEXT[],
    blocked_domains TEXT[],
    allowed_domains TEXT[],
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_network_policies_org_id ON network_policies(org_id);
CREATE INDEX idx_network_policies_is_active ON network_policies(is_active);

-- ============================================================================
-- Comments
-- ============================================================================

COMMENT ON TABLE connected_devices IS 'WiFi connected devices tracked from organization router';
COMMENT ON TABLE dns_logs IS 'DNS query history for all devices on network';
COMMENT ON TABLE site_categories IS 'Domain categorization for content filtering';
COMMENT ON TABLE wifi_configs IS 'WiFi router and DNS log source configuration';
COMMENT ON TABLE network_policies IS 'Network access policies and content filtering rules';

-- ============================================================================
-- Indexes for Performance
-- ============================================================================

-- For querying devices by organization and status
CREATE INDEX idx_devices_online_time ON connected_devices(org_id, is_online, connected_at DESC);

-- For DNS log queries by device and time
CREATE INDEX idx_dns_time_device ON dns_logs(org_id, device_id, timestamp DESC);

-- For DNS queries by domain category
CREATE INDEX idx_dns_category_blocked ON dns_logs(org_id, domain_category, is_blocked);
