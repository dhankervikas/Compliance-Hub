
NIST_CONTROLS_DATA = [
    # GOVERN
    {"control_id": "GV.OC-01", "title": "Organizational Context", "description": "The organizational mission, objectives, stakeholders, and legal, regulatory, and contractual requirements are understood and prioritized.", "category": "Governance", "priority": "high", "domain": "Govern (GV)"},
    {"control_id": "GV.OC-02", "title": "Risk Management Strategy", "description": "The organization's risk management strategy is established, communicated, and aligned with its mission and objectives.", "category": "Risk Management", "priority": "high", "domain": "Govern (GV)"},
    {"control_id": "GV.OC-03", "title": "Roles and Responsibilities", "description": "Cybersecurity roles, responsibilities, and authorities are established, communicated, and understood.", "category": "Governance", "priority": "high", "domain": "Govern (GV)"},
    {"control_id": "GV.OC-04", "title": "Policy", "description": "Cybersecurity policies, processes, and procedures are established, communicated, and enforced.", "category": "Governance", "priority": "high", "domain": "Govern (GV)"},
    {"control_id": "GV.OC-05", "title": "Oversight", "description": "Oversight of cybersecurity risk management is provided by the board of directors or equivalent.", "category": "Governance", "priority": "high", "domain": "Govern (GV)"},

    # IDENTIFY
    {"control_id": "ID.AM-01", "title": "Asset Inventory", "description": "Inventories of hardware, software, services, and data are maintained.", "category": "Asset Management", "priority": "high", "domain": "Identify (ID)"},
    {"control_id": "ID.AM-02", "title": "Asset Management", "description": "Assets are prioritized based on their classification, criticality, and business value.", "category": "Asset Management", "priority": "medium", "domain": "Identify (ID)"},
    {"control_id": "ID.RA-01", "title": "Risk Assessment", "description": "Cybersecurity risks to the organization, assets, and individuals are identified and assessed.", "category": "Risk Management", "priority": "high", "domain": "Identify (ID)"},
    {"control_id": "ID.RA-02", "title": "Vulnerability Assessment", "description": "Vulnerabilities in assets are identified and documented.", "category": "Risk Management", "priority": "high", "domain": "Identify (ID)"},
    {"control_id": "ID.RA-03", "title": "Threat Intelligence", "description": "Threat intelligence is received and analyzed to identify threats to the organization.", "category": "Threat Intel", "priority": "medium", "domain": "Identify (ID)"},

    # PROTECT
    {"control_id": "PR.AA-01", "title": "Identity Management", "description": "Identities and credentials are managed and authenticated.", "category": "Access Control (IAM)", "priority": "high", "domain": "Protect (PR)"},
    {"control_id": "PR.AA-02", "title": "Access Control", "description": "Physical and logical access to assets is managed and limited to authorized users, processes, and devices.", "category": "Access Control (IAM)", "priority": "high", "domain": "Protect (PR)"},
    {"control_id": "PR.AA-03", "title": "Remote Access", "description": "Remote access is managed and secured.", "category": "Access Control (IAM)", "priority": "high", "domain": "Protect (PR)"},
    {"control_id": "PR.AA-04", "title": "Privileged Access", "description": "Privileged access is managed and restricted.", "category": "Access Control (IAM)", "priority": "high", "domain": "Protect (PR)"},
    {"control_id": "PR.AT-01", "title": "Awareness Training", "description": "Personnel are provided with cybersecurity awareness training.", "category": "HR Security", "priority": "high", "domain": "Protect (PR)"},
    {"control_id": "PR.AT-02", "title": "Role-Based Training", "description": "Personnel are provided with role-based cybersecurity training.", "category": "HR Security", "priority": "medium", "domain": "Protect (PR)"},
    {"control_id": "PR.DS-01", "title": "Data Protection", "description": "Data is protected at rest and in transit.", "category": "Data Security", "priority": "high", "domain": "Protect (PR)"},
    {"control_id": "PR.DS-02", "title": "Data Leakage Prevention", "description": "Mechanisms are implemented to prevent unauthorized data exfiltration.", "category": "Data Security", "priority": "high", "domain": "Protect (PR)"},
    {"control_id": "PR.PS-01", "title": "Configuration Management", "description": "Configuration management practices are applied to assets.", "category": "Governance", "priority": "medium", "domain": "Protect (PR)"},
    {"control_id": "PR.PS-02", "title": "Software Security", "description": "Software is developed and maintained securely.", "category": "App Security", "priority": "high", "domain": "Protect (PR)"},

    # DETECT
    {"control_id": "DE.AE-01", "title": "Anomalies and Events", "description": "Anomalies and potential security events are detected.", "category": "Incident & Resilience", "priority": "high", "domain": "Detect (DE)"},
    {"control_id": "DE.CM-01", "title": "Security Monitoring", "description": "Information system and assets are monitored to identify cybersecurity events.", "category": "Incident & Resilience", "priority": "high", "domain": "Detect (DE)"},
    {"control_id": "DE.CM-02", "title": "Log Management", "description": "Logs are collected, aggregated, and analyzed.", "category": "Incident & Resilience", "priority": "high", "domain": "Detect (DE)"},

    # RESPOND
    {"control_id": "RS.MA-01", "title": "Incident Management", "description": "Incidents are managed to minimize impact.", "category": "Incident & Resilience", "priority": "high", "domain": "Respond (RS)"},
    {"control_id": "RS.MA-02", "title": "Incident Reporting", "description": "Incidents are reported to internal and external stakeholders.", "category": "Incident & Resilience", "priority": "high", "domain": "Respond (RS)"},
    {"control_id": "RS.AN-01", "title": "Analysis", "description": "Analysis is conducted to ensure adequate response and support recovery activities.", "category": "Incident & Resilience", "priority": "high", "domain": "Respond (RS)"},
    {"control_id": "RS.MI-01", "title": "Mitigation", "description": "Activities are performed to prevent expansion of an event, mitigate its effects, and eradicate the incident.", "category": "Incident & Resilience", "priority": "high", "domain": "Respond (RS)"},

    # RECOVER
    {"control_id": "RC.RP-01", "title": "Recovery Planning", "description": "Recovery processes and procedures are executed and maintained.", "category": "Incident & Resilience", "priority": "high", "domain": "Recover (RC)"},
    {"control_id": "RC.IM-01", "title": "Improvement", "description": "Recovery planning and processes are improved by incorporating lessons learned.", "category": "Incident & Resilience", "priority": "medium", "domain": "Recover (RC)"},
    {"control_id": "RC.CO-01", "title": "Communication", "description": "Restoration activities are communicated to internal and external parties.", "category": "Incident & Resilience", "priority": "medium", "domain": "Recover (RC)"}
]
