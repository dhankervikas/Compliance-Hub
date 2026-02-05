import re
import os

# DATA FROM seed_iso27001_custom.py
USER_DATA = [
    ("1. Governance & Policy", "Clause", "4.1", "Context of the organization"),
    ("1. Governance & Policy", "Clause", "4.2", "Needs of interested parties"),
    ("1. Governance & Policy", "Clause", "4.3", "Scope of the ISMS"),
    ("1. Governance & Policy", "Clause", "4.4", "ISMS System"),
    ("1. Governance & Policy", "Clause", "5.1", "Leadership & Commitment"),
    ("1. Governance & Policy", "Clause", "5.2", "Policy"),
    ("1. Governance & Policy", "Clause", "5.3", "Roles, responsibilities and authorities"),
    ("1. Governance & Policy", "Clause", "6.2", "Information Security Objectives"),
    ("1. Governance & Policy", "Clause", "6.3", "Planning of changes"),
    ("1. Governance & Policy", "Clause", "7.1", "Resources"),
    ("1. Governance & Policy", "Clause", "7.5", "Documented information"), # Shortened for matching
    ("1. Governance & Policy", "Annex A", "A.5.1", "Policies for information security"),
    ("1. Governance & Policy", "Annex A", "A.5.2", "Information security roles and responsibilities"),
    ("1. Governance & Policy", "Annex A", "A.5.3", "Segregation of duties"),
    ("1. Governance & Policy", "Annex A", "A.5.4", "Management responsibilities"),
    ("1. Governance & Policy", "Annex A", "A.5.5", "Contact with authorities"),
    ("1. Governance & Policy", "Annex A", "A.5.6", "Contact with special interest groups"),
    ("1. Governance & Policy", "Annex A", "A.5.8", "Information security in project management"),
    ("1. Governance & Policy", "Annex A", "A.5.37", "Documented operating procedures"),
    ("2. HR Security", "Clause", "7.2", "Competence"),
    ("2. HR Security", "Clause", "7.3", "Awareness"),
    ("2. HR Security", "Annex A", "A.6.1", "Screening"),
    ("2. HR Security", "Annex A", "A.6.2", "Terms and conditions of employment"),
    ("2. HR Security", "Annex A", "A.6.3", "Information security awareness, education and training"),
    ("2. HR Security", "Annex A", "A.6.4", "Disciplinary process"),
    ("2. HR Security", "Annex A", "A.6.5", "Responsibilities after termination or change of employment"),
    ("2. HR Security", "Annex A", "A.6.6", "Confidentiality or non-disclosure agreements"),
    ("2. HR Security", "Annex A", "A.6.7", "Remote working"),
    ("2. HR Security", "Annex A", "A.6.8", "Information security event reporting"),
    ("2. HR Security", "Annex A", "A.7.7", "Clear desk and clear screen"),
    ("3. Asset Management", "Annex A", "A.5.9", "Inventory of information and other associated assets"),
    ("3. Asset Management", "Annex A", "A.5.10", "Acceptable use of information and other associated assets"),
    ("3. Asset Management", "Annex A", "A.5.11", "Return of assets"),
    ("3. Asset Management", "Annex A", "A.5.12", "Classification of information"),
    ("3. Asset Management", "Annex A", "A.5.13", "Labelling of information"),
    ("3. Asset Management", "Annex A", "A.7.10", "Storage media"),
    ("3. Asset Management", "Annex A", "A.8.1", "User endpoint devices"),
    ("4. Access Control (IAM)", "Annex A", "A.5.15", "Access control"),
    ("4. Access Control (IAM)", "Annex A", "A.5.16", "Identity management"),
    ("4. Access Control (IAM)", "Annex A", "A.5.17", "Authentication information"),
    ("4. Access Control (IAM)", "Annex A", "A.5.18", "Access rights"),
    ("4. Access Control (IAM)", "Annex A", "A.8.2", "Privileged access rights"),
    ("4. Access Control (IAM)", "Annex A", "A.8.3", "Information access restriction"),
    ("4. Access Control (IAM)", "Annex A", "A.8.4", "Access to source code"),
    ("4. Access Control (IAM)", "Annex A", "A.8.5", "Secure authentication"),
    ("5. Physical Security", "Annex A", "A.7.1", "Physical security perimeters"),
    ("5. Physical Security", "Annex A", "A.7.2", "Physical entry"),
    ("5. Physical Security", "Annex A", "A.7.3", "Securing offices, rooms and facilities"),
    ("5. Physical Security", "Annex A", "A.7.4", "Physical security monitoring"),
    ("5. Physical Security", "Annex A", "A.7.5", "Protecting against physical and environmental threats"),
    ("5. Physical Security", "Annex A", "A.7.6", "Working in secure areas"),
    ("5. Physical Security", "Annex A", "A.7.8", "Equipment siting and protection"),
    ("5. Physical Security", "Annex A", "A.7.9", "Security of assets off-premises"),
    ("5. Physical Security", "Annex A", "A.7.11", "Supporting utilities"),
    ("5. Physical Security", "Annex A", "A.7.12", "Cabling security"),
    ("5. Physical Security", "Annex A", "A.7.13", "Equipment maintenance"),
    ("5. Physical Security", "Annex A", "A.7.14", "Secure disposal or re-use of equipment"),
    ("6. Operations (General)", "Annex A", "A.8.7", "Protection against malware"),
    ("6. Operations (General)", "Annex A", "A.8.10", "Information deletion"),
    ("6. Operations (General)", "Annex A", "A.8.11", "Data masking"),
    ("6. Operations (General)", "Annex A", "A.8.12", "Data leakage prevention"),
    ("6. Operations (General)", "Annex A", "A.8.18", "Use of privileged utility programs"),
    ("7. Configuration Management", "Annex A", "A.8.9", "Configuration management"),
    ("8. Cryptography", "Annex A", "A.8.24", "Use of cryptography"),
    ("9. Logging & Monitoring", "Annex A", "A.8.15", "Logging"),
    ("9. Logging & Monitoring", "Annex A", "A.8.16", "Monitoring activities"),
    ("10. Clock Synchronization", "Annex A", "A.8.17", "Clock synchronization"),
    ("11. Vulnerability Management", "Annex A", "A.8.8", "Management of technical vulnerabilities"),
    ("12. Capacity Management", "Annex A", "A.8.6", "Capacity management"),
    ("13. Backup Management", "Annex A", "A.8.13", "Information backup"),
    ("14. Network Security", "Annex A", "A.5.14", "Information transfer"),
    ("14. Network Security", "Annex A", "A.8.20", "Networks security"),
    ("14. Network Security", "Annex A", "A.8.21", "Security of network services"),
    ("14. Network Security", "Annex A", "A.8.22", "Segregation of networks"),
    ("14. Network Security", "Annex A", "A.8.23", "Web filtering"),
    ("15. SDLC (Development)", "Annex A", "A.8.25", "Secure development life cycle"),
    ("15. SDLC (Development)", "Annex A", "A.8.26", "Application security requirements"),
    ("15. SDLC (Development)", "Annex A", "A.8.27", "Secure system architecture and engineering principles"),
    ("15. SDLC (Development)", "Annex A", "A.8.28", "Secure coding"),
    ("15. SDLC (Development)", "Annex A", "A.8.29", "Security testing in development and acceptance"),
    ("15. SDLC (Development)", "Annex A", "A.8.30", "Outsourced development"),
    ("15. SDLC (Development)", "Annex A", "A.8.31", "Separation of development, test and production environments"),
    ("15. SDLC (Development)", "Annex A", "A.8.32", "Change management"),
    ("15. SDLC (Development)", "Annex A", "A.8.33", "Test information"),
    ("16. Supplier Mgmt", "Annex A", "A.5.19", "Information security in supplier relationships"),
    ("16. Supplier Mgmt", "Annex A", "A.5.20", "Addressing information security within supplier agreements"),
    ("16. Supplier Mgmt", "Annex A", "A.5.21", "Managing information security in the ICT supply chain"),
    ("16. Supplier Mgmt", "Annex A", "A.5.22", "Monitoring, review and change management of supplier services"),
    ("16. Supplier Mgmt", "Annex A", "A.5.23", "Information security for use of cloud services"),
    ("17. Incident & Resilience", "Clause", "7.4", "Communication"),
    ("17. Incident & Resilience", "Annex A", "A.5.24", "Information security incident management"),
    ("17. Incident & Resilience", "Annex A", "A.5.25", "Assessment and decision on information security events"),
    ("17. Incident & Resilience", "Annex A", "A.5.26", "Response to information security incidents"),
    ("17. Incident & Resilience", "Annex A", "A.5.27", "Learning from information security incidents"),
    ("17. Incident & Resilience", "Annex A", "A.5.28", "Collection of evidence"),
    ("17. Incident & Resilience", "Annex A", "A.5.29", "Information security during disruption"),
    ("17. Incident & Resilience", "Annex A", "A.5.30", "ICT readiness for business continuity"),
    ("17. Incident & Resilience", "Annex A", "A.8.14", "Redundancy of information processing facilities"),
    ("18. Threat Intel", "Annex A", "A.5.7", "Threat intelligence"),
    ("18. Threat Intel", "Annex A", "A.8.19", "Installation of software on operational systems"),
    ("19. Legal & Compliance", "Annex A", "A.5.31", "Legal, statutory, regulatory and contractual requirements"),
    ("19. Legal & Compliance", "Annex A", "A.5.32", "Intellectual property rights"),
    ("19. Legal & Compliance", "Annex A", "A.5.33", "Protection of records"),
    ("19. Legal & Compliance", "Annex A", "A.5.34", "Privacy and protection of PII"),
    ("19. Legal & Compliance", "Annex A", "A.5.36", "Compliance with policies, rules and standards for information security"),
    ("19. Legal & Compliance", "Annex A", "A.8.34", "Protection of information systems during audit testing"),
    ("20. Risk Management", "Clause", "6.1.1", "General Risk Planning"),
    ("20. Risk Management", "Clause", "6.1.2", "Information security risk assessment"),
    ("20. Risk Management", "Clause", "6.1.3", "Information security risk treatment"),
    ("20. Risk Management", "Clause", "8.1", "Operational planning and control"),
    ("20. Risk Management", "Clause", "8.2", "Information security risk assessment"),
    ("20. Risk Management", "Clause", "8.3", "Information security risk treatment"),
    ("21. Performance Evaluation", "Clause", "9.1", "Monitoring, measurement, analysis and evaluation"),
    ("21. Performance Evaluation", "Clause", "9.2", "Internal Audit"),
    ("21. Performance Evaluation", "Clause", "9.3", "Management Review"),
    ("21. Performance Evaluation", "Annex A", "A.5.35", "Independent review of information security"),
    ("22. Improvement", "Clause", "10.1", "Nonconformity and corrective action"),
    ("22. Improvement", "Clause", "10.2", "Continual Improvement")
]

# MAP: control_id -> clean_category
id_map = {}
for (cat, _, cid, _) in USER_DATA:
    # CLEAN CATEGORY: Remove "1. " etc.
    if "." in cat.split(" ")[0]:
        parts = cat.split(" ", 1)
        if len(parts) > 1:
            clean_cat = parts[1]
        else:
            clean_cat = cat
    else:
        clean_cat = cat
    
    id_map[cid] = clean_cat

# Read iso_data.py
file_path = r"C:\Projects\Compliance_Product\Backend\app\utils\iso_data.py"
with open(file_path, "r") as f:
    content = f.read()

# Update Content
new_lines = []
lines = content.split('\n')
current_id = None

for line in lines:
    # Check for control_id
    id_match = re.search(r'"control_id":\s+"([^"]+)"', line)
    if id_match:
        current_id = id_match.group(1)
        new_lines.append(line)
        continue
    
    # Check for category line
    if '"category":' in line and current_id in id_map:
        # Replace category
        new_cat = id_map[current_id]
        # Preserve indentation
        indent = line.split('"')[0]
        new_line = f'{indent}"category": "{new_cat}",'
        new_lines.append(new_line)
        print(f"Updated {current_id} -> {new_cat}")
    else:
        new_lines.append(line)

# Write back
with open(file_path, "w") as f:
    f.write('\n'.join(new_lines))

print("Done updating iso_data.py")
