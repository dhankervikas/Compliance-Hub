
# 9 Business Domains for AI Compliance
DOMAINS = {
    "ETHICS": "AI Ethics & Governance",
    "RISK": "Risk & Impact",
    "DATA": "Data & Privacy",
    "MLOPS": "AI Engineering (MLOps)",
    "SECURITY": "Model Security",
    "HUMAN": "Human-in-the-Loop",
    "SUPPLY": "Third-Party / Supply Chain",
    "PEOPLE": "People & Culture",
    "MONITOR": "Continuous Monitoring"
}

# Mapping: Control ID -> Business Domain
ISO_42001_BUSINESS_MAP = {
    # --- CLAUSE 4: CONTEXT ---
    "ISO42001-4.1": DOMAINS["ETHICS"], 
    "ISO42001-4.2": DOMAINS["ETHICS"], 
    "ISO42001-4.3": DOMAINS["ETHICS"], 
    "ISO42001-4.4": DOMAINS["ETHICS"], 

    # --- CLAUSE 5: LEADERSHIP ---
    "ISO42001-5.1": DOMAINS["ETHICS"], 
    "ISO42001-5.2": DOMAINS["ETHICS"], 
    "ISO42001-5.3": DOMAINS["ETHICS"], 

    # --- CLAUSE 6: PLANNING ---
    "ISO42001-6.1.1": DOMAINS["RISK"], 
    "ISO42001-6.1.2": DOMAINS["RISK"], 
    "ISO42001-6.1.3": DOMAINS["RISK"], 
    "ISO42001-6.1.4": DOMAINS["RISK"], 
    "ISO42001-6.2": DOMAINS["ETHICS"], 
    "ISO42001-6.3": DOMAINS["ETHICS"], 

    # --- CLAUSE 7: SUPPORT ---
    "ISO42001-7.1": DOMAINS["MLOPS"], 
    "ISO42001-7.2": DOMAINS["PEOPLE"], 
    "ISO42001-7.3": DOMAINS["PEOPLE"], 
    "ISO42001-7.4": DOMAINS["ETHICS"], 
    "ISO42001-7.5.1": DOMAINS["ETHICS"], 
    "ISO42001-7.5.2": DOMAINS["ETHICS"],
    "ISO42001-7.5.3": DOMAINS["ETHICS"],

    # --- CLAUSE 8: OPERATION ---
    "ISO42001-8.1": DOMAINS["MLOPS"], 
    "ISO42001-8.2": DOMAINS["RISK"], 
    "ISO42001-8.3": DOMAINS["RISK"], 
    "ISO42001-8.4": DOMAINS["RISK"], 

    # --- CLAUSE 9: PERFORMANCE ---
    "ISO42001-9.1": DOMAINS["MONITOR"], 
    "ISO42001-9.2.1": DOMAINS["ETHICS"], 
    "ISO42001-9.2.2": DOMAINS["ETHICS"],
    "ISO42001-9.3.1": DOMAINS["ETHICS"], 
    "ISO42001-9.3.2": DOMAINS["ETHICS"],
    "ISO42001-9.3.3": DOMAINS["ETHICS"],

    # --- CLAUSE 10: IMPROVEMENT ---
    "ISO42001-10.1": DOMAINS["ETHICS"], 
    "ISO42001-10.2": DOMAINS["ETHICS"], 

    # --- ANNEX A ---
    
    # A.2 Policies
    "ISO42001-A.2.2": DOMAINS["ETHICS"], 
    "ISO42001-A.2.3": DOMAINS["ETHICS"], 
    "ISO42001-A.2.4": DOMAINS["ETHICS"],

    # A.3 Internal Org
    "ISO42001-A.3.2": DOMAINS["ETHICS"],
    "ISO42001-A.3.3": DOMAINS["ETHICS"],

    # A.4 Resources
    "ISO42001-A.4.2": DOMAINS["DATA"],
    "ISO42001-A.4.3": DOMAINS["MLOPS"],
    "ISO42001-A.4.4": DOMAINS["MLOPS"],
    "ISO42001-A.4.5": DOMAINS["PEOPLE"],
    "ISO42001-A.4.6": DOMAINS["SUPPLY"],
    
    # A.5 Impact Assessment
    "ISO42001-A.5.2": DOMAINS["RISK"],
    "ISO42001-A.5.3": DOMAINS["RISK"],
    "ISO42001-A.5.4": DOMAINS["RISK"],
    "ISO42001-A.5.5": DOMAINS["RISK"],

    # A.6 AI System Life Cycle
    "ISO42001-A.6.1.2": DOMAINS["MLOPS"],
    "ISO42001-A.6.1.3": DOMAINS["MLOPS"],
    "ISO42001-A.6.2.2": DOMAINS["MLOPS"],
    "ISO42001-A.6.2.3": DOMAINS["MLOPS"],
    "ISO42001-A.6.2.4": DOMAINS["MLOPS"],
    "ISO42001-A.6.2.5": DOMAINS["MLOPS"],
    "ISO42001-A.6.2.6": DOMAINS["SECURITY"],
    "ISO42001-A.6.2.7": DOMAINS["MLOPS"],
    "ISO42001-A.6.2.8": DOMAINS["MONITOR"],
    
    # A.7 Data
    "ISO42001-A.7.2": DOMAINS["DATA"],
    "ISO42001-A.7.3": DOMAINS["DATA"],
    "ISO42001-A.7.4": DOMAINS["DATA"],
    "ISO42001-A.7.5": DOMAINS["DATA"],
    "ISO42001-A.7.6": DOMAINS["DATA"],

    # A.8 Information for Interested Parties
    "ISO42001-A.8.2": DOMAINS["HUMAN"],
    "ISO42001-A.8.3": DOMAINS["HUMAN"],
    "ISO42001-A.8.4": DOMAINS["HUMAN"],
    "ISO42001-A.8.5": DOMAINS["HUMAN"],

    # A.9 Use of AI Systems
    "ISO42001-A.9.2": DOMAINS["ETHICS"],
    "ISO42001-A.9.3": DOMAINS["HUMAN"],
    "ISO42001-A.9.4": DOMAINS["ETHICS"],

    # A.10 Third-Party Relationships
    "ISO42001-A.10.2": DOMAINS["SUPPLY"],
    "ISO42001-A.10.3": DOMAINS["SUPPLY"],
    "ISO42001-A.10.4": DOMAINS["SUPPLY"]
}
