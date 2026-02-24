"""
WebSocket endpoints for real-time updates
"""

import logging
import uuid
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status
from app.websocket import manager, WebSocketMessage
from app.auth import verify_token
from app.database import get_db
from app.models import User

logger = logging.getLogger(__name__)

router = APIRouter(tags=["WebSocket"])


@router.websocket("/ws/incidents")
async def websocket_incidents(websocket: WebSocket, token: str = Query(None)):
    """
    WebSocket endpoint for real-time incident updates
    
    Query Parameters:
    - token: JWT token for authentication
    
    Connection URL:
    ws://localhost:8000/api/ws/incidents?token=your_jwt_token
    """
    
    connection_id = str(uuid.uuid4())
    user_id = None
    org_id = None
    
    try:
        # Verify JWT token
        if not token:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Missing authentication token")
            return
        
        payload = verify_token(token)
        if not payload:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
            return
        
        user_id = payload.get("sub")
        org_id = payload.get("org_id")
        
        if not user_id or not org_id:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Missing user or org in token")
            return
        
        # Register connection
        await manager.connect(websocket, org_id, user_id, connection_id)
        
        # Send welcome message
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to incidents stream",
            "connection_id": connection_id,
            "user_id": user_id,
            "org_id": org_id,
        })
        
        # Listen for messages from client (for keep-alive pings)
        while True:
            data = await websocket.receive_text()
            
            try:
                message = eval(data)  # Parse JSON
                if message.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
            except Exception as e:
                logger.error(f"Error processing WebSocket message: {e}")
                continue
    
    except WebSocketDisconnect:
        manager.disconnect(org_id, connection_id, user_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(org_id, connection_id, user_id)


@router.websocket("/ws/vulnerabilities")
async def websocket_vulnerabilities(websocket: WebSocket, token: str = Query(None)):
    """
    WebSocket endpoint for real-time vulnerability updates
    
    Query Parameters:
    - token: JWT token for authentication
    
    Connection URL:
    ws://localhost:8000/api/ws/vulnerabilities?token=your_jwt_token
    """
    
    connection_id = str(uuid.uuid4())
    user_id = None
    org_id = None
    
    try:
        # Verify JWT token
        if not token:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Missing authentication token")
            return
        
        payload = verify_token(token)
        if not payload:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
            return
        
        user_id = payload.get("sub")
        org_id = payload.get("org_id")
        
        if not user_id or not org_id:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Missing user or org in token")
            return
        
        # Register connection
        await manager.connect(websocket, org_id, user_id, connection_id)
        
        # Send welcome message
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to vulnerabilities stream",
            "connection_id": connection_id,
            "user_id": user_id,
            "org_id": org_id,
        })
        
        # Listen for messages from client (for keep-alive pings)
        while True:
            data = await websocket.receive_text()
            
            try:
                message = eval(data)  # Parse JSON
                if message.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
            except Exception as e:
                logger.error(f"Error processing WebSocket message: {e}")
                continue
    
    except WebSocketDisconnect:
        manager.disconnect(org_id, connection_id, user_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(org_id, connection_id, user_id)


@router.websocket("/ws/dashboard")
async def websocket_dashboard(websocket: WebSocket, token: str = Query(None)):
    """
    WebSocket endpoint for real-time dashboard updates
    
    Receives metrics updates without polling
    """
    
    connection_id = str(uuid.uuid4())
    user_id = None
    org_id = None
    
    try:
        # Verify JWT token
        if not token:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Missing authentication token")
            return
        
        payload = verify_token(token)
        if not payload:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
            return
        
        user_id = payload.get("sub")
        org_id = payload.get("org_id")
        
        if not user_id or not org_id:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Missing user or org in token")
            return
        
        # Register connection
        await manager.connect(websocket, org_id, user_id, connection_id)
        
        # Send welcome message
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to dashboard stream",
            "connection_id": connection_id,
            "user_id": user_id,
            "org_id": org_id,
        })
        
        # Listen for messages from client (for keep-alive pings)
        while True:
            data = await websocket.receive_text()
            
            try:
                message = eval(data)  # Parse JSON
                if message.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
            except Exception as e:
                logger.error(f"Error processing WebSocket message: {e}")
                continue
    
    except WebSocketDisconnect:
        manager.disconnect(org_id, connection_id, user_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(org_id, connection_id, user_id)


@router.get("/ws/connections", tags=["WebSocket"])
async def get_active_connections(token: str = Query(None)):
    """
    Get count of active WebSocket connections
    Useful for monitoring
    """
    
    if not token:
        return {"error": "Missing authentication token"}
    
    payload = verify_token(token)
    if not payload:
        return {"error": "Invalid token"}
    
    org_id = payload.get("org_id")
    
    return {
        "org_id": org_id,
        "active_connections": manager.get_active_connections_count(org_id),
        "total_connections": manager.get_active_connections_count(),
    }
