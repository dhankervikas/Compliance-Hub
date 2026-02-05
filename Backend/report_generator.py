
import os
import json
import zipfile
import hashlib
from datetime import datetime, timedelta
from app.database import SessionLocal
from app.models.control import Control, ControlStatus
from app.models.evidence import Evidence
from sqlalchemy import func

REPORT_DIR = "data/reports"
os.makedirs(REPORT_DIR, exist_ok=True)

class ComplianceReporter:
    def __init__(self):
        self.db = SessionLocal()

    def get_aggregated_metrics(self):
        """
        Aggregates data for CISO Dashboard charts.
        Reads from 'data/mock_evidence_store.json' for consistent demo data.
        """
        MOCK_FILE = "data/mock_evidence_store.json"
        
        # Default mock if file missing
        trend_data = []
        encryption_matrix = [] # New widget data
        github_metrics = [] # New widget data
        
        if os.path.exists(MOCK_FILE):
             with open(MOCK_FILE, "r") as f:
                 data = json.load(f)
                 # 1. Historical Trends from JSON
                 if "historical_trends" in data:
                     # Adapt JSON format {month, score} to Chart format {date, fails, passing}
                     # We'll map Score -> Passing %
                     for t in data["historical_trends"]:
                         score = t.get("score", 50)
                         total = 100
                         trend_data.append({
                             "date": t.get("month"),
                             "fails": total - score,
                             "passing": score
                         })
                 
                 # 2. Extract Special Evidence (Encryption & GitHub)
                 evidence = data.get("current_evidence", [])
                 for ev in evidence:
                     payload = ev.get("raw_payload", {})
                     # Encryption Widget
                     if ev["control_id"] == "A.8.24" and "volume_id" in payload:
                         encryption_matrix.append(payload)
                     # GitHub Widget
                     if ev["control_id"] == "A.8.28" and "repository" in payload:
                         github_metrics.append(payload)

        # Fallback trend if empty
        if not trend_data:
            today = datetime.now()
            for i in range(4, -1, -1):
                date = (today - timedelta(weeks=i)).strftime("%Y-%m-%d")
                trend_data.append({"date": date, "fails": 10, "passing": 90})

        # 3. Remediation Velocity (Mocked by Severity)
        velocity_data = [
            {"severity": "Critical", "days": 2.5},
            {"severity": "High", "days": 5.0},
            {"severity": "Medium", "days": 12.0},
            {"severity": "Low", "days": 20.0}
        ]

        # 4. Framework Coverage (Keep existing DB logic or mock)
        framework_data = [
            {"name": "ISO 27001", "coverage": 85},
            {"name": "SOC 2 Type II", "coverage": 92},
            {"name": "HIPAA", "coverage": 78},
            {"name": "GDPR", "coverage": 65}
        ]

        return {
            "drift_trend": trend_data,
            "remediation_velocity": velocity_data,
            "framework_coverage": framework_data,
            "encryption_matrix": encryption_matrix, # NEW
            "github_metrics": github_metrics,       # NEW
            "meta": {
                "generated_at": datetime.now().isoformat(),
                "confidence_score": 98 
            }
        }

    def generate_auditor_pack(self, start_date=None, end_date=None):
        """
        Zips 'Pass' evidence and generates SoA.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"Auditor_Pack_{timestamp}.zip"
        zip_path = os.path.join(REPORT_DIR, zip_filename)
        
        manifest = {}
        
        with zipfile.ZipFile(zip_path, 'w') as zf:
            # 1. Statement of Applicability (Dynamic Generation)
            soa_content = self._generate_soa()
            zf.writestr("Statement_of_Applicability.md", soa_content)
            manifest["Statement_of_Applicability.md"] = hashlib.sha256(soa_content.encode()).hexdigest()
            
            # 2. Evidence Files (Grouped by Clause)
            # Fetch 'IMPLEMENTED' controls as proxy for 'Pass' evidence if no file records
            controls = self.db.query(Control).filter(Control.status == ControlStatus.IMPLEMENTED).all()
            
            for c in controls:
                # Mock Evidence Content if file doesn't exist
                evidence_content = f"Evidence for Control {c.control_id}\nVerified on: {datetime.now()}\nStatus: PASS\n"
                
                # Determine Clause Folder (e.g., A.5, A.8)
                clause = c.control_id.split('.')[1] if '.' in c.control_id else "General"
                folder = f"Annex_A_{clause}/{c.control_id}"
                filename = f"{folder}/evidence_simulated.txt"
                
                zf.writestr(filename, evidence_content)
                manifest[filename] = hashlib.sha256(evidence_content.encode()).hexdigest()

            # 3. Verification Manifest
            manifest_json = json.dumps(manifest, indent=2)
            zf.writestr("Verification_Manifest.json", manifest_json)
            
        return zip_path, zip_filename

    def _generate_soa(self):
        """
        Generates markdown content for Statement of Applicability.
        """
        metrics = self.get_aggregated_metrics()
        
        lines = [
            "# Statement of Applicability (SoA)",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d')}",
            "**Organization:** AssuRisk Demo Corp",
            "",
            "## Executive Summary",
            "This document defines the applicability of ISO 27001:2022 controls to our organization.",
            "",
            "## Applicability Matrix",
            "| Control ID | Title | Status | Justification |",
            "|---|---|---|---|"
        ]
        
        controls = self.db.query(Control).all()
        for c in controls:
            status = "Applicable" # Simplification
            state = "Implemented" if c.status == ControlStatus.IMPLEMENTED else "Planned"
            justification = c.ai_explanation or "Standard control requirement."
            lines.append(f"| {c.control_id} | {c.title} | {state} | {justification[:50]}... |")
            
        return "\n".join(lines)

    def close(self):
        self.db.close()

if __name__ == "__main__":
    reporter = ComplianceReporter()
    print("Aggregating Metrics...")
    print(json.dumps(reporter.get_aggregated_metrics(), indent=2))
    
    print("\nGenerating Auditor Pack...")
    path, name = reporter.generate_auditor_pack()
    print(f"Pack generated at: {path}")
    reporter.close()
