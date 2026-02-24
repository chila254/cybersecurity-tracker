"""
WebSocket manager for real-time incident and vulnerability updates
Handles client connections, broadcasting, and disconnections
"""

import json
import logging
from typing import Dict, List, Set
from fastapi import WebSocket, WebSocketDisconnect, HTTPException
from datetime import datetime

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and broadcasting"""
    
    def __init__(self):
        # Structure: {org_id: {connection_id: websocket}}
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}
        # Track user to connection mapping
        self.user_connections: Dict[str, Set[str]] = {}
    
    async def connect(self, websocket: WebSocket, org_id: str, user_id: str, connection_id: str):
        """Accept WebSocket connection and register it"""
        await websocket.accept()
        
        if org_id not in self.active_connections:
            self.active_connections[org_id] = {}
        
        self.active_connections[org_id][connection_id] = websocket
        
        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(connection_id)
        
        logger.info(f"✅ WebSocket connected - Org: {org_id}, User: {user_id}, Connection: {connection_id}")
    
    def disconnect(self, org_id: str, connection_id: str, user_id: str = None):
        """Remove disconnected client"""
        if org_id in self.active_connections:
            self.active_connections[org_id].pop(connection_id, None)
            
            if not self.active_connections[org_id]:
                del self.active_connections[org_id]
        
        if user_id and user_id in self.user_connections:
            self.user_connections[user_id].discard(connection_id)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        
        logger.info(f"❌ WebSocket disconnected - Connection: {connection_id}")
    
    async def broadcast_to_org(self, org_id: str, message: dict):
        """Broadcast message to all connected users in an organization"""
        if org_id not in self.active_connections:
            return
        
        message["timestamp"] = datetime.utcnow().isoformat()
        message_json = json.dumps(message)
        
        disconnected = []
        for connection_id, websocket in self.active_connections[org_id].items():
            try:
                await websocket.send_text(message_json)
            except Exception as e:
                logger.error(f"Error broadcasting to {connection_id}: {e}")
                disconnected.append((org_id, connection_id))
        
        # Clean up broken connections
        for org_id, conn_id in disconnected:
            self.disconnect(org_id, conn_id)
    
    async def broadcast_to_user(self, user_id: str, message: dict):
        """Broadcast message to all connections of a specific user"""
        if user_id not in self.user_connections:
            return
        
        message["timestamp"] = datetime.utcnow().isoformat()
        message_json = json.dumps(message)
        
        for connection_id in list(self.user_connections[user_id]):
            # Find the websocket for this connection
            for org_id, connections in self.active_connections.items():
                if connection_id in connections:
                    try:
                        await connections[connection_id].send_text(message_json)
                    except Exception as e:
                        logger.error(f"Error sending to {user_id}: {e}")
                    break
    
    async def send_to_connection(self, connection_id: str, message: dict):
        """Send message to a specific connection"""
        message["timestamp"] = datetime.utcnow().isoformat()
        message_json = json.dumps(message)
        
        for org_id, connections in self.active_connections.items():
            if connection_id in connections:
                try:
                    await connections[connection_id].send_text(message_json)
                    return True
                except Exception as e:
                    logger.error(f"Error sending to {connection_id}: {e}")
                    return False
        return False
    
    def get_active_connections_count(self, org_id: str = None) -> int:
        """Get count of active WebSocket connections"""
        if org_id:
            return len(self.active_connections.get(org_id, {}))
        return sum(len(conns) for conns in self.active_connections.values())


# Global connection manager
manager = ConnectionManager()


# Message schemas for type safety
class WebSocketMessage:
    """WebSocket message types"""
    
    # Incident events
    INCIDENT_CREATED = "incident_created"
    INCIDENT_UPDATED = "incident_updated"
    INCIDENT_DELETED = "incident_deleted"
    INCIDENT_STATUS_CHANGED = "incident_status_changed"
    INCIDENT_ASSIGNED = "incident_assigned"
    
    # Vulnerability events
    VULNERABILITY_CREATED = "vulnerability_created"
    VULNERABILITY_UPDATED = "vulnerability_updated"
    VULNERABILITY_PATCHED = "vulnerability_patched"
    
    # Comment events
    COMMENT_ADDED = "comment_added"
    
    # System events
    USER_ONLINE = "user_online"
    USER_OFFLINE = "user_offline"
    ALERT_TRIGGERED = "alert_triggered"
    DASHBOARD_UPDATE = "dashboard_update"
    
    # Connection events
    PING = "ping"
    PONG = "pong"


def create_incident_message(incident_id: int, action: str, data: dict = None) -> dict:
    """Create incident WebSocket message"""
    return {
        "type": action,
        "entity": "incident",
        "incident_id": incident_id,
        "data": data or {},
        "severity": data.get("severity") if data else None,
    }


def create_vulnerability_message(vuln_id: int, action: str, data: dict = None) -> dict:
    """Create vulnerability WebSocket message"""
    return {
        "type": action,
        "entity": "vulnerability",
        "vulnerability_id": vuln_id,
        "data": data or {},
        "severity": data.get("severity") if data else None,
    }


def create_alert_message(alert_type: str, title: str, description: str, severity: str = "medium") -> dict:
    """Create alert WebSocket message"""
    return {
        "type": WebSocketMessage.ALERT_TRIGGERED,
        "alert_type": alert_type,
        "title": title,
        "description": description,
        "severity": severity,
    }


def create_dashboard_message(metrics: dict) -> dict:
    """Create dashboard update message"""
    return {
        "type": WebSocketMessage.DASHBOARD_UPDATE,
        "metrics": metrics,
    }


def create_user_presence_message(user_id: str, username: str, status: str) -> dict:
    """Create user presence message (online/offline)"""
    return {
        "type": WebSocketMessage.USER_ONLINE if status == "online" else WebSocketMessage.USER_OFFLINE,
        "user_id": user_id,
        "username": username,
    }
