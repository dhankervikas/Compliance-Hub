"""
FastAPI Integration for Policy Generation
=========================================
RESTful API endpoints for policy generation, validation, and management
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
import os

from ai_policy_service import PolicyGenerationService
from policy_intents import POLICY_CONTROL_MAP, get_policy_intents, validate_policy_coverage
from policy_template_structure import PolicyTemplateStructure


# Pydantic Models
class PolicyGenerationRequest(BaseModel):
    policy_name: str = Field(..., description="Name of the policy to generate")
    company_name: str = Field(default="AssuRisk", description="Organization name")
    temperature: float = Field(default=0.3, ge=0.0, le=1.0, description="AI creativity level")

class BatchGenerationRequest(BaseModel):
    policy_names: List[str] = Field(..., description="List of policy names to generate")
    company_name: str = Field(default="AssuRisk", description="Organization name")

class SectionRegenerationRequest(BaseModel):
    policy_name: str
    section_name: str
    current_content: str
    feedback: Optional[str] = None

class PolicyValidationRequest(BaseModel):
    policy_name: str
    content: str

class PolicyListResponse(BaseModel):
    total: int
    policies: List[Dict]
    categories: Dict[str, List[str]]

class PolicyGenerationResponse(BaseModel):
    success: bool
    policy_name: str
    content: Optional[str] = None
    metadata: Optional[Dict] = None
    validation: Optional[Dict] = None
    intent_coverage: Optional[Dict] = None
    error: Optional[str] = None


# Initialize router
router = APIRouter(prefix="/api/policies", tags=["Policy Generation"])

# Initialize service (will use env var for API key)
policy_service = PolicyGenerationService()


@router.get("/list", response_model=PolicyListResponse)
async def list_all_policies():
    """
    Returns a list of all available policies that can be generated
    """
    # Categorize policies
    categories = {
        "Context & Scope": ["ISMS Scope", "Context of the Organization", "Interested Parties"],
        "Leadership": ["Information Security Policy", "Management Commitment Statement", "ISMS Roles and Responsibilities"],
        "Planning": ["Risk Assessment Methodology", "Risk Treatment Plan", "Statement of Applicability (SoA)", "Information Security Objectives"],
        "Support": ["Competence and Awareness Policy", "Information Security Training Program", "Document Control Procedure"],
        "Access Control": ["Access Control Policy", "Password Policy", "Privileged Access Rights"],
        "Asset Management": ["Asset Management Policy", "Data Classification Policy", "Acceptable Use Policy"],
        "Business Continuity": ["Business Continuity Policy", "Backup and Recovery Policy"],
        "Incident Management": ["Incident Response Policy", "Incident Management", "Information Security Event Reporting"],
        "Network & Systems": ["Network Security Policy", "Vulnerability Management Policy", "Configuration Management", "Change Management Policy"],
        "Physical Security": ["Physical Security Policy", "Physical Entry Controls", "Desk and Screen Policy"],
        "Development": ["Secure Development Policy", "Testing", "Separation of Environments"],
        "Third Party": ["Third-Party Security Policy", "Supplier Security Agreements", "ICT Supply Chain Management"],
        "Cryptography": ["Cryptography Policy", "Secure Authentication"],
        "Mobile & Remote": ["Mobile Device Policy", "Remote Access Policy", "Teleworking"],
        "Compliance": ["Legal and Compliance Requirements", "Independent Review"]
    }
    
    policies_list = []
    for policy_name, controls in POLICY_CONTROL_MAP.items():
        intents = get_policy_intents(policy_name)
        policies_list.append({
            "name": policy_name,
            "controls": controls,
            "has_intents": len(intents) > 0,
            "description": intents.get("description", "")
        })
    
    return {
        "total": len(POLICY_CONTROL_MAP),
        "policies": policies_list,
        "categories": categories
    }


@router.post("/generate", response_model=PolicyGenerationResponse)
async def generate_policy(request: PolicyGenerationRequest):
    """
    Generates a single policy with AI
    """
    try:
        result = policy_service.generate_policy(
            policy_name=request.policy_name,
            company_name=request.company_name,
            temperature=request.temperature
        )
        return PolicyGenerationResponse(**result)
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@router.post("/generate/batch")
async def generate_policies_batch(request: BatchGenerationRequest, background_tasks: BackgroundTasks):
    """
    Generates multiple policies in batch (runs in background)
    """
    # Validate all policy names exist
    invalid_policies = [p for p in request.policy_names if p not in POLICY_CONTROL_MAP]
    if invalid_policies:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid policy names: {', '.join(invalid_policies)}"
        )
    
    # Start batch generation in background
    job_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # TODO: Implement proper background job tracking with database
    # For now, just return job ID
    
    return {
        "job_id": job_id,
        "status": "started",
        "total_policies": len(request.policy_names),
        "message": "Batch generation started in background"
    }


@router.post("/validate")
async def validate_policy_content(request: PolicyValidationRequest):
    """
    Validates policy content against requirements
    """
    # Check if policy exists
    if request.policy_name not in POLICY_CONTROL_MAP:
        raise HTTPException(status_code=400, detail=f"Unknown policy: {request.policy_name}")
    
    # Validate structure
    validation = policy_service._validate_generated_policy(request.policy_name, request.content)
    
    # Check intent coverage
    coverage = validate_policy_coverage(request.policy_name, request.content)
    
    return {
        "policy_name": request.policy_name,
        "structure_validation": validation,
        "intent_coverage": coverage,
        "overall_status": "audit_ready" if (validation["valid"] and coverage["audit_ready"]) else "needs_review"
    }


@router.post("/regenerate/section")
async def regenerate_section(request: SectionRegenerationRequest):
    """
    Regenerates a specific section of a policy
    """
    try:
        new_section = policy_service.regenerate_section(
            policy_name=request.policy_name,
            section_name=request.section_name,
            current_content=request.current_content,
            feedback=request.feedback
        )
        
        return {
            "success": True,
            "section_name": request.section_name,
            "regenerated_content": new_section
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Regeneration failed: {str(e)}")


@router.get("/intents/{policy_name}")
async def get_policy_requirements(policy_name: str):
    """
    Returns the specific requirements and intents for a policy
    """
    if policy_name not in POLICY_CONTROL_MAP:
        raise HTTPException(status_code=404, detail=f"Policy not found: {policy_name}")
    
    intents = get_policy_intents(policy_name)
    controls = POLICY_CONTROL_MAP.get(policy_name, [])
    
    if not intents:
        return {
            "policy_name": policy_name,
            "controls": controls,
            "intents_defined": False,
            "message": "No specific intents defined for this policy yet"
        }
    
    return {
        "policy_name": policy_name,
        "controls": controls,
        "intents_defined": True,
        "description": intents.get("description"),
        "mandatory_elements": intents.get("mandatory_elements", []),
        "section_requirements": intents.get("section_specific_requirements", {}),
        "audit_evidence": intents.get("audit_evidence_needed", [])
    }


@router.get("/template/structure")
async def get_template_structure():
    """
    Returns the 10-section policy template structure
    """
    return {
        "sections": PolicyTemplateStructure.SECTIONS,
        "metadata_requirements": PolicyTemplateStructure.METADATA_REQUIREMENTS,
        "quality_checks": PolicyTemplateStructure.AUDIT_QUALITY_CHECKS,
        "markdown_template": PolicyTemplateStructure.get_markdown_template()
    }


@router.get("/statistics")
async def get_statistics():
    """
    Returns statistics about policy coverage and generation status
    """
    total_policies = len(POLICY_CONTROL_MAP)
    policies_with_intents = len([p for p in POLICY_CONTROL_MAP.keys() if get_policy_intents(p)])
    
    # Control coverage
    all_controls = set()
    for controls in POLICY_CONTROL_MAP.values():
        all_controls.update(controls)
    
    iso_controls = len([c for c in all_controls if c.startswith('ISO_') or c.startswith('A.')])
    soc_controls = len([c for c in all_controls if c.startswith('CC')])
    
    return {
        "total_policies": total_policies,
        "policies_with_intents": policies_with_intents,
        "intent_coverage_percentage": round((policies_with_intents / total_policies) * 100, 1),
        "unique_controls_covered": len(all_controls),
        "iso_27001_controls": iso_controls,
        "soc_2_controls": soc_controls,
        "ready_for_generation": policies_with_intents
    }


# Health check endpoint
@router.get("/health")
async def health_check():
    """
    Checks if the policy generation service is operational
    """
    api_key = os.getenv("GEMINI_API_KEY")
    
    return {
        "status": "healthy" if api_key else "misconfigured",
        "gemini_api_configured": bool(api_key),
        "total_policies": len(POLICY_CONTROL_MAP),
        "service": "Policy Generation Service",
        "version": "1.0.0"
    }


# Example integration with existing FastAPI app:
"""
In your main.py or app.py:

from fastapi import FastAPI
from api_integration import router as policy_router

app = FastAPI()

# Include the policy generation router
app.include_router(policy_router)

# Your other routes...
"""
