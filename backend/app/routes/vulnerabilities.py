"""
Vulnerabilities Management API routes
CVE tracking, vulnerability scans, patch management
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, ilike
from app.database import get_db
from app.models import Vulnerability, AuditLog, Incident, User, NotificationPreference
from app.schemas import (
    VulnerabilityCreate, VulnerabilityUpdate, VulnerabilityResponse
)
from app.auth import get_current_user
from app.services import email_service, WebhookService
from uuid import UUID
from datetime import datetime
import asyncio

router = APIRouter(prefix="/vulnerabilities", tags=["Vulnerabilities"])

# ============================================================================
# List Vulnerabilities with Search, Filters & Pagination
# ============================================================================

@router.get("", response_model=list[VulnerabilityResponse])
async def list_vulnerabilities(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    search: str = Query(None, description="Search by CVE ID, title, or description"),
    status: str = Query(None),
    severity: str = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """
    List all vulnerabilities for the organization
    Supports search, filtering by status/severity, and pagination
    """
    query = db.query(Vulnerability).filter(Vulnerability.org_id == current_user["org_id"])
    
    # Text search
    if search:
        query = query.filter(
            or_(
                ilike(Vulnerability.cve_id, f"%{search}%"),
                ilike(Vulnerability.title, f"%{search}%"),
                ilike(Vulnerability.description, f"%{search}%")
            )
        )
    
    # Filters
    if status:
        query = query.filter(Vulnerability.status == status)
    if severity:
        query = query.filter(Vulnerability.severity == severity)
    
    vulns = query.order_by(Vulnerability.discovered_date.desc()).offset(skip).limit(limit).all()
    return vulns

# ============================================================================
# Get Single Vulnerability
# ============================================================================

@router.get("/{vuln_id}", response_model=VulnerabilityResponse)
async def get_vulnerability(
    vuln_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get detailed information about a specific vulnerability
    """
    vuln = db.query(Vulnerability).filter(
        and_(
            Vulnerability.id == vuln_id,
            Vulnerability.org_id == current_user["org_id"]
        )
    ).first()
    
    if not vuln:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vulnerability not found"
        )
    
    return vuln

# ============================================================================
# Create Vulnerability
# ============================================================================

@router.post("", response_model=VulnerabilityResponse, status_code=status.HTTP_201_CREATED)
async def create_vulnerability(
    vuln_data: VulnerabilityCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new vulnerability record
    Can be from manual entry or automated scans
    Sends notifications if severity is CRITICAL or HIGH
    """
    # Check for duplicate CVE
    if vuln_data.cve_id:
        existing = db.query(Vulnerability).filter(
            and_(
                Vulnerability.cve_id == vuln_data.cve_id,
                Vulnerability.org_id == current_user["org_id"]
            )
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Vulnerability with this CVE ID already exists"
            )
    
    try:
        vuln = Vulnerability(
            org_id=current_user["org_id"],
            cve_id=vuln_data.cve_id,
            title=vuln_data.title,
            description=vuln_data.description,
            cvss_score=vuln_data.cvss_score,
            cvss_vector=vuln_data.cvss_vector,
            severity=vuln_data.severity,
            status=vuln_data.status,
            affected_systems=vuln_data.affected_systems or [],
            remediation=vuln_data.remediation,
            created_by=current_user["user_id"]
        )
        db.add(vuln)
        db.flush()
        
        # Create audit log
        audit = AuditLog(
            org_id=current_user["org_id"],
            user_id=current_user["user_id"],
            action="CREATE",
            resource_type="Vulnerability",
            resource_id=vuln.id,
            new_values=vuln_data.dict()
        )
        db.add(audit)
        db.commit()
        
        # Send notifications for CRITICAL or HIGH vulnerabilities
        if vuln_data.severity in ["CRITICAL", "HIGH"]:
            asyncio.create_task(
                _send_vulnerability_notifications(
                    db, vuln, current_user["org_id"]
                )
            )
        
        return vuln
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


async def _send_vulnerability_notifications(db: Session, vuln: Vulnerability, org_id):
    """Send email and webhook notifications for critical vulnerability"""
    try:
        # Get users with critical vulnerability preferences
        users_with_prefs = db.query(User, NotificationPreference).join(
            NotificationPreference
        ).filter(
            User.org_id == org_id,
            NotificationPreference.email_on_critical_vulnerability == True,
            User.is_active == True
        ).all()
        
        # Send emails to users
        for user, pref in users_with_prefs:
            await email_service.send_vulnerability_alert(
                recipient_email=user.email,
                cve_id=vuln.cve_id or "Unknown",
                title=vuln.title,
                severity=vuln.severity,
                cvss_score=float(vuln.cvss_score) if vuln.cvss_score else 0,
                affected_systems=vuln.affected_systems or [],
                vulnerability_id=str(vuln.id)
            )
        
        # Trigger webhooks
        await WebhookService.trigger_vulnerability_webhook(
            org_id=str(org_id),
            vulnerability_id=str(vuln.id),
            cve_id=vuln.cve_id or "Unknown",
            title=vuln.title,
            severity=vuln.severity,
            cvss_score=float(vuln.cvss_score) if vuln.cvss_score else 0,
            affected_systems=vuln.affected_systems or [],
            db=db
        )
    except Exception as e:
        print(f"Error sending vulnerability notifications: {str(e)}")

# ============================================================================
# Update Vulnerability
# ============================================================================

@router.put("/{vuln_id}", response_model=VulnerabilityResponse)
async def update_vulnerability(
    vuln_id: UUID,
    vuln_data: VulnerabilityUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update a vulnerability record
    Track patch application and mitigation
    """
    if current_user["role"] not in ["ANALYST", "ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only analysts and admins can update vulnerabilities"
        )
    
    vuln = db.query(Vulnerability).filter(
        and_(
            Vulnerability.id == vuln_id,
            Vulnerability.org_id == current_user["org_id"]
        )
    ).first()
    
    if not vuln:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vulnerability not found"
        )
    
    try:
        old_values = {
            "title": vuln.title,
            "severity": vuln.severity,
            "status": vuln.status
        }
        
        update_data = vuln_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None:
                setattr(vuln, field, value)
        
        vuln.updated_at = datetime.utcnow()
        db.flush()
        
        # Create audit log
        audit = AuditLog(
            org_id=current_user["org_id"],
            user_id=current_user["user_id"],
            action="UPDATE",
            resource_type="Vulnerability",
            resource_id=vuln.id,
            old_values=old_values,
            new_values=update_data
        )
        db.add(audit)
        db.commit()
        
        return vuln
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# ============================================================================
# Delete Vulnerability
# ============================================================================

@router.delete("/{vuln_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vulnerability(
    vuln_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a vulnerability record - Only ADMIN
    """
    if current_user["role"] != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete vulnerabilities"
        )
    
    vuln = db.query(Vulnerability).filter(
        and_(
            Vulnerability.id == vuln_id,
            Vulnerability.org_id == current_user["org_id"]
        )
    ).first()
    
    if not vuln:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vulnerability not found"
        )
    
    try:
        # Create audit log before deletion
        audit = AuditLog(
            org_id=current_user["org_id"],
            user_id=current_user["user_id"],
            action="DELETE",
            resource_type="Vulnerability",
            resource_id=vuln.id,
            old_values={"title": vuln.title, "cve_id": vuln.cve_id}
        )
        db.add(audit)
        
        db.delete(vuln)
        db.commit()
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# ============================================================================
# Link Vulnerability to Incident
# ============================================================================

@router.post("/{vuln_id}/incidents/{incident_id}", status_code=status.HTTP_201_CREATED)
async def link_vulnerability_to_incident(
    vuln_id: UUID,
    incident_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Link a vulnerability to an incident
    """
    from app.models import IncidentVulnerability
    
    # Verify both exist
    vuln = db.query(Vulnerability).filter(
        and_(
            Vulnerability.id == vuln_id,
            Vulnerability.org_id == current_user["org_id"]
        )
    ).first()
    
    incident = db.query(Incident).filter(
        and_(
            Incident.id == incident_id,
            Incident.org_id == current_user["org_id"]
        )
    ).first()
    
    if not vuln or not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vulnerability or incident not found"
        )
    
    try:
        # Check if already linked
        existing = db.query(IncidentVulnerability).filter(
            and_(
                IncidentVulnerability.incident_id == incident_id,
                IncidentVulnerability.vulnerability_id == vuln_id
            )
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Vulnerability already linked to this incident"
            )
        
        link = IncidentVulnerability(
            incident_id=incident_id,
            vulnerability_id=vuln_id
        )
        db.add(link)
        db.commit()
        
        return {"message": "Vulnerability linked to incident successfully"}
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
