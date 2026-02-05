import csv
import os
import shutil

# Vanta-Standard "Jobs to be Done" Mappings
TITLES = {
    "A.5.1": "Establish Information Security Policies",
    "A.5.2": "Assign Security Roles & Responsibilities",
    "A.5.3": "Segregate Conflicting Duties",
    "A.5.4": "Enforce Management Responsibilities",
    "A.5.5": "Maintain Contact with Authorities",
    "A.5.6": "Maintain Contact with Interest Groups",
    "A.5.7": "Collect and Analyze Threat Intelligence",
    "A.5.8": "Integrate Security into Project Management",
    "A.5.9": "Inventory Information Assets",
    "A.5.10": "Define Acceptable Use of Assets",
    "A.5.11": "Return Assets Upon Termination",
    "A.5.12": "Classify Information",
    "A.5.13": "Label Information",
    "A.5.14": "Secure Information Transfer",
    "A.5.15": "Control Access to Information",
    "A.5.16": "Manage Identity Lifecycle",
    "A.5.17": "Secure Authentication Information",
    "A.5.18": "Manage Access Rights",
    "A.5.19": "Manage Supplier Security Risks",
    "A.5.20": "Manage Supplier Agreements",
    "A.5.21": "Secure ICT Supply Chain",
    "A.5.22": "Monitor Supplier Services",
    "A.5.23": "Manage Cloud Services Security",
    "A.5.24": "Plan for Incident Management",
    "A.5.25": "Assess and Classify Security Events",
    "A.5.26": "Respond to Security Incidents",
    "A.5.27": "Learn from Information Security Incidents",
    "A.5.28": "Collect and Preserve Evidence",
    "A.5.29": "Plan for Business Continuity",
    "A.5.30": "Ensure ICT Readiness for Business Continuity",
    "A.5.31": "Identify Legal and Contractual Requirements",
    "A.5.32": "Protect Intellectual Property Rights",
    "A.5.33": "Protect Records",
    "A.5.34": "Protect Privacy and PII",
    "A.5.35": "Conduct Independent Security Reviews",
    "A.5.36": "Monitor Compliance with Policies",
    "A.5.37": "Document Operating Procedures",

    "A.6.1": "Screen Candidates",
    "A.6.2": "Define Employment Security Terms",
    "A.6.3": "Conduct Security Awareness Training",
    "A.6.4": "Enforce Disciplinary Process",
    "A.6.5": "Terminate or Change Employment",
    "A.6.6": "Enforce Confidentiality Agreements",
    "A.6.7": "Secure Remote Working",
    "A.6.8": "Report Security Events",

    "A.7.1": "Secure Physical Perimeters",
    "A.7.2": "Secure Physical Entry",
    "A.7.3": "Secure Offices and Facilities",
    "A.7.4": "Monitor Physical Security",
    "A.7.5": "Protect Against Environmental Threats",
    "A.7.6": "Work in Secure Areas",
    "A.7.7": "Enforce Clear Desk and Screen Policy",
    "A.7.8": "Secure Equipment Site and Placement",
    "A.7.9": "Secure Off-Premises Assets",
    "A.7.10": "Manage Removable Media",
    "A.7.11": "Secure Supporting Utilities",
    "A.7.12": "Secure Power and Cabling",
    "A.7.13": "Maintain Equipment",
    "A.7.14": "Securely Dispose of Equipment",

    "A.8.1": "Secure User Endpoints",
    "A.8.2": "Restrict Privileged Access",
    "A.8.3": "Restrict Information Access",
    "A.8.4": "Secure Source Code",
    "A.8.5": "Secure Authentication Systems",
    "A.8.6": "Manage Capacity",
    "A.8.7": "Protect Against Malware",
    "A.8.8": "Manage Technical Vulnerabilities",
    "A.8.9": "Manage Configuration",
    "A.8.10": "Delete Information Securely",
    "A.8.11": "Mask Data",
    "A.8.12": "Prevent Data Leakage",
    "A.8.13": "Backup Information",
    "A.8.14": "Ensure Redundancy of Processing Facilities",
    "A.8.15": "Enable Logging",
    "A.8.16": "Monitor Activities",
    "A.8.17": "Synchronize Clocks",
    "A.8.18": "Use Privileged Utility Programs",
    "A.8.19": "Install Software on Operational Systems",
    "A.8.20": "Secure Networks",
    "A.8.21": "Secure Network Services",
    "A.8.22": "Segregate Networks",
    "A.8.23": "Filter Web Access",
    "A.8.24": "Use Cryptography",
    "A.8.25": "Secure Development Lifecycle",
    "A.8.26": "Define Application Security Requirements",
    "A.8.27": "Secure System Architecture",
    "A.8.28": "Secure Coding",
    "A.8.29": "Test Security in Development",
    "A.8.30": "Secure Outsourced Development",
    "A.8.31": "Separate Development, Test, and Production",
    "A.8.32": "Manage Change",
    "A.8.33": "Protect Test Data",
    "A.8.34": "Protect Systems During Audit"
}

def update_csv():
    file_path = "Backend/MASTER_ISO27001_INTENTS.csv"
    temp_file = file_path + ".tmp"
    
    updated_count = 0
    
    with open(file_path, mode='r', encoding='utf-8', errors='replace') as infile, \
         open(temp_file, mode='w', newline='', encoding='utf-8') as outfile:
        
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in reader:
            clause = row.get('Clause_or_control', '').strip()
            # Normalize clause (ensure A. prefix for 5-8)
            norm_clause = clause
            if clause and clause[0].isdigit() and clause.startswith(('5','6','7','8')):
                 norm_clause = f"A.{clause}"
            
            if norm_clause in TITLES:
                row['Action_Title'] = TITLES[norm_clause]
                updated_count += 1
            
            writer.writerow(row)
            
    shutil.move(temp_file, file_path)
    print(f"Updated {updated_count} rows with Vanta-Standard titles.")

if __name__ == "__main__":
    update_csv()
