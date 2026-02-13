"""
Incidents Management API routes
CRUD operations for security incidents
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.database import get_db
from app.models import Incident, Comment, AuditLog
from app.schemas import (
    IncidentCreate, IncidentUpdate, IncidentResponse, CommentCreate, CommentResponse
)
from app.auth import get_current_user
from uuid import UUID
from datetime import datetime

router = APIRouter(prefix="/incidents", tags=["Incidents"])

# ============================================================================
# List Incidents
# ============================================================================

@router.get("", response_model=list[IncidentResponse])
async def list_incidents(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    status: str = Query(None),
    severity: str = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """
    List all incidents for the organization
    Supports filtering by status and severity
    """
    query = db.query(Incident).filter(Incident.org_id == current_user["org_id"])
    
    if status:
        query = query.filter(Incident.status == status)
    if severity:
        query = query.filter(Incident.severity == severity)
    
    incidents = query.order_by(Incident.created_at.desc()).offset(skip).limit(limit).all()
    return incidents

# ============================================================================
# Get Single Incident
# ============================================================================

@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(
    incident_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get detailed information about a specific incident
    """
    incident = db.query(Incident).filter(
        and_(
            Incident.id == incident_id,
            Incident.org_id == current_user["org_id"]
        )
    ).first()
    
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )
    
    return incident

# ============================================================================
# Create Incident
# ============================================================================

@router.post("", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
async def create_incident(
    incident_data: IncidentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new security incident
    """
    try:
        incident = Incident(
            org_id=current_user["org_id"],
            title=incident_data.title,
            description=incident_data.description,
            severity=incident_data.severity,
            incident_type=incident_data.incident_type,
            created_by=current_user["user_id"],
            assigned_to=incident_data.assigned_to,
            affected_systems=incident_data.affected_systems or [],
            external_reference_id=incident_data.external_reference_id
        )
        db.add(incident)
        db.flush()
        
        # Create audit log
        audit = AuditLog(
            org_id=current_user["org_id"],
            user_id=current_user["user_id"],
            action="CREATE",
            resource_type="Incident",
            resource_id=incident.id,
            new_values=incident_data.dict()
        )
        db.add(audit)
        db.commit()
        
        return incident
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# ============================================================================
# Update Incident
# ============================================================================

@router.put("/{incident_id}", response_model=IncidentResponse)
async def update_incident(
    incident_id: UUID,
    incident_data: IncidentUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update an existing incident
    Only ANALYST and ADMIN can update
    """
    if current_user["role"] not in ["ANALYST", "ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only analysts and admins can update incidents"
        )
    
    incident = db.query(Incident).filter(
        and_(
            Incident.id == incident_id,
            Incident.org_id == current_user["org_id"]
        )
    ).first()
    
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )
    
    try:
        old_values = {
            "title": incident.title,
            "severity": incident.severity,
            "status": incident.status
        }
        
        update_data = incident_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None:
                setattr(incident, field, value)
        
        # If status changed to RESOLVED, set resolved_at
        if incident_data.status == "RESOLVED":
            incident.resolved_at = datetime.utcnow()
        
        incident.updated_at = datetime.utcnow()
        db.flush()
        
        # Create audit log
        audit = AuditLog(
            org_id=current_user["org_id"],
            user_id=current_user["user_id"],
            action="UPDATE",
            resource_type="Incident",
            resource_id=incident.id,
            old_values=old_values,
            new_values=update_data
        )
        db.add(audit)
        db.commit()
        
        return incident
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# ============================================================================
# Delete Incident
# ============================================================================

@router.delete("/{incident_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_incident(
    incident_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete an incident - Only ADMIN
    """
    if current_user["role"] != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete incidents"
        )
    
    incident = db.query(Incident).filter(
        and_(
            Incident.id == incident_id,
            Incident.org_id == current_user["org_id"]
        )
    ).first()
    
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )
    
    try:
        # Create audit log before deletion
        audit = AuditLog(
            org_id=current_user["org_id"],
            user_id=current_user["user_id"],
            action="DELETE",
            resource_type="Incident",
            resource_id=incident.id,
            old_values={"title": incident.title, "severity": incident.severity}
        )
        db.add(audit)
        
        db.delete(incident)
        db.commit()
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# ============================================================================
# Comments/Timeline
# ============================================================================

@router.get("/{incident_id}/comments", response_model=list[CommentResponse])
async def get_incident_comments(
    incident_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get all comments for an incident
    """
    # Verify incident exists and belongs to org
    incident = db.query(Incident).filter(
        and_(
            Incident.id == incident_id,
            Incident.org_id == current_user["org_id"]
        )
    ).first()
    
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )
    
    comments = db.query(Comment).filter(
        Comment.incident_id == incident_id
    ).order_by(Comment.created_at.desc()).all()
    
    return comments

@router.post("/{incident_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def add_comment(
    incident_id: UUID,
    comment_data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Add a comment to an incident for team collaboration
    """
    # Verify incident exists
    incident = db.query(Incident).filter(
        and_(
            Incident.id == incident_id,
            Incident.org_id == current_user["org_id"]
        )
    ).first()
    
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )
    
    try:
        comment = Comment(
            incident_id=incident_id,
            author_id=current_user["user_id"],
            content=comment_data.content
        )
        db.add(comment)
        db.commit()
        
        return comment
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
