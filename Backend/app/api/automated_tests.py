from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from app.database import get_db
from app.models.control import Control
from app.api.auth import get_current_user
from app.tests.control_tests import run_control_test, run_all_tests, CONTROL_TESTS

router = APIRouter(
        tags=["Automated Tests"]
)

from app.collectors.base import EvidenceData
from app.collectors.system import PasswordPolicyCollector
from app.models.evidence import Evidence
import json

# Rich Metadata for Tests (Simulated for Demo)
TEST_DEFINITIONS = {
    "CC6.1": {
        "name": "MFA Enabled for All Users",
        "description": "Ensure multi-factor authentication is enforced for all user accounts.",
        "remediation": "1. Go to Identity Provider.\n2. Enforce MFA policy for 'Everyone'.",
        "owner": "IT Security"
    },
    "CC6.1.1": { 
        "name": "Password Complexity Check",
        "description": "Verify that local password policies meet minimum length and complexity.",
        "remediation": "Update Windows Group Policy or IAM settings.",
        "owner": "SysAdmin"
    },
    "CC7.1": {
        "name": "Vulnerability Scan",
        "description": "Ensure vulnerability scanning is active on all production instances.",
        "remediation": "Deploy Inspector agent to all EC2 instances.",
        "owner": "DevOps"
    },
    "CC8.1": {
        "name": "Database Encryption",
        "description": "Verify RDS instances are encrypted at rest.",
        "remediation": "Enable encryption on the RDS instance.",
        "owner": "Data Team"
    }
}


# Collector Registry - Map Controls to Collectors
# In a larger app, this would be a dynamic registry class.
COLLECTORS = [
    PasswordPolicyCollector()
]

def get_collector_for_control(control_id: str):
    for collector in COLLECTORS:
        if control_id in collector.supported_controls:
            return collector
    return None

@router.post("/run/{control_id}")
async def run_test_for_control(
    control_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Run automated collection for a specific control, save evidence, and update status.
    """
    # Get the control from database
    control = db.query(Control).filter(Control.id == control_id).first()
    if not control:
        raise HTTPException(status_code=404, detail="Control not found")
    
    # 1. Find the right collector
    collector = get_collector_for_control(control.control_id)
    
    if not collector:
        # Fallback to old simulation if defined (for backward compatibility during migration)
        test_result = run_control_test(control.control_id)
        if test_result.get("has_test"):
             # ... handle legacy simulation logic if needed or just return ...
             pass
        
        return {
            "success": False,
            "message": f"No workflow defined for control {control.control_id}",
            "control_id": control_id
        }
    
    # 2. Run Collection
    evidence_data: EvidenceData = collector.collect(control.control_id)
    
    # 3. Save Evidence to DB
    new_evidence = Evidence(
        filename=f"auto_{collector.name}_{control.control_id}.txt",
        file_path="memory", # or save to disk context
        file_size=len(evidence_data.content),
        file_type="text/plain",
        title=f"Automated Collection: {collector.name}",
        description=evidence_data.content, # Saving content in description for text evidence
        control_id=control_id,
        status="pending", # Pending AI Review
        validation_source="automated",
        uploaded_by="system"
    )
    db.add(new_evidence)
    
    # 4. Update Control Status
    if evidence_data.status == "success":
        control.status = "in_progress" # Evidence collected, waiting for AI/Manual review
        control.automation_status = "automated"
        control.last_automated_check = evidence_data.collected_at
    else:
        control.automation_status = "failed"
    
    db.commit()
    db.refresh(control)
    
    return {
        "success": evidence_data.status == "success",
        "message": "Evidence collected successfully" if evidence_data.status == "success" else f"Collection failed: {evidence_data.error}",
        "evidence_id": new_evidence.id,
        "content_preview": evidence_data.content[:200]
    }

@router.post("/run-all")
async def run_all_automated_tests(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Run all available automated collectors and update control statuses
    """
    results = []
    
    # Iterate over all registered collectors
    for collector in COLLECTORS:
        for control_id_str in collector.supported_controls:
            # Find control in database
            control = db.query(Control).filter(Control.control_id == control_id_str).first()
            if not control:
                continue
                
            # Run Collection
            evidence_data = collector.collect(control_id_str)
            
            # Save Evidence
            new_evidence = Evidence(
                filename=f"auto_{collector.name}_{control.control_id}.txt",
                file_path="memory",
                file_size=len(evidence_data.content),
                file_type="text/plain",
                title=f"Automated Collection: {collector.name}",
                description=evidence_data.content,
                control_id=control.id,
                status="pending",
                validation_source="automated",
                uploaded_by="system"
            )
            db.add(new_evidence)
            
            # Update Status
            old_status = control.status
            if evidence_data.status == "success":
                new_status = "in_progress" 
                control.status = new_status
                control.automation_status = "automated"
                control.last_automated_check = evidence_data.collected_at
            else:
                new_status = control.status
                control.automation_status = "failed"
            
            results.append({
                "control_id": control.id,
                "control_identifier": control.control_id,
                "collector": collector.name,
                "success": evidence_data.status == "success",
                "old_status": old_status,
                "new_status": new_status
            })
            
    db.commit()
    
    return {
        "success": True,
        "message": "All automated collectors executed",
        "total_run": len(results),
        "results": results
    }

@router.get("/available-tests")
async def get_available_tests(
    current_user = Depends(get_current_user)
):
    """
    Get list of controls that have automated collectors available
    """
    available_tests = []
    
    # 1. New Collectors
    for collector in COLLECTORS:
        for control_id in collector.supported_controls:
            available_tests.append({
                "control_id": control_id,
                "has_test": True,
                "type": "collector",
                "collector_name": collector.name
            })
            
    # 2. Legacy Tests (Optional, merge if needed)
    for control_id in CONTROL_TESTS.keys():
        # Avoid duplicates
        if not any(t['control_id'] == control_id for t in available_tests):
             available_tests.append({
                "control_id": control_id,
                "has_test": True,
                "type": "legacy_simulation"
            })
    
    return {
        "total_available": len(available_tests),
        "tests": available_tests
    }

@router.get("/control/{control_id}/has-test")
async def check_if_control_has_test(
    control_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Check if a specific control has an automated test available
    """
    control = db.query(Control).filter(Control.id == control_id).first()
    if not control:
        raise HTTPException(status_code=404, detail="Control not found")
    
    # Check new collectors
    has_collector = get_collector_for_control(control.control_id) is not None
    
    # Check legacy
    has_legacy = control.control_id in CONTROL_TESTS
    
    return {
        "control_id": control_id,
        "control_identifier": control.control_id,
        "has_automated_test": has_collector or has_legacy,
        "source": "collector" if has_collector else ("legacy" if has_legacy else None)
    }

@router.get("/results")
async def get_test_results(db: Session = Depends(get_db)):
    """
    Get all automated test results with rich metadata (Description, Remediation).
    """
    results = []
    
    # 1. Real System Collectors (e.g. Password Policy)
    for collector in COLLECTORS:
        for control_id in collector.supported_controls:
            # Check most recent evidence status
            control = db.query(Control).filter(Control.control_id == control_id).first()
            status = "failing"
            last_run = "Never"
            details = {}
            
            if control:
                if control.automation_status == "automated":
                    status = "passing"
                elif control.automation_status == "failed":
                    status = "failing"
                
                # Metadata lookup
                meta = TEST_DEFINITIONS.get(control_id, {
                    "name": f"Check {control_id}",
                    "description": "Automated system check.",
                    "remediation": "Check system configuration.",
                    "owner": "System"
                })
                
                results.append({
                    "id": control_id,
                    "name": meta["name"],
                    "status": status,
                    "owner": meta["owner"],
                    "description": meta["description"],
                    "remediation": meta["remediation"],
                    "last_run": str(control.last_automated_check) if control.last_automated_check else "Never",
                    "evidence": {"output": "System check executed."} # Mock evidence preview
                })

    # 2. Mock Tests for Demo (to fill the table)
    # These represent tests that WOULD run if we connected AWS/GitHub
    mock_scenarios = [
        ("CC6.1", "failing", "User 'admin' does not have MFA enabled."),
        ("CC7.1", "passing", "Inspector agent active on 12/12 instances."),
        ("CC8.1", "failing", "RDS 'prod-db' is unencrypted."),
    ]
    
    for cid, st, reason in mock_scenarios:
        if cid not in [r["id"] for r in results]: # Don't duplicate if real collector exists
             meta = TEST_DEFINITIONS.get(cid)
             if meta:
                 results.append({
                    "id": cid,
                    "name": meta["name"],
                    "status": st,
                    "owner": meta["owner"],
                    "description": meta["description"],
                    "remediation": meta["remediation"],
                    "last_run": "2 hours ago",
                    "evidence": {"reason": reason, "raw_log": "{ 'check': 'FAIL', 'resource': 'prod-db' }"}
                 })
                 
    return results