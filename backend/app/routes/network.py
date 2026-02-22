"""
Network Monitoring API routes
WiFi device tracking and DNS log monitoring
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
from uuid import UUID
from datetime import datetime, timedelta
from app.database import get_db
from app.auth import get_current_user
from app.models import (
    ConnectedDevice, DNSLog, WiFiConfig, NetworkPolicy, SiteCategory
)
from app.schemas import (
    ConnectedDeviceResponse, DNSLogResponse, WiFiConfigCreate, WiFiConfigResponse,
    NetworkPolicyCreate, NetworkPolicyResponse, NetworkStatsResponse
)
from app.services.wifi_service import WiFiService
from app.services.dns_service import DNSService

router = APIRouter(prefix="/network", tags=["Network Monitoring"])

# ============================================================================
# WiFi Configuration
# ============================================================================

@router.post("/wifi-config", response_model=WiFiConfigResponse, status_code=status.HTTP_201_CREATED)
async def setup_wifi_config(
    config_data: WiFiConfigCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Setup WiFi router connection
    Supports: UniFi, Meraki, TP-Link, Mikrotik
    """
    org_id = current_user["org_id"]
    
    # Check if org already has config
    existing = db.query(WiFiConfig).filter(WiFiConfig.org_id == org_id).first()
    if existing:
        db.delete(existing)
        db.commit()
    
    try:
        wifi_config = WiFiConfig(
            org_id=org_id,
            router_type=config_data.router_type,
            router_url=config_data.router_url,
            router_username=config_data.router_username,
            router_password=config_data.router_password,
            dns_log_source=config_data.dns_log_source,
            dns_log_url=config_data.dns_log_url,
            dns_api_key=config_data.dns_api_key,
            is_enabled=True
        )
        db.add(wifi_config)
        db.commit()
        db.refresh(wifi_config)
        
        return wifi_config
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to save WiFi config: {str(e)}"
        )

@router.get("/wifi-config", response_model=WiFiConfigResponse)
async def get_wifi_config(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get WiFi configuration for organization"""
    org_id = current_user["org_id"]
    
    config = db.query(WiFiConfig).filter(WiFiConfig.org_id == org_id).first()
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="WiFi configuration not found"
        )
    
    return config

@router.post("/wifi-config/sync")
async def sync_devices(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Sync connected devices from WiFi router
    Fetches current device list and stores in database
    """
    org_id = current_user["org_id"]
    
    config = db.query(WiFiConfig).filter(WiFiConfig.org_id == org_id).first()
    if not config or not config.is_enabled:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="WiFi configuration not found or disabled"
        )
    
    try:
        wifi_service = WiFiService(config)
        devices = await wifi_service.get_connected_devices()
        await wifi_service.save_devices_to_db(db, org_id, devices)
        
        # Update last sync time
        config.last_sync_at = datetime.utcnow()
        db.commit()
        
        return {
            "status": "success",
            "devices_found": len(devices),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to sync devices: {str(e)}"
        )

# ============================================================================
# Connected Devices
# ============================================================================

@router.get("/devices", response_model=list[ConnectedDeviceResponse])
async def list_connected_devices(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    is_online: bool = Query(None),
    device_type: str = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """
    List connected WiFi devices
    Optional filters: is_online, device_type
    """
    org_id = current_user["org_id"]
    
    query = db.query(ConnectedDevice).filter(ConnectedDevice.org_id == org_id)
    
    if is_online is not None:
        query = query.filter(ConnectedDevice.is_online == is_online)
    
    if device_type:
        query = query.filter(ConnectedDevice.device_type == device_type)
    
    devices = query.order_by(
        desc(ConnectedDevice.connected_at)
    ).offset(skip).limit(limit).all()
    
    return devices

@router.get("/devices/{device_id}", response_model=ConnectedDeviceResponse)
async def get_device_details(
    device_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get detailed information about a specific device"""
    org_id = current_user["org_id"]
    
    device = db.query(ConnectedDevice).filter(
        and_(
            ConnectedDevice.id == device_id,
            ConnectedDevice.org_id == org_id
        )
    ).first()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    return device

@router.get("/devices/{device_id}/dns-history", response_model=list[DNSLogResponse])
async def get_device_dns_history(
    device_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    limit: int = Query(100, ge=1, le=500),
    category: str = Query(None)
):
    """
    Get DNS query history for a specific device/user
    Shows all websites visited
    """
    org_id = current_user["org_id"]
    
    device = db.query(ConnectedDevice).filter(
        and_(
            ConnectedDevice.id == device_id,
            ConnectedDevice.org_id == org_id
        )
    ).first()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    query = db.query(DNSLog).filter(
        and_(
            DNSLog.org_id == org_id,
            DNSLog.device_id == device_id
        )
    )
    
    if category:
        query = query.filter(DNSLog.domain_category == category)
    
    logs = query.order_by(desc(DNSLog.timestamp)).limit(limit).all()
    
    return logs

# ============================================================================
# DNS Logs & Site History
# ============================================================================

@router.get("/dns-logs", response_model=list[DNSLogResponse])
async def list_dns_logs(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    mac_address: str = Query(None),
    domain: str = Query(None),
    category: str = Query(None),
    is_blocked: bool = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    days: int = Query(7, ge=1)
):
    """
    Get DNS logs with filters
    Shows site visit history across all devices
    """
    org_id = current_user["org_id"]
    
    # Filter by date
    start_date = datetime.utcnow() - timedelta(days=days)
    
    query = db.query(DNSLog).filter(
        and_(
            DNSLog.org_id == org_id,
            DNSLog.timestamp >= start_date
        )
    )
    
    if mac_address:
        query = query.filter(DNSLog.mac_address.ilike(f"%{mac_address}%"))
    
    if domain:
        query = query.filter(DNSLog.domain.ilike(f"%{domain}%"))
    
    if category:
        query = query.filter(DNSLog.domain_category == category)
    
    if is_blocked is not None:
        query = query.filter(DNSLog.is_blocked == is_blocked)
    
    logs = query.order_by(desc(DNSLog.timestamp)).offset(skip).limit(limit).all()
    
    return logs

@router.get("/dns-logs/blocked")
async def get_blocked_queries(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500)
):
    """Get blocked DNS queries"""
    org_id = current_user["org_id"]
    
    blocked = db.query(DNSLog).filter(
        and_(
            DNSLog.org_id == org_id,
            DNSLog.is_blocked == True
        )
    ).order_by(desc(DNSLog.timestamp)).offset(skip).limit(limit).all()
    
    return blocked

@router.post("/dns-logs/import")
async def import_dns_logs(
    logs: list[dict],
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Import DNS logs in bulk
    Used for integrating with DNS log sources
    """
    org_id = current_user["org_id"]
    
    try:
        count = DNSService.import_dns_logs(db, org_id, logs)
        
        return {
            "status": "success",
            "logs_imported": count,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to import logs: {str(e)}"
        )

# ============================================================================
# Network Analytics
# ============================================================================

@router.get("/stats", response_model=NetworkStatsResponse)
async def get_network_stats(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get network statistics and analytics"""
    org_id = current_user["org_id"]
    
    # Total devices
    total_devices = db.query(func.count(ConnectedDevice.id)).filter(
        ConnectedDevice.org_id == org_id
    ).scalar() or 0
    
    # Online devices
    online_devices = db.query(func.count(ConnectedDevice.id)).filter(
        and_(
            ConnectedDevice.org_id == org_id,
            ConnectedDevice.is_online == True
        )
    ).scalar() or 0
    
    # DNS query stats
    total_dns = db.query(func.count(DNSLog.id)).filter(
        DNSLog.org_id == org_id
    ).scalar() or 0
    
    blocked_queries = db.query(func.count(DNSLog.id)).filter(
        and_(
            DNSLog.org_id == org_id,
            DNSLog.is_blocked == True
        )
    ).scalar() or 0
    
    # Top domains
    top_domains = DNSService.get_top_domains(db, org_id, limit=10)
    
    # Category distribution
    top_categories = DNSService.get_category_distribution(db, org_id)
    
    # Device type distribution
    device_types = db.query(
        ConnectedDevice.device_type,
        func.count(ConnectedDevice.id).label("count")
    ).filter(
        ConnectedDevice.org_id == org_id
    ).group_by(
        ConnectedDevice.device_type
    ).all()
    
    device_types_dict = {dt[0]: dt[1] for dt in device_types}
    
    return NetworkStatsResponse(
        total_devices=total_devices,
        online_devices=online_devices,
        total_dns_queries=total_dns,
        blocked_queries=blocked_queries,
        top_domains=top_domains,
        top_categories=top_categories,
        device_types=device_types_dict
    )

# ============================================================================
# Network Policies
# ============================================================================

@router.post("/policies", response_model=NetworkPolicyResponse, status_code=status.HTTP_201_CREATED)
async def create_network_policy(
    policy_data: NetworkPolicyCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a network access policy"""
    org_id = current_user["org_id"]
    
    try:
        policy = NetworkPolicy(
            org_id=org_id,
            name=policy_data.name,
            description=policy_data.description,
            block_categories=policy_data.block_categories or [],
            allow_categories=policy_data.allow_categories or [],
            blocked_domains=policy_data.blocked_domains or [],
            allowed_domains=policy_data.allowed_domains or []
        )
        db.add(policy)
        db.commit()
        db.refresh(policy)
        
        return policy
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/policies", response_model=list[NetworkPolicyResponse])
async def list_network_policies(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List all network policies"""
    org_id = current_user["org_id"]
    
    policies = db.query(NetworkPolicy).filter(
        NetworkPolicy.org_id == org_id
    ).order_by(NetworkPolicy.created_at.desc()).all()
    
    return policies

@router.get("/policies/{policy_id}", response_model=NetworkPolicyResponse)
async def get_network_policy(
    policy_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a specific network policy"""
    org_id = current_user["org_id"]
    
    policy = db.query(NetworkPolicy).filter(
        and_(
            NetworkPolicy.id == policy_id,
            NetworkPolicy.org_id == org_id
        )
    ).first()
    
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found"
        )
    
    return policy

@router.put("/policies/{policy_id}", response_model=NetworkPolicyResponse)
async def update_network_policy(
    policy_id: UUID,
    policy_data: NetworkPolicyCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update a network policy"""
    org_id = current_user["org_id"]
    
    policy = db.query(NetworkPolicy).filter(
        and_(
            NetworkPolicy.id == policy_id,
            NetworkPolicy.org_id == org_id
        )
    ).first()
    
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found"
        )
    
    try:
        policy.name = policy_data.name
        policy.description = policy_data.description
        policy.block_categories = policy_data.block_categories or []
        policy.allow_categories = policy_data.allow_categories or []
        policy.blocked_domains = policy_data.blocked_domains or []
        policy.allowed_domains = policy_data.allowed_domains or []
        policy.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(policy)
        
        return policy
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/policies/{policy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_network_policy(
    policy_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a network policy"""
    org_id = current_user["org_id"]
    
    policy = db.query(NetworkPolicy).filter(
        and_(
            NetworkPolicy.id == policy_id,
            NetworkPolicy.org_id == org_id
        )
    ).first()
    
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy not found"
        )
    
    try:
        db.delete(policy)
        db.commit()
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
