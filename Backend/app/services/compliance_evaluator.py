from sqlalchemy.orm import Session
from datetime import datetime
from fastapi import BackgroundTasks

from app.models.universal_intent import UniversalIntent, IntentStatus
from app.models.intent_framework_crosswalk import IntentFrameworkCrosswalk
from app.models.compliance_result import ComplianceResult
from app.models.control import Control
from app.models.policy import Policy

class ComplianceEvaluator:
    """
    Universal Logic Engine: Evaluates Intents -> Dynamic Deduplication -> Compliance Results.
    """

    @staticmethod
    def evaluate_intent(db: Session, intent_id: int, background_tasks: BackgroundTasks = None):
        """
        Check if an Intent is satisfied (e.g. Policy Exists).
        If status changes to COMPLETED, trigger Async Deduplication.
        """
        intent = db.query(UniversalIntent).filter(UniversalIntent.id == intent_id).first()
        if not intent:
            return

        # 1. Check Condition (Simplified: Policy Existence)
        # Note: This is where we plug in the "Rules" logic later.
        # For now, we assume if a Policy matches the Intent Description/Name, it's satisfied.
        # Or better, we look for a Policy linked to this Intent via POLICY_INTENTS mapping.
        
        # Checking for any policy that vaguely matches helps simulates the AI logic
        # Ideally, we query the 'Policy' table.
        policy_exists = db.query(Policy).filter(Policy.name.ilike(f"%{intent.intent_id.replace('INT-', '')}%")).first()
        
        # Force completion logic for testing using a flag or specific intent check
        is_complete = True if policy_exists else False

        # Update Status
        new_status = IntentStatus.COMPLETED if is_complete else IntentStatus.PENDING
        
        if intent.status != new_status:
            intent.status = new_status
            db.commit()
            
            if new_status == IntentStatus.COMPLETED:
                print(f"[Logic Engine] Intent {intent.intent_id} COMPLETED. Triggering Impact Calc...")
                if background_tasks:
                   background_tasks.add_task(ComplianceEvaluator.calculate_intent_impact, intent.id)
                else:
                   # Synchronous fallback if no bg tasks provided
                   ComplianceEvaluator.calculate_intent_impact_sync(intent.id)

    @staticmethod
    def calculate_intent_impact_sync(intent_id: int):
        """
        Wrapper for sync execution (needed until we can pass db session to background task strictly)
        Realistically, background tasks need a fresh DB session. 
        So we will implement the logic inside a standalone function with its own session context
        or pass the ID and instantiate DB there.
        """
        from app.database import SessionLocal
        db = SessionLocal()
        try:
            ComplianceEvaluator._run_impact_logic(db, intent_id)
        finally:
            db.close()

    @staticmethod
    def calculate_intent_impact(intent_id: int):
        """
        Async worker entry point.
        """
        ComplianceEvaluator.calculate_intent_impact_sync(intent_id)

    @staticmethod
    def _run_impact_logic(db: Session, intent_id: int):
        """
        The "Deduplication Engine":
        Finds all frameworks mapped to this Intent and updates their controls.
        """
        # 1. Fetch Crosswalk Mappings
        mappings = db.query(IntentFrameworkCrosswalk).filter(
            IntentFrameworkCrosswalk.intent_id == intent_id
        ).all()
        
        if not mappings:
            print(f"[Logic Engine] No mappings found for Intent ID {intent_id}")
            return

        print(f"[Logic Engine] Broadcasting Impact: Found {len(mappings)} downstream controls.")

        # 2. Update Controls
        for map_entry in mappings:
            # map_entry.framework_id (e.g. ISO_27001)
            # map_entry.control_reference (e.g. A.5.15)
            
            # Find the actual Control ID using the Reference
            # Note: We need to handle the prefix differences (A.5.15 vs ISO_A.5.15)
            # Our Seeding logic put "A.5.15" in Crosswalk.
            # Our Control Table has "ISO_A.5.15". 
            
            target_control = db.query(Control).filter(
                Control.control_id.like(f"%{map_entry.control_reference}")
            ).first()
            
            if target_control:
                # Upsert Result
                # This affects ALL Tenants by default in this MVP, or we iterate tenants.
                # For "Universal" logic, we assume the Admin Tenant or Current Context.
                # Here we will just update for the default/admin tenant for Proof of Concept.
                tenant_id = "default_tenant" 
                
                result = db.query(ComplianceResult).filter(
                    ComplianceResult.control_id == target_control.id,
                    ComplianceResult.tenant_id == tenant_id
                ).first()
                
                if not result:
                    result = ComplianceResult(
                        control_id=target_control.id, 
                        tenant_id=tenant_id,
                        status="PASS",
                        evidence_metadata="Auto-Satisfied via Universal Intent"
                    )
                    db.add(result)
                else:
                    result.status = "PASS"
                    result.evidence_metadata = "Auto-Satisfied via Universal Intent"
                
        db.commit()
        print(f"[Logic Engine] Impact Calculation Complete for Intent ID {intent_id}")

