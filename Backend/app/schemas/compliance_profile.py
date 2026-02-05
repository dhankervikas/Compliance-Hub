from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import List, Optional, Dict, Literal, Union
from datetime import date, datetime

# -------------------------------------------------------------------
# 1. Organization Profile
# -------------------------------------------------------------------
class OrgContacts(BaseModel):
    exec_sponsor: Optional[str] = None
    security_owner: Optional[str] = None
    it_owner: Optional[str] = None

class OrgProfile(BaseModel):
    legal_name: str = Field(..., description="Legal entity name")
    dba: Optional[str] = None
    address: Optional[str] = None
    industry: Optional[str] = None
    headcount: Optional[Literal["<10", "10-50", "50-200", "200+"]] = None
    contacts: Optional[OrgContacts] = None
    support_model: Optional[Literal["Business Hours", "24x7"]] = None

# -------------------------------------------------------------------
# 2. ISMS / Scope
# -------------------------------------------------------------------
class ScopeProfile(BaseModel):
    scope_statement: Optional[str] = Field(None, description="The official ISMS scope statement")
    locations: List[str] = []
    products_in_scope: List[str] = []
    exclusions: List[str] = []
    frameworks: List[str] = []
    
    # SOC 2 Specific Scoping
    soc2_selected_principles: List[str] = ["Security"] # Default to Common Criteria
    soc2_exclusions: Dict[str, str] = {} # Key: Principle, Value: Justification

# -------------------------------------------------------------------
# 3. Technology & Hosting
# -------------------------------------------------------------------
class TechStackProfile(BaseModel):
    hosting_model: Optional[Literal["Cloud-Native", "Hybrid", "On-Prem"]] = None
    cloud_providers: List[Literal["AWS", "Azure", "GCP", "DigitalOcean", "Heroku", "Vercel"]] = []
    idp_tool: Optional[str] = None
    ticketing_tool: Optional[str] = None
    endpoint_management: Optional[str] = None
    siem_tool: Optional[str] = None
    vuln_scanner: Optional[str] = None
    code_repos: List[str] = []

# -------------------------------------------------------------------
# 4. Data & Privacy
# -------------------------------------------------------------------
class RetentionRule(BaseModel):
    data_type: str
    years: int

class DataPrivacyProfile(BaseModel):
    data_types: List[Literal["PII", "PHI", "PCI", "Customer Confidential", "Employee Data", "Public"]] = []
    classification_levels: List[str] = ["Public", "Internal", "Confidential", "Restricted"]
    retention_periods: List[RetentionRule] = []
    encryption_at_rest: Optional[str] = None
    encryption_in_transit: Optional[str] = None
    regions: List[str] = []
    cross_border_transfers: bool = False

# -------------------------------------------------------------------
# 5. Access & Identity
# -------------------------------------------------------------------
class MFAPolicy(BaseModel):
    who: str = "All Users"
    enforcement: Literal["Strict", "Optional", "Risk-Based"] = "Strict"

class AccessProfile(BaseModel):
    identity_provider: Optional[str] = None
    mfa_policy: Optional[MFAPolicy] = None
    access_review_frequency: Optional[Literal["Monthly", "Quarterly", "Semi-Annual", "Annual"]] = None
    privileged_access_tool: Optional[str] = None
    onboarding_workflow: Optional[str] = None

# -------------------------------------------------------------------
# 6. People & HR
# -------------------------------------------------------------------
class HRProfile(BaseModel):
    background_checks: bool = False
    background_check_roles: str = "All Employees"
    training_frequency: Optional[Literal["Onboarding", "Annual", "Quarterly"]] = None
    remote_work_policy: Optional[Literal["Allowed", "Hybrid", "Restricted"]] = None
    device_policy: Optional[Literal["MDM Required", "BYOD Allowed", "Company Issued Only"]] = None

# -------------------------------------------------------------------
# 7. Vendors
# -------------------------------------------------------------------
class VendorProfile(BaseModel):
    risk_tiering_method: Optional[Literal["Simple", "Advanced"]] = None
    critical_vendors: List[str] = []
    review_frequency: Optional[Literal["Annual", "Contract Renewal"]] = None

# -------------------------------------------------------------------
# 8. SecOps
# -------------------------------------------------------------------
class PatchCadence(BaseModel):
    workstation: str = "Auto"
    server: str = "30 days"
    critical_vuln: str = "24 hours"

class SecOpsProfile(BaseModel):
    incident_severity_levels: List[str] = ["Sev1 (Critical)", "Sev2 (High)", "Sev3 (Medium)", "Sev4 (Low)"]
    incident_response_contacts: List[str] = []
    vuln_scan_frequency: Optional[str] = None
    patch_cadence: Optional[PatchCadence] = None
    backup_frequency: Optional[str] = None
    restore_test_frequency: Optional[str] = None
    logging_tool: Optional[str] = None

# -------------------------------------------------------------------
# 9. Business Continuity
# -------------------------------------------------------------------
class BCPProfile(BaseModel):
    rto_target: Optional[str] = "24 hours"
    rpo_target: Optional[str] = "1 hour"
    dr_strategy: Optional[Literal["Multi-Region", "Warm Standby", "Backup Restore", "Active-Active"]] = None
    test_frequency: Optional[Literal["Annual", "Semi-Annual"]] = None
    crisis_comms_owner: Optional[str] = None

# -------------------------------------------------------------------
# 10. Document Preferences
# -------------------------------------------------------------------
class DocPreferences(BaseModel):
    style: Optional[Literal["Policy", "Procedure", "Hybrid"]] = None
    tone: Optional[Literal["Formal", "Standard", "Simple"]] = None
    review_period: Optional[Literal["Annual", "Semi-Annual"]] = "Annual"
    approval_role: str = "CISO"

# -------------------------------------------------------------------
# Generic Wrapper
# -------------------------------------------------------------------
class SettingsUpdate(BaseModel):
    section: Literal[
        "org_profile", "scope", "tech_stack", "data_privacy", 
        "access_identity", "hr_security", "vendors", "sec_ops", 
        "bcp_dr", "doc_preferences"
    ]
    content: Dict # Flexible payload, validated in logic layer if needed, or by Pydantic Generic logic
    

class SettingsResponse(BaseModel):
    section: str
    content: Dict # Flexible response to avoid Union matching issues on empty dicts
    updated_at: Optional[datetime]
    completeness_score: int

