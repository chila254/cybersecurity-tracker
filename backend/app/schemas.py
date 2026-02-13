"""
Pydantic schemas for request/response validation
"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum
from uuid import UUID

# ============================================================================
# Enums
# ============================================================================

class UserRole(str, Enum):
    ADMIN = "ADMIN"
    ANALYST = "ANALYST"
    VIEWER = "VIEWER"

class IncidentSeverity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class IncidentStatus(str, Enum):
    OPEN = "OPEN"
    INVESTIGATING = "INVESTIGATING"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"

class IncidentType(str, Enum):
    DATA_BREACH = "data_breach"
    MALWARE = "malware"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DENIAL_OF_SERVICE = "denial_of_service"
    SOCIAL_ENGINEERING = "social_engineering"
    CONFIGURATION_ERROR = "configuration_error"
    SUPPLY_CHAIN = "supply_chain"
    OTHER = "other"

class VulnSeverity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"

class VulnStatus(str, Enum):
    UNPATCHED = "UNPATCHED"
    PATCHED = "PATCHED"
    MITIGATED = "MITIGATED"
    MONITORING = "MONITORING"

# ============================================================================
# User Schemas
# ============================================================================

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str
    role: UserRole = UserRole.VIEWER

class UserUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[UserRole] = None

class UserResponse(BaseModel):
    id: UUID
    email: str
    name: str
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# ============================================================================
# Authentication Schemas
# ============================================================================

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int

# ============================================================================
# Organization Schemas
# ============================================================================

class OrganizationCreate(BaseModel):
    name: str
    description: Optional[str] = None

class OrganizationResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# ============================================================================
# Incident Schemas
# ============================================================================

class IncidentCreate(BaseModel):
    title: str
    description: str
    severity: IncidentSeverity = IncidentSeverity.MEDIUM
    incident_type: IncidentType = IncidentType.OTHER
    assigned_to: Optional[UUID] = None
    affected_systems: Optional[List[str]] = []
    external_reference_id: Optional[str] = None

class IncidentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[IncidentSeverity] = None
    status: Optional[IncidentStatus] = None
    assigned_to: Optional[UUID] = None
    affected_systems: Optional[List[str]] = None

class IncidentResponse(BaseModel):
    id: UUID
    title: str
    description: str
    severity: IncidentSeverity
    status: IncidentStatus
    incident_type: IncidentType
    created_by: UUID
    assigned_to: Optional[UUID]
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime]
    affected_systems: List[str]
    external_reference_id: Optional[str]

    model_config = ConfigDict(from_attributes=True)

# ============================================================================
# Vulnerability Schemas
# ============================================================================

class VulnerabilityCreate(BaseModel):
    cve_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    cvss_score: Optional[float] = None
    cvss_vector: Optional[str] = None
    severity: VulnSeverity = VulnSeverity.MEDIUM
    status: VulnStatus = VulnStatus.UNPATCHED
    affected_systems: Optional[List[str]] = []
    remediation: Optional[str] = None

class VulnerabilityUpdate(BaseModel):
    title: Optional[str] = None
    severity: Optional[VulnSeverity] = None
    status: Optional[VulnStatus] = None
    remediation: Optional[str] = None
    patch_available_date: Optional[datetime] = None
    patched_date: Optional[datetime] = None

class VulnerabilityResponse(BaseModel):
    id: UUID
    cve_id: Optional[str]
    title: str
    description: Optional[str]
    cvss_score: Optional[float]
    severity: VulnSeverity
    status: VulnStatus
    affected_systems: List[str]
    remediation: Optional[str]
    discovered_date: datetime
    patch_available_date: Optional[datetime]
    patched_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# ============================================================================
# Comment Schemas
# ============================================================================

class CommentCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)

class CommentResponse(BaseModel):
    id: UUID
    incident_id: UUID
    author_id: UUID
    content: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# ============================================================================
# Dashboard Schemas
# ============================================================================

class DashboardStats(BaseModel):
    total_incidents: int
    open_incidents: int
    critical_severity: int
    total_vulnerabilities: int
    unpatched_vulnerabilities: int
    incidents_this_month: int

class IncidentTrend(BaseModel):
    date: str
    count: int

class SeverityDistribution(BaseModel):
    severity: str
    count: int

class DashboardResponse(BaseModel):
    stats: DashboardStats
    incident_trends: List[IncidentTrend]
    severity_distribution: List[SeverityDistribution]
