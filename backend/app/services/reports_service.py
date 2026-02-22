"""
Reports and analytics service
Generate security reports with aggregated data
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Incident, Vulnerability, AuditLog, User


class ReportsService:
    """Generate comprehensive security reports"""
    
    @staticmethod
    def get_monthly_summary(org_id, db: Session) -> Dict:
        """Get monthly summary report"""
        now = datetime.utcnow()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Incident counts
        incidents_created = db.query(func.count(Incident.id)).filter(
            Incident.org_id == org_id,
            Incident.created_at >= start_of_month
        ).scalar()
        
        incidents_resolved = db.query(func.count(Incident.id)).filter(
            Incident.org_id == org_id,
            Incident.status == "RESOLVED",
            Incident.resolved_at >= start_of_month
        ).scalar()
        
        # Vulnerability counts
        vulns_discovered = db.query(func.count(Vulnerability.id)).filter(
            Vulnerability.org_id == org_id,
            Vulnerability.created_at >= start_of_month
        ).scalar()
        
        vulns_patched = db.query(func.count(Vulnerability.id)).filter(
            Vulnerability.org_id == org_id,
            Vulnerability.status == "PATCHED",
            Vulnerability.patched_date >= start_of_month
        ).scalar()
        
        # Severity breakdown
        incidents_by_severity = db.query(
            Incident.severity,
            func.count(Incident.id)
        ).filter(
            Incident.org_id == org_id,
            Incident.created_at >= start_of_month
        ).group_by(Incident.severity).all()
        
        # Team activity
        audit_logs = db.query(func.count(AuditLog.id)).filter(
            AuditLog.org_id == org_id,
            AuditLog.timestamp >= start_of_month
        ).scalar()
        
        return {
            "month": now.strftime("%B %Y"),
            "incidents": {
                "created": incidents_created or 0,
                "resolved": incidents_resolved or 0,
                "open": (incidents_created or 0) - (incidents_resolved or 0)
            },
            "vulnerabilities": {
                "discovered": vulns_discovered or 0,
                "patched": vulns_patched or 0,
                "unpatched": (vulns_discovered or 0) - (vulns_patched or 0)
            },
            "severity_breakdown": {
                item[0]: item[1] for item in incidents_by_severity
            },
            "team_actions": audit_logs or 0
        }
    
    @staticmethod
    def get_incident_analysis(org_id, db: Session, days: int = 30) -> Dict:
        """Get detailed incident analysis report"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Incident distribution
        incidents_by_type = db.query(
            Incident.incident_type,
            func.count(Incident.id)
        ).filter(
            Incident.org_id == org_id,
            Incident.created_at >= start_date
        ).group_by(Incident.incident_type).all()
        
        incidents_by_severity = db.query(
            Incident.severity,
            func.count(Incident.id)
        ).filter(
            Incident.org_id == org_id,
            Incident.created_at >= start_date
        ).group_by(Incident.severity).all()
        
        incidents_by_status = db.query(
            Incident.status,
            func.count(Incident.id)
        ).filter(
            Incident.org_id == org_id,
            Incident.created_at >= start_date
        ).group_by(Incident.status).all()
        
        # Average resolution time
        resolved_incidents = db.query(Incident).filter(
            Incident.org_id == org_id,
            Incident.status == "RESOLVED",
            Incident.resolved_at >= start_date
        ).all()
        
        resolution_times = [
            (inc.resolved_at - inc.created_at).total_seconds() / 3600
            for inc in resolved_incidents
            if inc.resolved_at
        ]
        avg_resolution_hours = sum(resolution_times) / len(resolution_times) if resolution_times else 0
        
        # MTTR (Mean Time To Respond)
        open_incidents = db.query(Incident).filter(
            Incident.org_id == org_id,
            Incident.status.in_(["OPEN", "INVESTIGATING"]),
            Incident.created_at >= start_date
        ).all()
        
        response_times = [
            (inc.updated_at - inc.created_at).total_seconds() / 3600
            for inc in open_incidents
        ]
        mttr_hours = sum(response_times) / len(response_times) if response_times else 0
        
        return {
            "period_days": days,
            "date_range": {
                "start": start_date.strftime("%Y-%m-%d"),
                "end": datetime.utcnow().strftime("%Y-%m-%d")
            },
            "by_type": {
                item[0]: item[1] for item in incidents_by_type
            },
            "by_severity": {
                item[0]: item[1] for item in incidents_by_severity
            },
            "by_status": {
                item[0]: item[1] for item in incidents_by_status
            },
            "metrics": {
                "total_incidents": sum([item[1] for item in incidents_by_type]),
                "average_resolution_hours": round(avg_resolution_hours, 2),
                "mean_time_to_respond_hours": round(mttr_hours, 2),
                "resolved_incidents": len(resolved_incidents)
            }
        }
    
    @staticmethod
    def get_vulnerability_status(org_id, db: Session) -> Dict:
        """Get vulnerability status report"""
        # Vulnerability status breakdown
        vulns_by_status = db.query(
            Vulnerability.status,
            func.count(Vulnerability.id)
        ).filter(
            Vulnerability.org_id == org_id
        ).group_by(Vulnerability.status).all()
        
        vulns_by_severity = db.query(
            Vulnerability.severity,
            func.count(Vulnerability.id)
        ).filter(
            Vulnerability.org_id == org_id
        ).group_by(Vulnerability.severity).all()
        
        # Critical vulnerabilities
        critical_vulns = db.query(Vulnerability).filter(
            Vulnerability.org_id == org_id,
            Vulnerability.severity == "CRITICAL",
            Vulnerability.status != "PATCHED"
        ).all()
        
        # Oldest unpatched
        oldest_unpatched = db.query(Vulnerability).filter(
            Vulnerability.org_id == org_id,
            Vulnerability.status == "UNPATCHED"
        ).order_by(Vulnerability.discovered_date).first()
        
        return {
            "by_status": {
                item[0]: item[1] for item in vulns_by_status
            },
            "by_severity": {
                item[0]: item[1] for item in vulns_by_severity
            },
            "critical_unpatched": len(critical_vulns),
            "oldest_unpatched": {
                "cve_id": oldest_unpatched.cve_id if oldest_unpatched else None,
                "days_open": (datetime.utcnow() - oldest_unpatched.discovered_date).days if oldest_unpatched else 0
            },
            "total_vulnerabilities": sum([item[1] for item in vulns_by_status])
        }
    
    @staticmethod
    def get_compliance_audit_log(org_id, db: Session, days: int = 90) -> List[Dict]:
        """Get compliance-friendly audit log"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        logs = db.query(AuditLog).filter(
            AuditLog.org_id == org_id,
            AuditLog.timestamp >= start_date
        ).order_by(AuditLog.timestamp.desc()).all()
        
        return [
            {
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
    
    @staticmethod
    def get_team_performance(org_id, db: Session, days: int = 30) -> Dict:
        """Get team performance metrics"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get all users in org
        users = db.query(User).filter(User.org_id == org_id).all()
        
        team_stats = []
        for user in users:
            # Incidents created by user
            incidents_created = db.query(func.count(Incident.id)).filter(
                Incident.created_by == user.id,
                Incident.created_at >= start_date
            ).scalar()
            
            # Incidents assigned to user
            incidents_assigned = db.query(func.count(Incident.id)).filter(
                Incident.assigned_to == user.id,
                Incident.created_at >= start_date
            ).scalar()
            
            # Actions taken
            actions = db.query(func.count(AuditLog.id)).filter(
                AuditLog.user_id == user.id,
                AuditLog.timestamp >= start_date
            ).scalar()
            
            team_stats.append({
                "user_id": str(user.id),
                "user_name": user.name,
                "user_email": user.email,
                "role": user.role,
                "incidents_created": incidents_created or 0,
                "incidents_assigned": incidents_assigned or 0,
                "actions_taken": actions or 0
            })
        
        return {
            "period_days": days,
            "team_members": len(users),
            "team_stats": team_stats
        }
    
    @staticmethod
    def export_to_csv(report_data: Dict) -> str:
        """Convert report data to CSV format"""
        import csv
        from io import StringIO
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Flatten nested dict for CSV
        def flatten_dict(d, parent_key='', sep='_'):
            items = []
            for k, v in d.items():
                new_key = f"{parent_key}{sep}{k}" if parent_key else k
                if isinstance(v, dict):
                    items.extend(flatten_dict(v, new_key, sep=sep).items())
                else:
                    items.append((new_key, v))
            return dict(items)
        
        flat_data = flatten_dict(report_data)
        writer.writerow(flat_data.keys())
        writer.writerow(flat_data.values())
        
        return output.getvalue()
