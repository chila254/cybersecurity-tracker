"""
Reports API endpoints
Generate various security reports and exports
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime
import io
import json

from app.database import get_db
from app.auth import get_current_user
from app.services.reports_service import ReportsService


router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/monthly-summary")
async def get_monthly_summary(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get monthly security summary report"""
    report = ReportsService.get_monthly_summary(current_user["org_id"], db)
    return report


@router.get("/incident-analysis")
async def get_incident_analysis(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get detailed incident analysis report"""
    report = ReportsService.get_incident_analysis(current_user["org_id"], db, days)
    return report


@router.get("/vulnerability-status")
async def get_vulnerability_status(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get vulnerability status report"""
    report = ReportsService.get_vulnerability_status(current_user["org_id"], db)
    return report


@router.get("/compliance-audit")
async def get_compliance_audit(
    days: int = Query(90, ge=1, le=365),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get compliance audit log report"""
    logs = ReportsService.get_compliance_audit_log(current_user["org_id"], db, days)
    # Simple pagination
    return {
        "total": len(logs),
        "skip": skip,
        "limit": limit,
        "logs": logs[skip:skip+limit]
    }


@router.get("/team-performance")
async def get_team_performance(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get team performance metrics"""
    report = ReportsService.get_team_performance(current_user["org_id"], db, days)
    return report


@router.get("/monthly-summary/export/csv")
async def export_monthly_summary_csv(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Export monthly summary as CSV"""
    report = ReportsService.get_monthly_summary(current_user["org_id"], db)
    csv_data = ReportsService.export_to_csv(report)
    
    return StreamingResponse(
        iter([csv_data]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=monthly_summary_{datetime.utcnow().strftime('%Y%m%d')}.csv"
        }
    )


@router.get("/incident-analysis/export/csv")
async def export_incident_analysis_csv(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Export incident analysis as CSV"""
    report = ReportsService.get_incident_analysis(current_user["org_id"], db, days)
    csv_data = ReportsService.export_to_csv(report)
    
    return StreamingResponse(
        iter([csv_data]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=incident_analysis_{datetime.utcnow().strftime('%Y%m%d')}.csv"
        }
    )


@router.get("/vulnerability-status/export/csv")
async def export_vulnerability_status_csv(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Export vulnerability status as CSV"""
    report = ReportsService.get_vulnerability_status(current_user["org_id"], db)
    csv_data = ReportsService.export_to_csv(report)
    
    return StreamingResponse(
        iter([csv_data]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=vulnerability_status_{datetime.utcnow().strftime('%Y%m%d')}.csv"
        }
    )


@router.get("/compliance-audit/export/csv")
async def export_compliance_audit_csv(
    days: int = Query(90, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Export compliance audit log as CSV"""
    logs = ReportsService.get_compliance_audit_log(current_user["org_id"], db, days)
    
    import csv
    output = io.StringIO()
    if logs:
        writer = csv.DictWriter(output, fieldnames=logs[0].keys())
        writer.writeheader()
        writer.writerows(logs)
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=compliance_audit_{datetime.utcnow().strftime('%Y%m%d')}.csv"
        }
    )


@router.get("/team-performance/export/csv")
async def export_team_performance_csv(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Export team performance as CSV"""
    report = ReportsService.get_team_performance(current_user["org_id"], db, days)
    csv_data = ReportsService.export_to_csv(report)
    
    return StreamingResponse(
        iter([csv_data]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=team_performance_{datetime.utcnow().strftime('%Y%m%d')}.csv"
        }
    )
