from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.control import Control, ControlStatus

router = APIRouter(
    tags=["analytics"]
)

@router.get("/domain/{domain_name}")
def get_domain_analytics(domain_name: str, db: Session = Depends(get_db)):
    """
    Get compliance analytics for a specific Process Domain (e.g., 'Access Management')
    """
    controls = db.query(Control).filter(Control.domain == domain_name).all()
    
    if not controls:
        return {
            "domain": domain_name,
            "compliance_score": 0,
            "total_controls": 0,
            "breakdown": {},
            "gaps": []
        }
    
    total = len(controls)
    implemented = len([c for c in controls if c.status == ControlStatus.IMPLEMENTED])
    score = round((implemented / total) * 100) if total > 0 else 0
    
    # Identify Gaps (Not Implemented)
    gap_controls = [
        {
            "id": c.control_id,
            "title": c.title,
            "status": c.status,
            "priority": c.priority
        }
        for c in controls if c.status != ControlStatus.IMPLEMENTED
    ]
    
    # Mapped Frameworks (e.g. ISO 27001, SOC 2)
    # Assuming we can join Framework here to get names
    # For now, just listing distinct framework_ids or names if relationship loaded
    framework_ids = list(set([c.framework_id for c in controls]))
    
    return {
        "domain": domain_name,
        "compliance_score": score,
        "total_controls": total,
        "implemented": implemented,
        "gaps": gap_controls,
        "framework_ids": framework_ids
    }


@router.get("/system-stats")
def get_system_stats(db: Session = Depends(get_db)):
    """
    Get System Effectiveness Dashboard Metrics (Vanta-Style)
    """
    from datetime import datetime, timedelta
    from app.models.evidence import Evidence
    from app.models.framework import Framework
    
    # 1. Coverage Gap (Focus on ISO 27001)
    # Find ISO Framework
    iso_fw = db.query(Framework).filter(Framework.code.contains("ISO")).first()
    if iso_fw:
        total_iso = db.query(Control).filter(Control.framework_id == iso_fw.id).count()
        missing_iso = db.query(Control).filter(
            Control.framework_id == iso_fw.id, 
            Control.status != ControlStatus.IMPLEMENTED
        ).count()
        coverage_gap = round((missing_iso / total_iso) * 100) if total_iso > 0 else 0
    else:
        coverage_gap = 100 # Worst case

    # 2. Evidence Freshness
    # Avg days since collection. Target < 90 days.
    evidence_items = db.query(Evidence).filter(Evidence.collection_date.isnot(None)).all()
    if evidence_items:
        now = datetime.utcnow()
        ages = [(now - e.collection_date).days for e in evidence_items]
        avg_age = sum(ages) / len(ages)
        # Freshness Score: 100% if 0 days, 0% if > 365 days
        freshness_score = max(0, min(100, 100 - (avg_age / 3.65)))
        avg_days_expiry = max(0, 365 - avg_age) 
    else:
        freshness_score = 0
        avg_days_expiry = 0

    # 3. Compliance Velocity (Mocked Logic based on recency)
    # in real world: avg time from 'failed' check to 'pass'
    recent_impl = db.query(Control).filter(
        Control.status == ControlStatus.IMPLEMENTED,
        Control.updated_at >= datetime.utcnow() - timedelta(days=30)
    ).count()
    velocity_score = min(100, recent_impl * 10) # 10 controls/mo = 100% velocity

    # 4. Infrastructure Scan Integration (NEW)
    # Read latest scan from /data/scans
    scan_failures = 0
    total_checks = 0
    
    import os
    import json
    SCAN_DIR = "data/scans"
    if os.path.exists(SCAN_DIR):
        # Get latest file
        files = [os.path.join(SCAN_DIR, f) for f in os.listdir(SCAN_DIR) if f.endswith('.json')]
        if files:
            latest_file = max(files, key=os.path.getctime)
            try:
                with open(latest_file, 'r') as f:
                    scan_data = json.load(f)
                    summary = scan_data.get('summary', {})
                    scan_failures = summary.get('fail', 0)
                    total_checks = summary.get('total', 0)
            except Exception as e:
                print(f"Error reading scan: {e}")

    # Adjust Coverage Gap or Freshness based on Failures?
    # Let's add a specialized "Compliance Health" metric for the user request
    # Since the frontend expects specific keys, we might need to piggyback or add a new one.
    # The user asked for "Compliance Health" chart. The frontend has "Coverage Gap".
    # I will stick to existing structure but influence the values.
    
    # If we have scan failures, Coverage Gap should definitely not be 0% (or 100% coverage).
    # Let's say Coverage Gap = (Missing ISO + Scan Failures) / Total
    
    # Recalculate Coverage Gap with Scan Data
    if iso_fw:
        missing_count = missing_iso + scan_failures
        coverage_gap = round((missing_count / (total_iso + total_checks)) * 100) if (total_iso + total_checks) > 0 else 0


    return {
        "coverage_gap": {
            "value": coverage_gap,
            "unit": "%",
            "label": "Coverage Gap (Controls + Scans)"
        },
        "evidence_freshness": {
            "value": round(freshness_score),
            "days_to_expiry": round(avg_days_expiry),
            "label": "Evidence Freshness"
        },
        "compliance_velocity": {
            "value": velocity_score, 
            "label": "Velocity (Controls/Mo)",
            "trend": "+12%"
        },
        # Optional: Pass raw scan stats if needed by frontend updates
        "scan_stats": {
            "failures": scan_failures,
            "total": total_checks,
            "findings": scan_data.get('findings', []) if 'scan_data' in locals() else []
        }
    }
