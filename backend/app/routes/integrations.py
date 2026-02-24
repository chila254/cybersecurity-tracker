"""
Integrations and API Keys management
Third-party integrations, webhooks, and API authentication
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.database import get_db
from app.models import ApiKey, Webhook
from app.auth import get_current_user, hash_password
from app.schemas import UserRole
from uuid import UUID, uuid4
from datetime import datetime, timedelta
import secrets

router = APIRouter(tags=["Integrations"])

# ============================================================================
# API Keys Management
# ============================================================================

def generate_api_key() -> tuple[str, str]:
    """
    Generate a new API key and its hash
    Returns: (key, key_hash) where key is shown once and hash is stored
    """
    key = f"sk_{secrets.token_urlsafe(32)}"
    key_hash = hash_password(key)
    return key, key_hash

@router.post("/api-keys", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    name: str,
    expires_in_days: int = Query(90),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new API key for integrations
    Note: Key is only shown once during creation
    """
    if current_user["role"] not in ["ADMIN", "ANALYST"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and analysts can create API keys"
        )
    
    try:
        key, key_hash = generate_api_key()
        
        expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        
        api_key = ApiKey(
            org_id=current_user["org_id"],
            user_id=current_user["user_id"],
            name=name,
            key_hash=key_hash,
            expires_at=expires_at
        )
        db.add(api_key)
        db.commit()
        
        return {
            "id": str(api_key.id),
            "name": api_key.name,
            "key": key,  # Only shown once!
            "created_at": api_key.created_at,
            "expires_at": api_key.expires_at,
            "message": "Save this key securely. You won't see it again."
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/api-keys", response_model=list[dict])
async def list_api_keys(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    List all API keys for the organization
    """
    keys = db.query(ApiKey).filter(
        ApiKey.org_id == current_user["org_id"]
    ).all()
    
    return [
        {
            "id": str(key.id),
            "name": key.name,
            "is_active": key.is_active,
            "created_at": key.created_at,
            "expires_at": key.expires_at,
            "last_used_at": key.last_used_at,
        }
        for key in keys
    ]

@router.post("/api-keys/{key_id}/revoke")
async def revoke_api_key(
    key_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Revoke an API key
    """
    if current_user["role"] not in ["ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can revoke API keys"
        )
    
    api_key = db.query(ApiKey).filter(
        and_(
            ApiKey.id == key_id,
            ApiKey.org_id == current_user["org_id"]
        )
    ).first()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    api_key.is_active = False
    db.commit()
    
    return {"message": "API key revoked successfully"}

# ============================================================================
# Webhooks Management
# ============================================================================

@router.post("/webhooks", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_webhook(
    name: str,
    url: str,
    events: list[str],
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new webhook for external event notifications
    Supported events: incident.created, incident.updated, vulnerability.created
    """
    if current_user["role"] not in ["ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create webhooks"
        )
    
    # Validate URL format
    if not url.startswith("http://") and not url.startswith("https://"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Webhook URL must start with http:// or https://"
        )
    
    # Validate events
    valid_events = [
        "incident.created",
        "incident.updated",
        "incident.resolved",
        "vulnerability.created",
        "vulnerability.patched"
    ]
    
    for event in events:
        if event not in valid_events:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid event: {event}. Valid events: {valid_events}"
            )
    
    try:
        webhook = Webhook(
            org_id=current_user["org_id"],
            name=name,
            url=url,
            events=events,
            is_active=True
        )
        db.add(webhook)
        db.commit()
        
        return {
            "id": str(webhook.id),
            "name": webhook.name,
            "url": webhook.url,
            "events": webhook.events,
            "is_active": webhook.is_active,
            "created_at": webhook.created_at,
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/webhooks", response_model=list[dict])
async def list_webhooks(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    List all webhooks for the organization
    """
    webhooks = db.query(Webhook).filter(
        Webhook.org_id == current_user["org_id"]
    ).all()
    
    return [
        {
            "id": str(wh.id),
            "name": wh.name,
            "url": wh.url,
            "events": wh.events,
            "is_active": wh.is_active,
            "created_at": wh.created_at,
        }
        for wh in webhooks
    ]

@router.put("/webhooks/{webhook_id}")
async def update_webhook(
    webhook_id: UUID,
    name: str = None,
    events: list[str] = None,
    is_active: bool = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Update a webhook configuration
    """
    if current_user["role"] not in ["ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can update webhooks"
        )
    
    webhook = db.query(Webhook).filter(
        and_(
            Webhook.id == webhook_id,
            Webhook.org_id == current_user["org_id"]
        )
    ).first()
    
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )
    
    try:
        if name:
            webhook.name = name
        if events:
            webhook.events = events
        if is_active is not None:
            webhook.is_active = is_active
        
        webhook.updated_at = datetime.utcnow()
        db.commit()
        
        return {
            "id": str(webhook.id),
            "name": webhook.name,
            "url": webhook.url,
            "events": webhook.events,
            "is_active": webhook.is_active,
            "updated_at": webhook.updated_at,
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/webhooks/{webhook_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_webhook(
    webhook_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a webhook
    """
    if current_user["role"] not in ["ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete webhooks"
        )
    
    webhook = db.query(Webhook).filter(
        and_(
            Webhook.id == webhook_id,
            Webhook.org_id == current_user["org_id"]
        )
    ).first()
    
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook not found"
        )
    
    db.delete(webhook)
    db.commit()

# ============================================================================
# Integration Status
# ============================================================================

@router.get("/status", response_model=dict)
async def get_integration_status(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get status of all integrations for the organization
    """
    api_keys_count = db.query(ApiKey).filter(
        and_(
            ApiKey.org_id == current_user["org_id"],
            ApiKey.is_active == True
        )
    ).count()
    
    webhooks_count = db.query(Webhook).filter(
        and_(
            Webhook.org_id == current_user["org_id"],
            Webhook.is_active == True
        )
    ).count()
    
    return {
        "api_keys": {
            "active": api_keys_count,
            "status": "configured" if api_keys_count > 0 else "not_configured"
        },
        "webhooks": {
            "active": webhooks_count,
            "status": "configured" if webhooks_count > 0 else "not_configured"
        },
        "supported_integrations": [
            "Slack",
            "Jira",
            "ServiceNow",
            "Splunk",
            "ELK Stack",
            "Generic Webhook"
        ]
    }
