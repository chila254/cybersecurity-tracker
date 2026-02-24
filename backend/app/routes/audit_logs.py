"""
Audit logs API endpoints
View and filter audit logs for compliance
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
from app.database import get_db
from app.models import AuditLog
from app.auth import get_current_user
from uuid import UUID


router = APIRouter(tags=["Audit Logs"])


@router.get("")
async def list_audit_logs(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    action: str = Query(None, description="Filter by action (CREATE, UPDATE, DELETE)"),
    resource_type: str = Query(None, description="Filter by resource type (Incident, Vulnerability)"),
    user_id: UUID = Query(None, description="Filter by user ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500)
):
    """
    List all audit logs for the organization
    Supports filtering by action, resource type, and user
    """
    query = db.query(AuditLog).filter(AuditLog.org_id == current_user["org_id"])
    
    # Filters
    if action:
        query = query.filter(AuditLog.action == action)
    if resource_type:
        query = query.filter(AuditLog.resource_type == resource_type)
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    
    # Get total count before pagination
    total = query.count()
    
    logs = query.order_by(desc(AuditLog.timestamp)).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "logs": [
            {
                "id": str(log.id),
                "timestamp": log.timestamp.isoformat(),
                "user_id": str(log.user_id),
                "action": log.action,
                "resource_type": log.resource_type,
                "resource_id": str(log.resource_id),
                "old_values": log.old_values,
                "new_values": log.new_values,
                "ip_address": log.ip_address,
                "user_agent": log.user_agent
            }
            for log in logs
        ]
    }


@router.get("/stats")
async def get_audit_stats(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get audit log statistics"""
    
    # Total logs
    total_logs = db.query(func.count(AuditLog.id)).filter(
        AuditLog.org_id == current_user["org_id"]
    ).scalar()
    
    # Logs by action
    by_action = db.query(
        AuditLog.action,
        func.count(AuditLog.id)
    ).filter(
        AuditLog.org_id == current_user["org_id"]
    ).group_by(AuditLog.action).all()
    
    # Logs by resource type
    by_resource = db.query(
        AuditLog.resource_type,
        func.count(AuditLog.id)
    ).filter(
        AuditLog.org_id == current_user["org_id"]
    ).group_by(AuditLog.resource_type).all()
    
    # Most active users
    active_users = db.query(
        AuditLog.user_id,
        func.count(AuditLog.id).label("action_count")
    ).filter(
        AuditLog.org_id == current_user["org_id"]
    ).group_by(AuditLog.user_id).order_by(desc("action_count")).limit(5).all()
    
    return {
        "total_logs": total_logs or 0,
        "by_action": {
            item[0]: item[1] for item in by_action
        },
        "by_resource_type": {
            item[0]: item[1] for item in by_resource
        },
        "top_users": [
            {
                "user_id": str(user_id),
                "action_count": count
            }
            for user_id, count in active_users
        ]
    }


@router.get("/{log_id}")
async def get_audit_log(
    log_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a specific audit log entry"""
    
    log = db.query(AuditLog).filter(
        and_(
            AuditLog.id == log_id,
            AuditLog.org_id == current_user["org_id"]
        )
    ).first()
    
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit log not found"
        )
    
    return {
        "id": str(log.id),
        "timestamp": log.timestamp.isoformat(),
        "user_id": str(log.user_id),
        "action": log.action,
        "resource_type": log.resource_type,
        "resource_id": str(log.resource_id),
        "old_values": log.old_values,
        "new_values": log.new_values,
        "ip_address": log.ip_address,
        "user_agent": log.user_agent
    }


@router.get("/resource/{resource_id}")
async def get_resource_history(
    resource_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get full change history for a specific resource"""
    
    logs = db.query(AuditLog).filter(
        and_(
            AuditLog.resource_id == resource_id,
            AuditLog.org_id == current_user["org_id"]
        )
    ).order_by(desc(AuditLog.timestamp)).all()
    
    if not logs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No history found for this resource"
        )
    
    return {
        "resource_id": str(resource_id),
        "total_changes": len(logs),
        "history": [
            {
                "id": str(log.id),
                "timestamp": log.timestamp.isoformat(),
                "user_id": str(log.user_id),
                "action": log.action,
                "old_values": log.old_values,
                "new_values": log.new_values
            }
            for log in logs
        ]
    }
