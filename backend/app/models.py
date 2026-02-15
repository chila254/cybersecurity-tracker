"""
SQLAlchemy ORM models for database tables
Maps Python classes to database schema
"""

from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, ARRAY, Numeric, Enum as SQLEnum, JSON, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
from uuid import uuid4
import enum

# ============================================================================
# Enums
# ============================================================================

class UserRoleEnum(str, enum.Enum):
    ADMIN = "ADMIN"
    ANALYST = "ANALYST"
    VIEWER = "VIEWER"

class IncidentSeverityEnum(str, enum.Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class IncidentStatusEnum(str, enum.Enum):
    OPEN = "OPEN"
    INVESTIGATING = "INVESTIGATING"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"

class IncidentTypeEnum(str, enum.Enum):
    DATA_BREACH = "data_breach"
    MALWARE = "malware"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DENIAL_OF_SERVICE = "denial_of_service"
    SOCIAL_ENGINEERING = "social_engineering"
    CONFIGURATION_ERROR = "configuration_error"
    SUPPLY_CHAIN = "supply_chain"
    OTHER = "other"

class VulnSeverityEnum(str, enum.Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"

class VulnStatusEnum(str, enum.Enum):
    UNPATCHED = "UNPATCHED"
    PATCHED = "PATCHED"
    MITIGATED = "MITIGATED"
    MONITORING = "MONITORING"

# ============================================================================
# Tables
# ============================================================================

class Organization(Base):
    __tablename__ = "organizations"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = relationship("User", back_populates="organization")
    incidents = relationship("Incident", back_populates="organization")
    vulnerabilities = relationship("Vulnerability", back_populates="organization")

class User(Base):
    __tablename__ = "users"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    org_id = Column(PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    email = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRoleEnum), default=UserRoleEnum.VIEWER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization = relationship("Organization", back_populates="users")
    incidents_created = relationship("Incident", foreign_keys="[Incident.created_by]")
    incidents_assigned = relationship("Incident", foreign_keys="[Incident.assigned_to]")
    comments = relationship("Comment", back_populates="author")

class Incident(Base):
    __tablename__ = "incidents"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    org_id = Column(PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(SQLEnum(IncidentSeverityEnum), default=IncidentSeverityEnum.MEDIUM)
    status = Column(SQLEnum(IncidentStatusEnum), default=IncidentStatusEnum.OPEN)
    incident_type = Column(SQLEnum(IncidentTypeEnum), default=IncidentTypeEnum.OTHER)
    created_by = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    assigned_to = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    affected_systems = Column(ARRAY(String), default=[])
    external_reference_id = Column(String(255), nullable=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="incidents")
    comments = relationship("Comment", back_populates="incident", cascade="all, delete-orphan")
    vulnerabilities = relationship("Vulnerability", secondary="incident_vulnerabilities", back_populates="incidents")

class Vulnerability(Base):
    __tablename__ = "vulnerabilities"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    org_id = Column(PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    cve_id = Column(String(50), unique=True, nullable=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    cvss_score = Column(Numeric(3, 1), nullable=True)
    cvss_vector = Column(String(255), nullable=True)
    severity = Column(SQLEnum(VulnSeverityEnum), default=VulnSeverityEnum.MEDIUM)
    status = Column(SQLEnum(VulnStatusEnum), default=VulnStatusEnum.UNPATCHED)
    source = Column(String(50), default="manual")
    affected_systems = Column(ARRAY(String), default=[])
    remediation = Column(Text, nullable=True)
    discovered_date = Column(DateTime, default=datetime.utcnow)
    patch_available_date = Column(DateTime, nullable=True)
    patched_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="vulnerabilities")
    incidents = relationship("Incident", secondary="incident_vulnerabilities", back_populates="vulnerabilities")

class IncidentVulnerability(Base):
    __tablename__ = "incident_vulnerabilities"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    incident_id = Column(PG_UUID(as_uuid=True), ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False)
    vulnerability_id = Column(PG_UUID(as_uuid=True), ForeignKey("vulnerabilities.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    incident_id = Column(PG_UUID(as_uuid=True), ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False)
    author_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    incident = relationship("Incident", back_populates="comments")
    author = relationship("User", back_populates="comments")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    org_id = Column(PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    action = Column(String(50), nullable=False)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(PG_UUID(as_uuid=True), nullable=False)
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

class ApiKey(Base):
    __tablename__ = "api_keys"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    org_id = Column(PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    key_hash = Column(String(255), nullable=False, unique=True)
    last_used_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)

class Webhook(Base):
    __tablename__ = "webhooks"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    org_id = Column(PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    url = Column(String(500), nullable=False)
    events = Column(ARRAY(String), default=[])
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class NotificationPreference(Base):
    __tablename__ = "notification_preferences"
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    org_id = Column(PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    email_on_new_incident = Column(Boolean, default=True)
    email_on_critical_vulnerability = Column(Boolean, default=True)
    email_on_incident_update = Column(Boolean, default=True)
    email_digest = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
class Alert(Base):
    __tablename__ = "alerts"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    org_id = Column(PG_UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    incident_id = Column(PG_UUID(as_uuid=True), ForeignKey("incidents.id"), nullable=True)
    message = Column(Text, nullable=False)
    alert_type = Column(String(50), nullable=True)  # e.g., "email", "system"
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization = relationship("Organization")
    user = relationship("User")
    incident = relationship("Incident")
