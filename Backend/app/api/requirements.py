"""
Requirements API - Dynamic Requirements, Evidence Review, Cross-Framework Mapping & Policy Generation
Integrates with existing ai_service.py infrastructure (OpenAI GPT-4 Turbo)
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, List
from datetime import datetime
import json
import os
import shutil
import uuid

# ─── Internal Imports (adjust paths to match your project structure) ───
from app.database import get_db
from app.models import Control, Framework, Evidence
from app.services.ai_service import (
    suggest_evidence,
    analyze_document_gap,
    generate_premium_policy,
    analyze_gap,
    detect_and_redact_pii,
    generate_ai_response,
    client as ai_client,
)

router = APIRouter()

# ─── Config ───
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads", "evidence")
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. DYNAMIC REQUIREMENTS (AI-Generated, Cached in DB)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@router.get("/controls/{control_id}/requirements")
def get_requirements(
    control_id: str,
    regenerate: bool = Query(False, description="Force AI regeneration (bypasses cache)"),
    db: Session = Depends(get_db),
):
    """
    Get AI-generated requirements for a control.
    - First call: AI generates + caches in DB (~3-5 sec)
    - Subsequent calls: instant retrieval from cache
    - Pass ?regenerate=true to force fresh generation
    """
    # 1. Find the control
    control = db.query(Control).filter(Control.control_id == str(control_id)).first()
    if not control:
        raise HTTPException(status_code=404, detail=f"Control '{control_id}' not found")

    # 2. Delegate to existing ai_service.suggest_evidence (handles caching internally)
    result = suggest_evidence(
        title=control.title or "",
        description=control.description or "",
        category=control.category or "General",
        control_id=control_id,
        db=db,
        regenerate=regenerate,
    )

    return {
        "control_id": control_id,
        "control_title": control.title,
        "explanation": result.get("explanation", ""),
        "requirements": result.get("requirements", []),
        "cached": not regenerate and bool(control.ai_requirements_json),
        "generated_at": datetime.utcnow().isoformat(),
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. EVIDENCE UPLOAD + AI REVIEW
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@router.post("/controls/{control_id}/evidence/upload")
async def upload_evidence(
    control_id: str,
    file: UploadFile = File(...),
    requirement_name: Optional[str] = Form(None),
    is_confidential: bool = Form(False),
    tenant_id: str = Form("default_tenant"),
    db: Session = Depends(get_db),
):
    """
    Upload evidence file for a control + automatic AI review.
    Supports: PDF, DOCX, PNG, JPG, TXT, MD
    Returns AI analysis with PASS/FAIL verdict.
    """
    # 1. Validate control exists
    control = db.query(Control).filter(Control.control_id == str(control_id)).first()
    if not control:
        raise HTTPException(status_code=404, detail=f"Control '{control_id}' not found")

    # 2. Save file to disk
    file_ext = file.filename.split(".")[-1].lower() if file.filename else "bin"
    safe_filename = f"{control_id}_{uuid.uuid4().hex[:8]}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 3. Get cached requirements for context
    requirements = []
    if control.ai_requirements_json:
        try:
            requirements = json.loads(control.ai_requirements_json)
        except json.JSONDecodeError:
            pass

    # 4. Run AI Evidence Review (reuses existing analyze_document_gap)
    ai_review = analyze_document_gap(
        control_title=control.title or control_id,
        requirements=requirements,
        file_path=file_path,
        is_confidential=is_confidential,
    )

    # 5. Optional: PII scan
    pii_result = None
    if not is_confidential:
        try:
            if file_ext in ["png", "jpg", "jpeg"]:
                import base64
                with open(file_path, "rb") as f:
                    img_b64 = base64.b64encode(f.read()).decode("utf-8")
                pii_result = detect_and_redact_pii(
                    text_content="", is_image=True, file_ext=file_ext, image_base64=img_b64
                )
            elif file_ext in ["pdf", "docx", "txt", "md"]:
                # Extract text for PII check (lightweight re-read)
                text_snippet = ""
                if file_ext == "txt" or file_ext == "md":
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        text_snippet = f.read()[:5000]
                pii_result = detect_and_redact_pii(
                    text_content=text_snippet, is_image=False
                ) if text_snippet else None
        except Exception as e:
            print(f"PII scan skipped: {e}")

    # 6. Save evidence record to DB
    evidence_record = Evidence(
        control_id=control.id,
        filename=file.filename,
        title=requirement_name or file.filename,
        file_path=file_path,
        file_type=file_ext,
        file_size=os.path.getsize(file_path),
        tenant_id=tenant_id,
        status=ai_review.get("final_verdict", "pending").lower(),
        validation_source="manual",
    )
    db.add(evidence_record)
    db.commit()
    db.refresh(evidence_record)

    return {
        "evidence_id": evidence_record.id,
        "file_name": file.filename,
        "control_id": control_id,
        "ai_review": ai_review,
        "pii_scan": pii_result,
        "requirement_name": requirement_name,
        "uploaded_at": evidence_record.created_at.isoformat() if evidence_record.created_at else None,
    }


@router.get("/controls/{control_id}/evidence")
def get_evidence_list(
    control_id: str,
    db: Session = Depends(get_db),
):
    """List all evidence uploaded for a control."""
    control = db.query(Control).filter(Control.control_id == str(control_id)).first()
    if not control:
        raise HTTPException(status_code=404, detail=f"Control '{control_id}' not found")

    evidence_list = db.query(Evidence).filter(Evidence.control_id == control.id).all()

    return {
        "control_id": control_id,
        "count": len(evidence_list),
        "evidence": [
            {
                "id": e.id,
                "file_name": e.filename,
                "file_type": e.file_type,
                "uploaded_at": e.created_at.isoformat() if e.created_at else None,
                "ai_review_status": (e.status or "pending").upper(),
                "ai_review": None,
            }
            for e in evidence_list
        ],
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. CROSS-FRAMEWORK EVIDENCE MAPPING
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@router.get("/controls/{control_id}/cross-framework")
def get_cross_framework_mapping(
    control_id: str,
    db: Session = Depends(get_db),
):
    """
    Find all controls across frameworks that share the same universal intent.
    Upload evidence once → satisfies multiple frameworks automatically.
    """
    control = db.query(Control).filter(Control.control_id == str(control_id)).first()
    if not control:
        raise HTTPException(status_code=404, detail=f"Control '{control_id}' not found")

    # Strategy: Use raw SQL for the crosswalk join since model relationships may vary
    # This query finds controls sharing the same intent via the crosswalk table
    related_controls = []

    try:
        query = text("""
            SELECT DISTINCT
                c.control_id,
                c.title,
                c.status,
                f.name AS framework_name,
                f.id AS framework_id,
                ui.name AS intent_name,
                ui.id AS intent_id
            FROM intent_framework_crosswalk ifc1
            JOIN intent_framework_crosswalk ifc2 
                ON ifc1.intent_id = ifc2.intent_id 
                AND ifc1.control_reference != ifc2.control_reference
            JOIN controls c ON c.control_id = ifc2.control_reference
            JOIN frameworks f ON c.framework_id = f.id
            JOIN universal_intents ui ON ui.id = ifc1.intent_id
            WHERE ifc1.control_reference = :control_id
            ORDER BY f.name, c.control_id
        """)

        result = db.execute(query, {"control_id": control_id}).fetchall()

        for row in result:
            related_controls.append({
                "control_id": row.control_id,
                "title": row.title,
                "status": row.status,
                "framework_name": row.framework_name,
                "framework_id": row.framework_id,
                "shared_intent": row.intent_name,
                "intent_id": row.intent_id,
            })

    except Exception as e:
        print(f"Cross-framework query error: {e}")
        # Fallback: return empty with error context
        return {
            "control_id": control_id,
            "related_controls": [],
            "total_frameworks_impacted": 0,
            "note": f"Crosswalk query failed: {str(e)}. Verify intent_framework_crosswalk table exists.",
        }

    # Deduplicate frameworks
    frameworks_impacted = list({rc["framework_name"] for rc in related_controls})

    return {
        "control_id": control_id,
        "control_title": control.title,
        "related_controls": related_controls,
        "total_related": len(related_controls),
        "frameworks_impacted": frameworks_impacted,
        "total_frameworks_impacted": len(frameworks_impacted),
    }


@router.post("/controls/{control_id}/evidence/{evidence_id}/apply-cross-framework")
def apply_evidence_cross_framework(
    control_id: str,
    evidence_id: int,
    db: Session = Depends(get_db),
):
    """
    Apply an uploaded evidence file to all cross-framework related controls.
    This creates evidence links so one upload satisfies multiple frameworks.
    """
    # 1. Get source evidence
    source_evidence = db.query(Evidence).filter(Evidence.id == evidence_id).first()
    if not source_evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")

    # 2. Get related controls
    mapping = get_cross_framework_mapping(control_id, db)
    related = mapping.get("related_controls", [])

    applied_to = []
    for rc in related:
        target_control = db.query(Control).filter(
            Control.control_id == rc["control_id"]
        ).first()
        if not target_control:
            continue

        # Check if evidence already linked to this control
        existing = db.query(Evidence).filter(
            Evidence.control_id == target_control.id,
            Evidence.file_path == source_evidence.file_path,
        ).first()

        if existing:
            continue  # Skip duplicates

        # Create linked evidence record
        linked_evidence = Evidence(
            control_id=target_control.id,
            filename=source_evidence.filename,
            title=source_evidence.title,
            file_path=source_evidence.file_path,
            file_type=source_evidence.file_type,
            file_size=source_evidence.file_size,
            tenant_id=source_evidence.tenant_id or "default_tenant",
            status=source_evidence.status or "pending",
            validation_source="automated_agent",
        )
        db.add(linked_evidence)
        applied_to.append({
            "control_id": rc["control_id"],
            "framework": rc["framework_name"],
        })

    db.commit()

    return {
        "source_control": control_id,
        "evidence_id": evidence_id,
        "applied_to": applied_to,
        "total_applied": len(applied_to),
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4. POLICY GENERATOR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@router.post("/controls/{control_id}/generate-policy")
def generate_policy(
    control_id: str,
    policy_name: Optional[str] = Form(None),
    company_name: Optional[str] = Form("Our Organization"),
    industry: Optional[str] = Form("Technology"),
    policy_owner: Optional[str] = Form("Chief Information Security Officer"),
    policy_approver: Optional[str] = Form("Board of Directors"),
    db: Session = Depends(get_db),
):
    """
    Generate an audit-ready policy document for a control using AI.
    Returns professional Markdown content ready for PDF/Word export.
    """
    control = db.query(Control).filter(Control.control_id == str(control_id)).first()
    if not control:
        raise HTTPException(status_code=404, detail=f"Control '{control_id}' not found")

    # Build company profile for context
    company_profile = {
        "Company Name": company_name,
        "Industry": industry,
        "Policy Owner": policy_owner,
        "Policy Approver": policy_approver,
        "Framework": "ISO 27001:2022",
        "Control Reference": control_id,
    }

    # Default policy name if not provided
    if not policy_name:
        policy_name = f"{control.title} Policy" if control.title else f"Control {control_id} Policy"

    # Use existing generate_premium_policy from ai_service
    policy_content = generate_premium_policy(
        control_title=control.title or control_id,
        policy_name=policy_name,
        company_profile=company_profile,
        control_description=control.description or "",
    )

    return {
        "control_id": control_id,
        "policy_name": policy_name,
        "content": policy_content,
        "generated_at": datetime.utcnow().isoformat(),
        "status": "draft",
        "company_profile": company_profile,
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 5. GAP ANALYSIS (Bulk)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@router.get("/controls/{control_id}/gap-analysis")
def run_gap_analysis(
    control_id: str,
    db: Session = Depends(get_db),
):
    """
    Run gap analysis: compare uploaded evidence against requirements.
    Returns MET / PARTIAL / NOT_MET status.
    """
    control = db.query(Control).filter(Control.control_id == str(control_id)).first()
    if not control:
        raise HTTPException(status_code=404, detail=f"Control '{control_id}' not found")

    # Get requirements
    requirements = []
    if control.ai_requirements_json:
        try:
            requirements = json.loads(control.ai_requirements_json)
        except json.JSONDecodeError:
            pass

    # Get uploaded evidence files
    evidence_list = db.query(Evidence).filter(Evidence.control_id == control.id).all()
    uploaded_files = [e.filename for e in evidence_list if e.filename]

    # Run AI gap analysis using existing function
    gap_result = analyze_gap(
        control_title=control.title or control_id,
        requirements=requirements,
        uploaded_files=uploaded_files,
    )

    return {
        "control_id": control_id,
        "control_title": control.title,
        "status": gap_result.get("status", "NOT_MET"),
        "missing_items": gap_result.get("missing_items", []),
        "reasoning": gap_result.get("reasoning", ""),
        "evidence_count": len(evidence_list),
        "requirements_count": len(requirements),
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 6. COMPLIANCE DASHBOARD SUMMARY
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@router.get("/frameworks/{framework_id}/compliance-summary")
def get_compliance_summary(
    framework_id: int,
    db: Session = Depends(get_db),
):
    """
    Get overall compliance summary for a framework.
    Shows: total controls, evidence coverage, AI review pass rate.
    """
    framework = db.query(Framework).filter(Framework.id == framework_id).first()
    if not framework:
        raise HTTPException(status_code=404, detail="Framework not found")

    controls = db.query(Control).filter(Control.framework_id == framework_id).all()

    total = len(controls)
    with_requirements = 0
    with_evidence = 0
    statuses = {"implemented": 0, "in_progress": 0, "not_started": 0, "other": 0}

    for c in controls:
        if c.ai_requirements_json:
            try:
                reqs = json.loads(c.ai_requirements_json)
                if len(reqs) > 0:
                    with_requirements += 1
            except json.JSONDecodeError:
                pass

        ev_count = db.query(Evidence).filter(Evidence.control_id == c.id).count()
        if ev_count > 0:
            with_evidence += 1

        status = (c.status or "not_started").lower()
        if status in statuses:
            statuses[status] += 1
        else:
            statuses["other"] += 1

    return {
        "framework_id": framework_id,
        "framework_name": framework.name,
        "total_controls": total,
        "controls_with_requirements": with_requirements,
        "controls_with_evidence": with_evidence,
        "evidence_coverage_pct": round((with_evidence / total) * 100, 1) if total > 0 else 0,
        "status_breakdown": statuses,
        "compliance_score": round((statuses["implemented"] / total) * 100, 1) if total > 0 else 0,
    }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 7. HEALTH CHECK
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@router.get("/ai/health")
def ai_health_check():
    """Check if AI service is operational."""
    return {
        "ai_available": ai_client is not None,
        "provider": "openai" if ai_client else None,
        "model": "gpt-4-turbo" if ai_client else None,
        "timestamp": datetime.utcnow().isoformat(),
    }
