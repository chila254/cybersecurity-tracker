"""
Dashboard API routes
Analytics, statistics, trends, and charts data
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.database import get_db
from app.models import Incident, Vulnerability
from app.schemas import DashboardStats, DashboardResponse, IncidentTrend, SeverityDistribution, IncidentResponse
from app.auth import get_current_user
from datetime import datetime, timedelta

router = APIRouter(tags=["Dashboard"])

# ============================================================================
# Dashboard Statistics
# ============================================================================

@router.get("/stats", response_model=DashboardStats)
async def get_stats(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get dashboard statistics for the organization
    """
    org_id = current_user["org_id"]
    
    # Total and open incidents
    total_incidents = db.query(Incident).filter(
        Incident.org_id == org_id
    ).count()
    
    open_incidents = db.query(Incident).filter(
        and_(
            Incident.org_id == org_id,
            Incident.status.in_(["OPEN", "INVESTIGATING"])
        )
    ).count()
    
    critical_severity = db.query(Incident).filter(
        and_(
            Incident.org_id == org_id,
            Incident.severity == "CRITICAL"
        )
    ).count()
    
    # Vulnerabilities
    total_vulns = db.query(Vulnerability).filter(
        Vulnerability.org_id == org_id
    ).count()
    
    unpatched_vulns = db.query(Vulnerability).filter(
        and_(
            Vulnerability.org_id == org_id,
            Vulnerability.status == "UNPATCHED"
        )
    ).count()
    
    # This month incidents
    month_ago = datetime.utcnow() - timedelta(days=30)
    incidents_this_month = db.query(Incident).filter(
        and_(
            Incident.org_id == org_id,
            Incident.created_at >= month_ago
        )
    ).count()
    
    return DashboardStats(
        total_incidents=total_incidents,
        open_incidents=open_incidents,
        critical_severity=critical_severity,
        total_vulnerabilities=total_vulns,
        unpatched_vulnerabilities=unpatched_vulns,
        incidents_this_month=incidents_this_month
    )

# ============================================================================
# Incident Trends (Last 30 days)
# ============================================================================

@router.get("/trends", response_model=list[IncidentTrend])
async def get_incident_trends(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    days: int = 30
):
    """
    Get incident creation trends for the last N days
    """
    org_id = current_user["org_id"]
    start_date = datetime.utcnow() - timedelta(days=days)
    
    trends = db.query(
        func.date(Incident.created_at).label("date"),
        func.count(Incident.id).label("count")
    ).filter(
        and_(
            Incident.org_id == org_id,
            Incident.created_at >= start_date
        )
    ).group_by(
        func.date(Incident.created_at)
    ).order_by("date").all()
    
    return [
        IncidentTrend(date=str(trend[0]), count=trend[1])
        for trend in trends
    ]

# ============================================================================
# Severity Distribution
# ============================================================================

@router.get("/severity-distribution", response_model=list[SeverityDistribution])
async def get_severity_distribution(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get incident distribution by severity level
    """
    org_id = current_user["org_id"]
    
    distribution = db.query(
        Incident.severity,
        func.count(Incident.id).label("count")
    ).filter(
        Incident.org_id == org_id
    ).group_by(
        Incident.severity
    ).all()
    
    return [
        SeverityDistribution(severity=str(item[0]), count=item[1])
        for item in distribution
    ]

# ============================================================================
# Complete Dashboard
# ============================================================================

@router.get("", response_model=DashboardResponse)
async def get_dashboard(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get complete dashboard data with stats, trends, and distributions
    """
    stats = await get_stats(db, current_user)
    trends = await get_incident_trends(db, current_user)
    severity = await get_severity_distribution(db, current_user)
    
    return DashboardResponse(
        stats=stats,
        incident_trends=trends,
        severity_distribution=severity
    )

# ============================================================================
# Most Recent Incidents
# ============================================================================

@router.get("/recent-incidents", response_model=list[IncidentResponse])
async def get_recent_incidents(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    limit: int = 10
):
    """
    Get most recent incidents across the organization
    """
    incidents = db.query(Incident).filter(
        Incident.org_id == current_user["org_id"]
    ).order_by(
        Incident.created_at.desc()
    ).limit(limit).all()
    
    return [IncidentResponse.model_validate(incident) for incident in incidents]

# ============================================================================
# Critical Vulnerabilities
# ============================================================================

@router.get("/critical-vulnerabilities", response_model=list)
async def get_critical_vulnerabilities(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get all critical vulnerabilities that are unpatched
    """
    vulns = db.query(Vulnerability).filter(
        and_(
            Vulnerability.org_id == current_user["org_id"],
            Vulnerability.severity.in_(["CRITICAL", "HIGH"]),
            Vulnerability.status == "UNPATCHED"
        )
    ).order_by(
        Vulnerability.discovered_date.desc()
    ).all()
    
    return vulns
