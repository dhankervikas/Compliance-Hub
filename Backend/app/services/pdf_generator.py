import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def create_signed_pdf(policy_name: str, content: str, version: str, approver: str, output_dir: str = "generated_docs") -> str:
    """
    Generates a PDF for the policy with a digital signature watermark.
    Returns the absolute path to the generated file.
    """
    
    # Ensure directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    filename = f"{policy_name.replace(' ', '_')}_v{version}.pdf"
    filepath = os.path.abspath(os.path.join(output_dir, filename))
    
    # Create PDF
    doc = SimpleDocTemplate(filepath, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    story.append(Paragraph(f"POLICY: {policy_name}", styles['Title']))
    story.append(Spacer(1, 12))
    
    # Metadata
    story.append(Paragraph(f"<b>Version:</b> {version}", styles['Normal']))
    story.append(Paragraph(f"<b>Approved By:</b> {approver}", styles['Normal']))
    story.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    story.append(Spacer(1, 24))
    
    # Content (Basic text handling for now - assuming plain text or simple markdown-like)
    # Ideally we'd parse markdown to reportlab flowables, but for MVP we'll just dump text
    # or handle paragraphs.
    
    # Split by double newline for paragraphs
    paragraphs = content.split('\n\n')
    for para in paragraphs:
        if para.strip():
            # Basic header detection
            if para.startswith('#'):
                style = styles['Heading1']
                para = para.lstrip('#').strip()
            else:
                style = styles['Normal']
                
            story.append(Paragraph(para.replace('\n', '<br/>'), style))
            story.append(Spacer(1, 12))
            
    # Add watermark on every page
    def add_watermark(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica-Bold', 60)
        canvas.setStrokeColorRGB(0.9, 0.9, 0.9)
        canvas.setFillColorRGB(0.9, 0.9, 0.9)
        canvas.translate(100, 500)
        canvas.rotate(45)
        canvas.drawCentredString(0, 0, "APPROVED & SIGNED")
        canvas.restoreState()
        
        # Add footer signature
        canvas.saveState()
        canvas.setFont('Helvetica', 9)
        canvas.drawString(10*mm, 10*mm, f"Digitally Signed by AssuRisk Compliance Engine | {datetime.now().isoformat()}")
        canvas.restoreState()

    doc.build(story, onFirstPage=add_watermark, onLaterPages=add_watermark)
    
    return filepath
