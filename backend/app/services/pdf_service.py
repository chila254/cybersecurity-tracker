"""
PDF Report Generation Service
"""

import io
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from app.models import Incident, Vulnerability, Comment, Organization


class PDFReportService:
    """Service for generating PDF security reports"""
    
    @staticmethod
    def generate_incident_report(db: Session, org_id, days: int = 30) -> bytes:
        """Generate incident report for specified period"""
        
        # Get date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Query incidents
        incidents = db.query(Incident).filter(
            and_(
                Incident.org_id == org_id,
                Incident.created_at >= start_date,
                Incident.created_at <= end_date
            )
        ).all()
        
        # Calculate statistics
        total = len(incidents)
        critical = len([i for i in incidents if i.severity == 'CRITICAL'])
        high = len([i for i in incidents if i.severity == 'HIGH'])
        medium = len([i for i in incidents if i.severity == 'MEDIUM'])
        low = len([i for i in incidents if i.severity == 'LOW'])
        
        resolved = len([i for i in incidents if i.status == 'RESOLVED'])
        open_incidents = len([i for i in incidents if i.status == 'OPEN'])
        
        # Create PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1F2937'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1F2937'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        story = []
        
        # Title
        story.append(Paragraph("Incident Security Report", title_style))
        story.append(Paragraph(f"Period: {start_date.date()} to {end_date.date()}", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", heading_style))
        summary_data = [
            ['Metric', 'Count'],
            ['Total Incidents', str(total)],
            ['Critical Severity', str(critical)],
            ['High Severity', str(high)],
            ['Resolved Incidents', str(resolved)],
            ['Open Incidents', str(open_incidents)],
        ]
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E5E7EB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1F2937')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Severity Distribution
        story.append(Paragraph("Severity Distribution", heading_style))
        severity_data = [
            ['Critical', 'High', 'Medium', 'Low'],
            [str(critical), str(high), str(medium), str(low)],
        ]
        severity_table = Table(severity_data, colWidths=[1.25*inch, 1.25*inch, 1.25*inch, 1.25*inch])
        severity_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.red),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        story.append(severity_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Recent Incidents Table
        if incidents:
            story.append(PageBreak())
            story.append(Paragraph("Recent Incidents", heading_style))
            
            incidents_data = [['Date', 'Title', 'Severity', 'Status']]
            for incident in sorted(incidents, key=lambda x: x.created_at, reverse=True)[:10]:
                incidents_data.append([
                    incident.created_at.strftime('%Y-%m-%d'),
                    incident.title[:40],
                    incident.severity,
                    incident.status
                ])
            
            incidents_table = Table(incidents_data, colWidths=[1.2*inch, 2.5*inch, 1*inch, 1.3*inch])
            incidents_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#374151')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]))
            story.append(incidents_table)
            story.append(Spacer(1, 0.3*inch))
        
        # Recommendations
        story.append(Paragraph("Recommendations", heading_style))
        recommendations = [
            f"1. Monitor critical severity incidents closely - {critical} detected in this period",
            f"2. Improve incident response time - {open_incidents} incidents still open",
            f"3. Review incident patterns to identify root causes",
            f"4. Implement automated remediation for common incident types",
            f"5. Conduct security awareness training if trend increasing"
        ]
        for rec in recommendations:
            story.append(Paragraph(rec, styles['Normal']))
            story.append(Spacer(1, 0.1*inch))
        
        # Footer
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC", styles['Normal']))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    @staticmethod
    def generate_vulnerability_report(db: Session, org_id, days: int = 30) -> bytes:
        """Generate vulnerability report"""
        
        # Get date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Query vulnerabilities
        vulns = db.query(Vulnerability).filter(
            and_(
                Vulnerability.org_id == org_id,
                Vulnerability.created_at >= start_date,
                Vulnerability.created_at <= end_date
            )
        ).all()
        
        # Calculate statistics
        total = len(vulns)
        critical = len([v for v in vulns if v.severity == 'CRITICAL'])
        high = len([v for v in vulns if v.severity == 'HIGH'])
        patched = len([v for v in vulns if v.status == 'PATCHED'])
        unpatched = len([v for v in vulns if v.status == 'UNPATCHED'])
        
        # Create PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1F2937'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1F2937'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        story = []
        
        # Title
        story.append(Paragraph("Vulnerability Report", title_style))
        story.append(Paragraph(f"Period: {start_date.date()} to {end_date.date()}", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", heading_style))
        summary_data = [
            ['Metric', 'Count'],
            ['Total Vulnerabilities', str(total)],
            ['Critical CVEs', str(critical)],
            ['High CVEs', str(high)],
            ['Patched', str(patched)],
            ['Unpatched', str(unpatched)],
            ['Patch Coverage', f"{(patched / total * 100):.1f}%" if total > 0 else "0%"],
        ]
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E5E7EB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1F2937')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Critical Vulnerabilities
        critical_vulns = [v for v in vulns if v.severity == 'CRITICAL']
        if critical_vulns:
            story.append(PageBreak())
            story.append(Paragraph("Critical Vulnerabilities Requiring Immediate Action", heading_style))
            
            for vuln in critical_vulns[:10]:
                story.append(Paragraph(f"• {vuln.cve_id}: {vuln.title}", styles['Normal']))
                story.append(Paragraph(f"  Status: {vuln.status} | CVSS: {vuln.cvss_score}", styles['Normal']))
                story.append(Spacer(1, 0.1*inch))
        
        # Footer
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC", styles['Normal']))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
