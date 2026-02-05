
"""
NIST CSF 2.0 Business Mapping
Maps NIST Categories (and specific Subcategories) to 10 Business Domains.
"""

NIST_BUSINESS_MAP = {
    # 1. Governance & Strategy
    # "All of Govern (GV): Policy, Oversight, Strategy..." EXCEPT Supply Chain
    "GV.OC": "Governance & Strategy",
    "GV.RM": "Governance & Strategy",
    "GV.RR": "Governance & Strategy",
    "GV.PO": "Governance & Strategy",
    "GV.OV": "Governance & Strategy",
    
    # 2. Asset & Inventory
    # "Identify (ID.AM)"
    "ID.AM": "Asset & Inventory",
    
    # 3. Identity & Access (IAM)
    # "Protect (PR.AA)"
    "PR.AA": "Identity & Access (IAM)",
    
    # 4. Risk & Vulnerability
    # "Identify (ID.RA) & Protect (PR.PS)"
    "ID.RA": "Risk & Vulnerability",
    
    # NOTE: PR.PS is split in user request between "Risk & Vuln" and "Infra".
    # User said: "4. Risk & Vulnerability: ... Protect (PR.PS)"
    # AND "7. Infrastructure & Network: Protect (PR.IR) & (PR.PS)"
    # Strategy: Map PR.PS generally to "Risk & Vulnerability" (Platform Security fits vuln mgmt).
    # If specific subcategories need "Infrastructure", we could map them individually, 
    # but based on standard 'Platform Security' (config, log mgmt, software security), 'Risk & Vulnerability' is a strong fit.
    # Alternatively, PR.PS-01 (Config Mgmt) -> Infra? 
    # Let's stick to user list order prioritization: #4 listed PR.PS first. 
    "PR.PS": "Risk & Vulnerability", 

    # 5. Data Protection
    # "Protect (PR.DS)"
    "PR.DS": "Data Protection",
    
    # 6. Security Awareness (People)
    # "Protect (PR.AT)"
    "PR.AT": "Security Awareness (People)",
    
    # 7. Infrastructure & Network
    # "Protect (PR.IR)"
    "PR.IR": "Infrastructure & Network",
    
    # 8. Security Monitoring (SOC)
    # "All of Detect (DE)"
    "DE.AE": "Security Monitoring (SOC)",
    "DE.CM": "Security Monitoring (SOC)",
    
    # 9. Incident Management
    # "All of Respond (RS)"
    "RS.MA": "Incident Management",
    "RS.AN": "Incident Management",
    "RS.MI": "Incident Management",
    "RS.CO": "Incident Management",
    
    # 10. Business Continuity
    # "All of Recover (RC)"
    "RC.RP": "Business Continuity",
    "RC.CO": "Business Continuity",
    
    # EXCEPTIONS (Subcategory Level Overrides)
    # "GV.SC (Supply Chain) -> Folder: Third-Party Risk"
    "GV.SC": "Third-Party / Supply Chain" 
}

# Helper to look up domain by Category Code (e.g., "GV.OC") or by checking start
def get_nist_business_domain(category_code):
    return NIST_BUSINESS_MAP.get(category_code, "Governance & Strategy")
