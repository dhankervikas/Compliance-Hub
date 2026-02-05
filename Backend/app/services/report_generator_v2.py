from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from app.models.requirement import RequirementMaster, RequirementStatus
import pandas as pd
import datetime
import os

class ReportGeneratorV2:
    def __init__(self, db):
        self.db = db

    def generate_compliance_report(self, workspace_id, output_dir="reports"):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_path = os.path.join(output_dir, f"AI_Compliance_Report_{timestamp}.pdf")
        excel_path = os.path.join(output_dir, f"AI_Compliance_Report_{timestamp}.xlsx")

        # 1. Fetch Data (3-way Join Logic)
        query = self.db.query(RequirementMaster, RequirementStatus).\
            outerjoin(RequirementStatus, RequirementMaster.id == RequirementStatus.requirement_id).all()
            
        data = []
        module_stats = {}

        for req, status in query:
            # Safe access to status fields (might be None if left join, though we init them)
            st_val = status.status if status else "GAP"
            mapped_sec = status.mapped_section if status else "Unmapped"
            
            # Module Stats
            mod = req.module_source
            if mod not in module_stats:
                module_stats[mod] = {"total": 0, "met": 0}
            module_stats[mod]["total"] += 1
            if st_val == "MET":
                module_stats[mod]["met"] += 1
            
            # Prepare row for Excel/PDF
            row = {
                "Control ID": req.control_id,
                "Domain": req.domain,
                "Requirement": req.requirement_text[:200] + "..." if len(req.requirement_text) > 200 else req.requirement_text,
                "Target Control": req.target_control,
                "Status": st_val,
                "Mapped Evidence": mapped_sec,
                "Module": mod
            }
            data.append(row)

        # 2. Generate Excel
        df = pd.DataFrame(data)
        df.to_excel(excel_path, index=False)
        print(f"Generated Excel: {excel_path}")

        # 3. Generate PDF
        doc = SimpleDocTemplate(pdf_path, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()

        # Title / Metadata
        elements.append(Paragraph(f"AI Compliance Verification Report", styles['Title']))
        elements.append(Paragraph(f"Generated: {datetime.datetime.now()}", styles['Normal']))
        elements.append(Paragraph(f"Standard: ISO 42001:2023", styles['Normal']))
        elements.append(Spacer(1, 12))

        # Executive Summary (Module Scores)
        elements.append(Paragraph("Executive Summary (Compliance Scores)", styles['Heading2']))
        score_data = [["Module", "Progress", "Score"]]
        for mod, stats in module_stats.items():
            score = (stats["met"] / stats["total"]) * 100 if stats["total"] > 0 else 0
            score_data.append([mod, f"{stats['met']}/{stats['total']}", f"{score:.1f}%"])

        t = Table(score_data)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 24))

        # Deep Link / Audit Proof Section
        elements.append(Paragraph("Audit Proof & Mapping Details", styles['Heading2']))
        
        # Filter for MET items first? Or show all? User said "Unmapped Requirements" section.
        # Let's show "Met Requirements" then "Unmapped"
        
        elements.append(Paragraph("Mapped Requirements (Evidence Linked)", styles['Heading3']))
        # Table of Mapped
        mapped_rows = [["ID", "Requirement", "Evidence Source (Deep Link)"]]
        gap_rows = [["ID", "Requirement", "Module"]]
        
        for d in data:
            if d["Status"] == "MET":
                mapped_rows.append([d["Control ID"], d["Requirement"][:50]+"...", d["Mapped Evidence"]])
            else:
                gap_rows.append([d["Control ID"], d["Requirement"][:50]+"...", d["Module"]])
                
        if len(mapped_rows) > 1:
            t_map = Table(mapped_rows, colWidths=[60, 250, 200])
            t_map.setStyle(TableStyle([('GRID', (0, 0), (-1, -1), 0.5, colors.grey)]))
            elements.append(t_map)
        else:
            elements.append(Paragraph("No requirements verified yet.", styles['Normal']))
            
        elements.append(Spacer(1, 12))
        
        elements.append(Paragraph("Gap Analysis (Unmapped Requirements)", styles['Heading3']))
        if len(gap_rows) > 1:
            t_gap = Table(gap_rows, colWidths=[60, 300, 150])
            t_gap.setStyle(TableStyle([('GRID', (0, 0), (-1, -1), 0.5, colors.grey), ('TEXTCOLOR', (0,0), (-1,-1), colors.red)]))
            elements.append(t_gap)
            
        doc.build(elements)
        print(f"Generated PDF: {pdf_path}")
        
        return {"pdf": pdf_path, "excel": excel_path, "stats": module_stats}

if __name__ == "__main__":
    from app.database import SessionLocal
    db = SessionLocal()
    gen = ReportGeneratorV2(db)
    gen.generate_compliance_report(workspace_id=1)
    db.close()
