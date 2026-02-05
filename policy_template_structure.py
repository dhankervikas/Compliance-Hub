"""
AssuRisk Policy Template Structure
===================================
Defines the 10-section audit-ready policy format that ensures ISO 27001:2022 
and SOC 2 compliance.
"""

from typing import Dict, List, Optional
from datetime import datetime

class PolicyTemplateStructure:
    """
    Standard 10-section policy template structure that meets auditor requirements.
    This structure is based on ISO 27001:2022 Annex A controls and SOC 2 common criteria.
    """
    
    SECTIONS = {
        "1_purpose": {
            "title": "1. Purpose",
            "description": "Why this policy exists and its compliance objectives",
            "required_elements": [
                "Primary objective of the policy",
                "Regulatory/framework alignment (ISO 27001, SOC 2, etc.)",
                "Business justification",
                "Scope boundary definition"
            ],
            "min_paragraphs": 2,
            "audit_keywords": ["objective", "compliance", "purpose", "ensure"]
        },
        "2_scope": {
            "title": "2. Scope",
            "description": "What and who this policy applies to",
            "required_elements": [
                "Organizational units covered",
                "Information assets included",
                "Systems and processes in scope",
                "Geographic/jurisdictional boundaries",
                "Exclusions (if any) with justification"
            ],
            "min_paragraphs": 2,
            "audit_keywords": ["applies to", "includes", "covers", "within"]
        },
        "3_definitions": {
            "title": "3. Definitions",
            "description": "Key terms and their meanings",
            "required_elements": [
                "Technical terms specific to this policy",
                "Role definitions",
                "Asset classifications",
                "Abbreviations and acronyms"
            ],
            "format": "list",
            "audit_keywords": ["means", "defined as", "refers to"]
        },
        "4_roles_responsibilities": {
            "title": "4. Roles and Responsibilities",
            "description": "Who is accountable for what",
            "required_elements": [
                "Executive ownership (CISO, CTO, etc.)",
                "Implementation responsibilities",
                "Operational duties",
                "Monitoring and review roles",
                "Escalation paths"
            ],
            "format": "structured_list",
            "min_roles": 3,
            "audit_keywords": ["responsible for", "accountable", "shall", "must"]
        },
        "5_policy_statements": {
            "title": "5. Policy Statements",
            "description": "The core requirements and rules",
            "required_elements": [
                "Mandatory controls (SHALL/MUST statements)",
                "Recommended practices (SHOULD statements)",
                "Prohibited activities (SHALL NOT/MUST NOT)",
                "Specific technical/procedural requirements"
            ],
            "critical": True,
            "min_statements": 5,
            "audit_keywords": ["shall", "must", "required", "prohibited", "mandatory"]
        },
        "6_procedures": {
            "title": "6. Procedures and Implementation",
            "description": "How the policy is operationalized",
            "required_elements": [
                "Step-by-step implementation guidance",
                "Technical controls to be deployed",
                "Workflow and approval processes",
                "Documentation requirements",
                "Integration with existing systems"
            ],
            "min_paragraphs": 3,
            "audit_keywords": ["procedure", "process", "implement", "perform"]
        },
        "7_exceptions": {
            "title": "7. Exceptions and Deviations",
            "description": "How to handle non-compliance scenarios",
            "required_elements": [
                "Exception request process",
                "Approval authority",
                "Risk assessment requirements",
                "Temporary vs. permanent exceptions",
                "Documentation and tracking",
                "Review frequency for exceptions"
            ],
            "min_paragraphs": 2,
            "audit_keywords": ["exception", "deviation", "approval", "justified"]
        },
        "8_compliance_monitoring": {
            "title": "8. Compliance and Monitoring",
            "description": "How compliance is verified and enforced",
            "required_elements": [
                "Monitoring mechanisms (automated/manual)",
                "Audit frequency and scope",
                "Key Performance Indicators (KPIs)",
                "Reporting requirements",
                "Non-compliance consequences",
                "Corrective action procedures"
            ],
            "min_paragraphs": 2,
            "audit_keywords": ["monitor", "audit", "review", "compliance", "measure"]
        },
        "9_enforcement": {
            "title": "9. Enforcement and Violations",
            "description": "Consequences of policy breaches",
            "required_elements": [
                "Violation categories (minor, major, critical)",
                "Disciplinary actions",
                "Legal/contractual implications",
                "Incident response linkage",
                "Remediation requirements"
            ],
            "min_paragraphs": 2,
            "audit_keywords": ["violation", "breach", "disciplinary", "consequence"]
        },
        "10_review_maintenance": {
            "title": "10. Policy Review and Maintenance",
            "description": "How the policy stays current",
            "required_elements": [
                "Review frequency (minimum annually)",
                "Review triggers (incidents, regulatory changes, etc.)",
                "Approval workflow for updates",
                "Version control procedures",
                "Communication of changes",
                "Archival of previous versions"
            ],
            "min_paragraphs": 2,
            "audit_keywords": ["review", "update", "maintain", "version", "annual"]
        }
    }
    
    METADATA_REQUIREMENTS = {
        "document_id": "Unique identifier (e.g., POL-ISMS-001)",
        "version": "Semantic versioning (e.g., 1.0.0)",
        "effective_date": "ISO 8601 date format",
        "next_review_date": "ISO 8601 date format (max 12 months from effective)",
        "owner": "Named individual with title",
        "approver": "Named approver with title and date",
        "classification": "Internal/Confidential/Public",
        "related_policies": "List of related document IDs",
        "related_controls": "Mapped ISO/SOC 2 controls"
    }
    
    AUDIT_QUALITY_CHECKS = [
        {
            "check": "length_adequacy",
            "rule": "Minimum 1500 words total",
            "severity": "warning"
        },
        {
            "check": "section_completeness",
            "rule": "All 10 sections present with content",
            "severity": "critical"
        },
        {
            "check": "intent_coverage",
            "rule": "All POLICY_INTENTS requirements addressed",
            "severity": "critical"
        },
        {
            "check": "control_mapping",
            "rule": "Explicit reference to mapped ISO/SOC 2 controls",
            "severity": "critical"
        },
        {
            "check": "actionable_language",
            "rule": "Contains SHALL/MUST statements (min 5)",
            "severity": "warning"
        },
        {
            "check": "measurable_requirements",
            "rule": "Includes quantifiable compliance metrics",
            "severity": "warning"
        },
        {
            "check": "version_control",
            "rule": "Metadata includes version and dates",
            "severity": "critical"
        }
    ]
    
    @staticmethod
    def get_markdown_template() -> str:
        """Returns the base Markdown template structure"""
        return """# {title}

**Document ID:** {document_id}  
**Version:** {version}  
**Effective Date:** {effective_date}  
**Next Review:** {next_review_date}  
**Owner:** {owner}  
**Classification:** {classification}

---

## 1. Purpose

{purpose_content}

## 2. Scope

{scope_content}

## 3. Definitions

{definitions_content}

## 4. Roles and Responsibilities

{roles_content}

## 5. Policy Statements

{policy_statements_content}

## 6. Procedures and Implementation

{procedures_content}

## 7. Exceptions and Deviations

{exceptions_content}

## 8. Compliance and Monitoring

{compliance_content}

## 9. Enforcement and Violations

{enforcement_content}

## 10. Policy Review and Maintenance

{review_content}

---

**Approval History:**

| Version | Date | Approved By | Changes |
|---------|------|-------------|---------|
| {version} | {effective_date} | {approver} | Initial Release |

**Related Documents:** {related_policies}  
**Mapped Controls:** {related_controls}
"""

    @staticmethod
    def validate_section(section_key: str, content: str) -> Dict[str, any]:
        """
        Validates a section against its requirements
        
        Returns:
            Dict with 'valid', 'errors', 'warnings' keys
        """
        section_def = PolicyTemplateStructure.SECTIONS.get(section_key)
        if not section_def:
            return {"valid": False, "errors": ["Unknown section"], "warnings": []}
        
        errors = []
        warnings = []
        
        # Check minimum length
        if "min_paragraphs" in section_def:
            paragraph_count = len([p for p in content.split('\n\n') if p.strip()])
            if paragraph_count < section_def["min_paragraphs"]:
                warnings.append(f"Expected {section_def['min_paragraphs']} paragraphs, found {paragraph_count}")
        
        # Check for required keywords
        content_lower = content.lower()
        keyword_found = any(kw in content_lower for kw in section_def.get("audit_keywords", []))
        if not keyword_found and section_def.get("audit_keywords"):
            warnings.append(f"Missing expected audit keywords: {section_def['audit_keywords'][:3]}")
        
        # Check for critical sections
        if section_def.get("critical") and len(content.strip()) < 200:
            errors.append("Critical section must be substantial (min 200 characters)")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
