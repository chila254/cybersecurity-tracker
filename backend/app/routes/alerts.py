"""
Alerts and Notifications API routes
Email alerts, webhook notifications, real-time updates
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.database import get_db
from app.models import Alert, Incident, Vulnerability, NotificationPreference, User
from app.auth import get_current_user
from uuid import UUID
from datetime import datetime

router = APIRouter(prefix="/alerts", tags=["Alerts"])

# ============================================================================
# List Alerts
# ============================================================================

@router.get("", response_model=list[dict])
async def list_alerts(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    status: str = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """
    List all alerts for the organization or user
    """
    query = db.query(Alert).filter(Alert.org_id == current_user["org_id"])
    
    if status:
        query = query.filter(Alert.status == status)
    
    alerts = query.order_by(Alert.created_at.desc()).offset(skip).limit(limit).all()
    
    return [
        {
            "id": str(alert.id),
            "type": alert.alert_type,
            "status": alert.status,
            "subject": alert.subject,
            "sent_at": alert.sent_at,
            "created_at": alert.created_at,
        }
        for alert in alerts
    ]

# ============================================================================
# Get Notification Preferences
# ============================================================================

@router.get("/preferences/{user_id}", response_model=dict)
async def get_notification_preferences(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get notification preferences for a user
    """
    # Users can only view their own preferences unless they're admin
    if str(user_id) != str(current_user["user_id"]) and current_user["role"] != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access other user's preferences"
        )
    
    prefs = db.query(NotificationPreference).filter(
        and_(
            NotificationPreference.user_id == user_id,
            NotificationPreference.org_id == current_user["org_id"]
        )
    ).first()
    
    if not prefs:
        # Create default preferences
        prefs = NotificationPreference(
            user_id=user_id,
            org_id=current_user["org_id"]
        )
        db.add(prefs)
        db.commit()
    
    return {
        "user_id": str(prefs.user_id),
        "email_on_new_incident": prefs.email_on_new_incident,
        "email_on_critical_vulnerability": prefs.email_on_critical_vulnerability,
        "email_on_incident_update": prefs.email_on_incident_update,
        "email_digest": prefs.email_digest,
    }

# ============================================================================
# Update Notification Preferences
# ============================================================================

@router.put("/preferences/{user_id}")
async def update_notification_preferences(
    user_id: UUID,
    preferences: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update notification preferences for a user
    """
    # Users can only update their own preferences unless they're admin
    if str(user_id) != str(current_user["user_id"]) and current_user["role"] != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot update other user's preferences"
        )
    
    prefs = db.query(NotificationPreference).filter(
        and_(
            NotificationPreference.user_id == user_id,
            NotificationPreference.org_id == current_user["org_id"]
        )
    ).first()
    
    if not prefs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preferences not found"
        )
    
    try:
        if "email_on_new_incident" in preferences:
            prefs.email_on_new_incident = preferences["email_on_new_incident"]
        if "email_on_critical_vulnerability" in preferences:
            prefs.email_on_critical_vulnerability = preferences["email_on_critical_vulnerability"]
        if "email_on_incident_update" in preferences:
            prefs.email_on_incident_update = preferences["email_on_incident_update"]
        if "email_digest" in preferences:
            prefs.email_digest = preferences["email_digest"]
        
        prefs.updated_at = datetime.utcnow()
        db.commit()
        
        return {
            "message": "Preferences updated successfully",
            "user_id": str(prefs.user_id),
            "email_on_new_incident": prefs.email_on_new_incident,
            "email_on_critical_vulnerability": prefs.email_on_critical_vulnerability,
            "email_on_incident_update": prefs.email_on_incident_update,
            "email_digest": prefs.email_digest,
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# ============================================================================
# Create Alert (Internal use - called after incidents/vulns created)
# ============================================================================

def create_alert_for_incident(
    db: Session,
    incident_id: UUID,
    org_id: UUID,
    subject: str,
    body: str,
    alert_type: str = "email"
):
    """
    Helper function to create alerts when incidents are created/updated
    Used internally by incident routes
    """
    try:
        # Get users with notification preferences enabled
        users_to_notify = db.query(User).filter(
            and_(
                User.org_id == org_id,
                User.is_active == True
            )
        ).all()
        
        for user in users_to_notify:
            prefs = db.query(NotificationPreference).filter(
                NotificationPreference.user_id == user.id
            ).first()
            
            # Check if user wants incident notifications
            if prefs and prefs.email_on_new_incident:
                alert = Alert(
                    org_id=org_id,
                    user_id=user.id,
                    incident_id=incident_id,
                    alert_type=alert_type,
                    status="pending",
                    recipient_email=user.email,
                    subject=subject,
                    body=body
                )
                db.add(alert)
        
        db.commit()
    
    except Exception as e:
        print(f"Error creating alert: {e}")

def create_alert_for_vulnerability(
    db: Session,
    vulnerability_id: UUID,
    org_id: UUID,
    severity: str,
    subject: str,
    body: str,
    alert_type: str = "email"
):
    """
    Helper function to create alerts when vulnerabilities are created
    Used internally by vulnerability routes
    """
    try:
        # Get users with notification preferences enabled
        users_to_notify = db.query(User).filter(
            and_(
                User.org_id == org_id,
                User.is_active == True
            )
        ).all()
        
        for user in users_to_notify:
            prefs = db.query(NotificationPreference).filter(
                NotificationPreference.user_id == user.id
            ).first()
            
            # Only notify for critical/high vulnerabilities
            if prefs and prefs.email_on_critical_vulnerability and severity in ["CRITICAL", "HIGH"]:
                alert = Alert(
                    org_id=org_id,
                    user_id=user.id,
                    vulnerability_id=vulnerability_id,
                    alert_type=alert_type,
                    status="pending",
                    recipient_email=user.email,
                    subject=subject,
                    body=body
                )
                db.add(alert)
        
        db.commit()
    
    except Exception as e:
        print(f"Error creating vulnerability alert: {e}")

# ============================================================================
# Mark Alert as Sent
# ============================================================================

@router.post("/{alert_id}/sent")
async def mark_alert_sent(
    alert_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Mark an alert as sent (internal use)
    """
    alert = db.query(Alert).filter(
        and_(
            Alert.id == alert_id,
            Alert.org_id == current_user["org_id"]
        )
    ).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    alert.status = "sent"
    alert.sent_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Alert marked as sent"}

# ============================================================================
# Mark Alert as Failed
# ============================================================================

@router.post("/{alert_id}/failed")
async def mark_alert_failed(
    alert_id: UUID,
    reason: str = Query(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Mark an alert as failed (internal use)
    """
    alert = db.query(Alert).filter(
        and_(
            Alert.id == alert_id,
            Alert.org_id == current_user["org_id"]
        )
    ).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    alert.status = "failed"
    alert.failed_reason = reason
    db.commit()
    
    return {"message": "Alert marked as failed"}
