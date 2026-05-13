"""
Network Monitoring API routes
WiFi device tracking and DNS log monitoring
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
from uuid import UUID
from datetime import datetime, timedelta
import json
import asyncio
from typing import List
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
from app.services.router_detection_service import RouterDetectionService
from app.services.pihole_service import PiHoleService
from app.services.network_monitor import NetworkMonitor

router = APIRouter(tags=["Network Monitoring"])

# ============================================================================
# Router Auto-Detection
# ============================================================================

@router.post("/wifi-config/detect")
async def detect_router():
    """
    Auto-detect router type and URL
    No authentication required (local network scan)
    """
    try:
        result = await RouterDetectionService.detect_router()
        return result
    except Exception as e:
        return {
            "detected": False,
            "error": str(e),
            "message": "Router detection failed"
        }

@router.post("/wifi-config/test-connection")
async def test_router_connection(
    router_url: str,
    password: str,
    router_type: str = "tenda",
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Test if router connection works with provided credentials
    """
    try:
        result = await RouterDetectionService.test_connection(
            router_url=router_url,
            password=password,
            router_type=router_type
        )
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

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
            detail=str(e)
        )

# ============================================================================
# Real-time Network Monitoring
# ============================================================================

# Global network monitor instance (per organization)
network_monitors = {}

@router.post("/monitoring/start")
async def start_network_monitoring(
    interface: str = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Start real-time network monitoring for device detection"""
    org_id = str(current_user["org_id"])

    if org_id in network_monitors and network_monitors[org_id].is_monitoring:
        return {
            "status": "already_running",
            "message": "Network monitoring is already active"
        }

    try:
        monitor = NetworkMonitor(interface)
        network_monitors[org_id] = monitor

        # Add callback to save detected devices to database
        async def device_callback(event_type, data):
            try:
                if event_type == "device_connected":
                    # Save new device to database
                    device_data = data
                    existing = db.query(ConnectedDevice).filter(
                        ConnectedDevice.org_id == current_user["org_id"],
                        ConnectedDevice.mac_address == device_data["mac"]
                    ).first()

                    if not existing:
                        new_device = ConnectedDevice(
                            org_id=current_user["org_id"],
                            mac_address=device_data["mac"],
                            ip_address=device_data["ip"],
                            device_name=device_data.get("hostname", ""),
                            device_type="unknown",  # Will be determined later
                            is_online=True,
                            connected_at=device_data["last_seen"],
                            router_model="network_monitor"
                        )
                        db.add(new_device)
                        db.commit()

            except Exception as e:
                logger.error(f"Database callback error: {str(e)}")

        monitor.add_callback(device_callback)

        success = await monitor.start_monitoring()
        if success:
            return {
                "status": "started",
                "interface": monitor.interface,
                "message": f"Network monitoring started on interface {monitor.interface}"
            }
        else:
            return {
                "status": "failed",
                "message": "Failed to start network monitoring"
            }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to start monitoring: {str(e)}"
        }

@router.post("/monitoring/stop")
async def stop_network_monitoring(
    current_user: dict = Depends(get_current_user)
):
    """Stop real-time network monitoring"""
    org_id = str(current_user["org_id"])

    if org_id not in network_monitors:
        return {
            "status": "not_running",
            "message": "Network monitoring is not active"
        }

    try:
        monitor = network_monitors[org_id]
        monitor.stop_monitoring()
        del network_monitors[org_id]

        return {
            "status": "stopped",
            "message": "Network monitoring stopped"
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to stop monitoring: {str(e)}"
        }

@router.get("/monitoring/status")
async def get_monitoring_status(
    current_user: dict = Depends(get_current_user)
):
    """Get current monitoring status"""
    org_id = str(current_user["org_id"])

    if org_id not in network_monitors:
        return {
            "active": False,
            "interface": None,
            "device_count": 0
        }

    monitor = network_monitors[org_id]
    devices = monitor.get_connected_devices()

    return {
        "active": monitor.is_monitoring,
        "interface": monitor.interface,
        "device_count": len(devices),
        "devices": devices
    }

@router.websocket("/ws/monitoring")
async def websocket_monitoring(
    websocket: WebSocket,
    current_user: dict = Depends(get_current_user)
):
    """WebSocket endpoint for real-time device monitoring"""
    await websocket.accept()
    org_id = str(current_user["org_id"])

    try:
        # Create monitor if not exists
        if org_id not in network_monitors:
            monitor = NetworkMonitor()
            network_monitors[org_id] = monitor

            # Add callback to send updates via WebSocket
            async def ws_callback(event_type, data):
                try:
                    await websocket.send_json({
                        "event": event_type,
                        "data": data,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                except Exception as e:
                    logger.error(f"WebSocket callback error: {str(e)}")

            monitor.add_callback(ws_callback)

            # Start monitoring if not already running
            if not monitor.is_monitoring:
                await monitor.start_monitoring()

        monitor = network_monitors[org_id]

        # Send initial device list
        devices = monitor.get_connected_devices()
        await websocket.send_json({
            "event": "initial_devices",
            "data": devices,
            "timestamp": datetime.utcnow().isoformat()
        })

        # Keep connection alive and listen for messages
        while True:
            # Wait for client messages (could be used for commands)
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30)
                # Process any client commands here
            except asyncio.TimeoutError:
                # Send ping to keep connection alive
                await websocket.send_json({"event": "ping"})

    except WebSocketDisconnect:
        logger.info("WebSocket monitoring connection closed")
    except Exception as e:
        logger.error(f"WebSocket monitoring error: {str(e)}")
    finally:
        # Cleanup if needed
        pass

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

# ============================================================================
# Pi-hole Integration
# ============================================================================

@router.post("/pihole/test-connection")
async def test_pihole_connection(
    pihole_url: str,
    api_key: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Test connection to Pi-hole instance"""
    try:
        async with PiHoleService(pihole_url, api_key) as pihole:
            result = await pihole.test_connection()
            return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to test Pi-hole connection"
        }

@router.post("/pihole/setup", response_model=WiFiConfigResponse)
async def setup_pihole_integration(
    pihole_url: str,
    api_key: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Setup Pi-hole integration for DNS monitoring"""
    org_id = current_user["org_id"]

    # Check if Pi-hole connection works
    async with PiHoleService(pihole_url, api_key) as pihole:
        test_result = await pihole.test_connection()
        if not test_result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot connect to Pi-hole: {test_result.get('error', 'Unknown error')}"
            )

    # Update existing config or create new one
    config = db.query(WiFiConfig).filter(WiFiConfig.org_id == org_id).first()
    if config:
        config.dns_log_source = "pihole"
        config.dns_log_url = pihole_url
        config.dns_api_key = api_key
        config.is_enabled = True
        config.last_sync_at = datetime.utcnow()
    else:
        # Create new config for Pi-hole only
        config = WiFiConfig(
            org_id=org_id,
            router_type="pihole_only",
            router_url="",  # No router needed for Pi-hole
            router_username="",
            router_password="",
            dns_log_source="pihole",
            dns_log_url=pihole_url,
            dns_api_key=api_key,
            is_enabled=True,
            last_sync_at=datetime.utcnow()
        )
        db.add(config)

    db.commit()
    db.refresh(config)

    return config

@router.post("/pihole/sync-dns")
async def sync_pihole_dns_logs(
    since_hours: int = Query(24, ge=1, le=168),  # Last 24 hours to 1 week
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Sync DNS logs from Pi-hole to database"""
    org_id = current_user["org_id"]

    config = db.query(WiFiConfig).filter(WiFiConfig.org_id == org_id).first()
    if not config or config.dns_log_source != "pihole":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pi-hole integration not configured"
        )

    try:
        since_timestamp = int((datetime.utcnow().timestamp() - (since_hours * 3600)))

        async with PiHoleService(config.dns_log_url, config.dns_api_key) as pihole:
            imported_count = await pihole.sync_dns_logs_to_db(db, org_id, since_timestamp)

        # Update last sync time
        config.last_sync_at = datetime.utcnow()
        db.commit()

        return {
            "status": "success",
            "logs_imported": imported_count,
            "timestamp": datetime.utcnow().isoformat(),
            "message": f"Successfully imported {imported_count} DNS logs from Pi-hole"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to sync DNS logs: {str(e)}"
        )

@router.get("/pihole/stats")
async def get_pihole_stats(
    current_user: dict = Depends(get_current_user)
):
    """Get current Pi-hole statistics"""
    org_id = current_user["org_id"]

    from app.database import SessionLocal
    db = SessionLocal()
    try:
        config = db.query(WiFiConfig).filter(WiFiConfig.org_id == org_id).first()
        if not config or config.dns_log_source != "pihole":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pi-hole integration not configured"
            )

        async with PiHoleService(config.dns_log_url, config.dns_api_key) as pihole:
            stats = await pihole.get_stats()

        return {
            "pihole_stats": stats,
            "last_sync": config.last_sync_at.isoformat() if config.last_sync_at else None
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get Pi-hole stats: {str(e)}"
        )
    finally:
        db.close()

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
