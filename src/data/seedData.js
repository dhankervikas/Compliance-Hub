
// ============================================================================
// UNIVERSAL INTENT LIBRARY (Source of Truth)
// ============================================================================
export const UNIVERSAL_INTENTS = [
    { id: "INT-A5-15", text: "Access Control Pol: Access to information and other associated assets shall be limited to authorized users.", domain: "Access Control" },
    { id: "INT-A5-16", text: "Identity Mgmt: The full lifecycle of identities shall be managed.", domain: "Access Control" },
    { id: "INT-A5-17", text: "Auth Info: Allocation and management of authentication info shall be controlled.", domain: "Access Control" }
];

// ============================================================================
// ISO 27001:2022 - USER DEFINED MAPPING (EXACT) - ID SEPARATED
// ============================================================================
export const ISO_CONTROLS = [
    // --- CLAUSE 4: CONTEXT ---
    { control_id: "ISO-4.1", title: "4.1 Understanding organization", description: "Determine external and internal issues relevant to the ISMS.", process: "Governance & Policy", category: "Governance" },
    { control_id: "ISO-4.2", title: "4.2 Interested Parties", description: "Determine requirements of interested parties relevant to the ISMS.", process: "Governance & Policy", category: "Governance" },
    { control_id: "ISO-4.3", title: "4.3 Scope of ISMS", description: "Determine and document the scope of the ISMS.", process: "Governance & Policy", category: "Governance" },
    { control_id: "ISO-4.4", title: "4.4 ISMS Processes", description: "Establish, implement, maintain, and continually improve the ISMS.", process: "Governance & Policy", category: "Governance" },

    // --- CLAUSE 5: LEADERSHIP ---
    { control_id: "ISO-5.1", title: "5.1 Leadership & Commitment", description: "Top management demonstrates leadership and commitment to the ISMS.", process: "Governance & Policy", category: "Governance" },
    { control_id: "ISO-5.2", title: "5.2 Policy", description: "Establish and communicate the information security policy.", process: "Governance & Policy", category: "Governance" },
    { control_id: "ISO-5.3", title: "5.3 Roles & Responsibilities", description: "Assign and communicate organizational roles, responsibilities, and authorities.", process: "Governance & Policy", category: "Governance" },

    // --- CLAUSE 6: PLANNING (RISK) ---
    { control_id: "ISO-6.1.1", title: "6.1.1 General Actions", description: "Plan actions to address risks and opportunities.", process: "Risk Management", category: "Governance" },
    { control_id: "ISO-6.1.2", title: "6.1.2 Risk Assessment", description: "Define and apply an information security risk assessment process.", process: "Risk Management", category: "Governance" },
    { control_id: "ISO-6.1.3", title: "6.1.3 Risk Treatment", description: "Define and apply an information security risk treatment process.", process: "Risk Management", category: "Governance" },
    { control_id: "ISO-6.2", title: "6.2 Objectives", description: "Establish information security objectives and plans to achieve them.", process: "Governance & Policy", category: "Governance" },
    { control_id: "ISO-6.3", title: "6.3 Planning of Changes", description: "Changes to the ISMS are carried out in a planned manner.", process: "Governance & Policy", category: "Governance" },

    // --- CLAUSE 7: SUPPORT ---
    { control_id: "ISO-7.1", title: "7.1 Resources", description: "Provide resources needed for the ISMS.", process: "Governance & Policy", category: "Governance" },
    { control_id: "ISO-7.2", title: "7.2 Competence", description: "Ensure necessary competence of persons doing work under the organization's control.", process: "HR Security", category: "Governance" },
    { control_id: "ISO-7.3", title: "7.3 Awareness", description: "Ensure persons are aware of the policy and their contribution to effectiveness.", process: "HR Security", category: "Governance" },
    { control_id: "ISO-7.4", title: "7.4 Communication", description: "Determine internal and external communications relevant to the ISMS.", process: "Governance & Policy", category: "Governance" },
    { control_id: "ISO-7.5.1", title: "7.5.1 Documented Info - General", description: "Include documented information required by the standard and the organization.", process: "Governance & Policy", category: "Governance" },
    { control_id: "ISO-7.5.2", title: "7.5.2 Creating & Updating", description: "Ensure appropriate identification, format, and review of documents.", process: "Governance & Policy", category: "Governance" },
    { control_id: "ISO-7.5.3", title: "7.5.3 Control of Doc Info", description: "Documented information is available, protected, and controlled.", process: "Governance & Policy", category: "Governance" },

    // --- CLAUSE 8: OPERATION (RISK) ---
    { control_id: "ISO-8.1", title: "8.1 Operational Planning", description: "Plan, implement, and control processes needed to meet requirements.", process: "Risk Management", category: "Governance" },
    { control_id: "ISO-8.2", title: "8.2 Risk Assessment", description: "Perform information security risk assessments at planned intervals.", process: "Risk Management", category: "Governance" },
    { control_id: "ISO-8.3", title: "8.3 Risk Treatment", description: "Implement the information security risk treatment plan.", process: "Risk Management", category: "Governance" },

    // --- CLAUSE 9: PERFORMANCE ---
    { control_id: "ISO-9.1", title: "9.1 Monitoring & Measurement", description: "Evaluate the performance and effectiveness of the ISMS.", process: "Performance Evaluation", category: "Governance" },
    { control_id: "ISO-9.2", title: "9.2 Internal Audit", description: "Conduct internal audits at planned intervals.", process: "Performance Evaluation", category: "Governance" },
    { control_id: "ISO-9.3", title: "9.3 Management Review", description: "Top management reviews the ISMS at planned intervals.", process: "Performance Evaluation", category: "Governance" },

    // --- CLAUSE 10: IMPROVEMENT ---
    { control_id: "ISO-10.1", title: "10.1 Continual Improvement", description: "Continually improve the suitability, adequacy, and effectiveness of the ISMS.", process: "Improvement", category: "Governance" },
    { control_id: "ISO-10.2", title: "10.2 Nonconformity", description: "React to nonconformities and take action to control and correct them.", process: "Improvement", category: "Governance" },

    // --- ANNEX A CONTROLS (Consolidated) ---
    // A.5 Organizational
    { control_id: "ISO-A.5.1", title: "A.5.1 Policies for InfoSec", description: "Policies for information security and topic-specific policies.", process: "Governance & Policy", category: "Governance" },
    { control_id: "ISO-A.5.2", title: "A.5.2 InfoSec Roles", description: "Information security roles and responsibilities.", process: "Governance & Policy", category: "Governance" },
    { control_id: "ISO-A.5.3", title: "A.5.3 Segregation of Duties", description: "Segregation of conflicting duties and areas of responsibility.", process: "Governance & Policy", category: "Governance" },
    { control_id: "ISO-A.5.4", title: "A.5.4 Management Responsibilities", description: "Management requires all personnel to apply security.", process: "Governance & Policy", category: "Governance" },
    { control_id: "ISO-A.5.5", title: "A.5.5 Contact with Authorities", description: "Contacts with relevant authorities are maintained.", process: "Legal & Compliance", category: "Governance" },
    { control_id: "ISO-A.5.6", title: "A.5.6 Special Interest Groups", description: "Contacts with special interest groups are maintained.", process: "Governance & Policy", category: "Governance" },
    { control_id: "ISO-A.5.7", title: "A.5.7 Threat Intelligence", description: "Information about threats is collected and analyzed.", process: "Threat Intel", category: "Technical" },
    { control_id: "ISO-A.5.8", title: "A.5.8 InfoSec in Project Mgmt", description: "Information security is integrated into project management.", process: "Governance & Policy", category: "Governance" },
    { control_id: "ISO-A.5.9", title: "A.5.9 Inventory of Assets", description: "Inventory of information and other associated assets.", process: "Asset Management", category: "Governance" },
    { control_id: "ISO-A.5.10", title: "A.5.10 Acceptable Use", description: "Rules for the acceptable use of information and associated assets.", process: "Asset Management", category: "Governance" },
    { control_id: "ISO-A.5.11", title: "A.5.11 Return of Assets", description: "Rules for return of assets upon termination.", process: "Asset Management", category: "Governance" },
    { control_id: "ISO-A.5.12", title: "A.5.12 Classification of Info", description: "Information is classified according to needs.", process: "Asset Management", category: "Governance" },
    { control_id: "ISO-A.5.13", title: "A.5.13 Labeling of Info", description: "Procedures for labeling information.", process: "Asset Management", category: "Governance" },
    { control_id: "ISO-A.5.14", title: "A.5.14 Information Transfer", description: "Rules for information transfer and communication services.", process: "Asset Management", category: "Governance" },
    { control_id: "ISO-A.5.15", title: "A.5.15 Access Control", description: "Rules to control physical and logical access.", process: "Access Control (IAM)", category: "Technical" },
    { control_id: "ISO-A.5.16", title: "A.5.16 Identity Mgmt", description: "Managing the full lifecycle of identity.", process: "Access Control (IAM)", category: "Technical" },
    { control_id: "ISO-A.5.17", title: "A.5.17 Authentication Info", description: "Allocation and management of authentication info.", process: "Access Control (IAM)", category: "Technical" },
    { control_id: "ISO-A.5.18", title: "A.5.18 Access Rights", description: "Access rights are provisioned and reviewed.", process: "Access Control (IAM)", category: "Governance" },
    { control_id: "ISO-A.5.19", title: "A.5.19 Supplier Security", description: "Information security in supplier relationships.", process: "Supplier Mgmt", category: "Governance" },
    { control_id: "ISO-A.5.20", title: "A.5.20 Supplier Agreements", description: "Addressing security in supplier agreements.", process: "Supplier Mgmt", category: "Governance" },
    { control_id: "ISO-A.5.21", title: "A.5.21 Supplier ICT Chain", description: "Managing ICT supply chain security risk.", process: "Supplier Mgmt", category: "Governance" },
    { control_id: "ISO-A.5.22", title: "A.5.22 Supplier Monitoring", description: "Monitoring, review and change management of supplier services.", process: "Supplier Mgmt", category: "Governance" },
    { control_id: "ISO-A.5.23", title: "A.5.23 Cloud Services", description: "Information security for use of cloud services.", process: "Supplier Mgmt", category: "Governance" },
    { control_id: "ISO-A.5.24", title: "A.5.24 Incident Mgmt Planning", description: "Planning and preparation for incident management.", process: "Incident & Resilience", category: "Governance" },
    { control_id: "ISO-A.5.25", title: "A.5.25 Assessment of Events", description: "Assessment and decision on information security events.", process: "Incident & Resilience", category: "Governance" },
    { control_id: "ISO-A.5.26", title: "A.5.26 Response to Incidents", description: "Response to information security incidents.", process: "Incident & Resilience", category: "Governance" },
    { control_id: "ISO-A.5.27", title: "A.5.27 Learning from Incidents", description: "Learning from information security incidents.", process: "Incident & Resilience", category: "Governance" },
    { control_id: "ISO-A.5.28", title: "A.5.28 Collection of Evidence", description: "Collection, identification, and preservation of evidence.", process: "Incident & Resilience", category: "Governance" },
    { control_id: "ISO-A.5.29", title: "A.5.29 Disruption Planning", description: "Planning to maintain operations during disruption.", process: "Incident & Resilience", category: "Governance" },
    { control_id: "ISO-A.5.30", title: "A.5.30 ICT Readiness", description: "ICT readiness for business continuity.", process: "Incident & Resilience", category: "Technical" },
    { control_id: "ISO-A.5.31", title: "A.5.31 Legal Obligations", description: "Identification of legal, statutory, regulatory requirements.", process: "Legal & Compliance", category: "Governance" },
    { control_id: "ISO-A.5.32", title: "A.5.32 IPR", description: "Intellectual property rights.", process: "Legal & Compliance", category: "Governance" },
    { control_id: "ISO-A.5.33", title: "A.5.33 Records Protection", description: "Protection of records.", process: "Asset Management", category: "Governance" },
    { control_id: "ISO-A.5.34", title: "A.5.34 Privacy", description: "Privacy and protection of PII.", process: "Legal & Compliance", category: "Governance" },
    { control_id: "ISO-A.5.35", title: "A.5.35 Review of InfoSec", description: "Independent review of information security.", process: "Risk Management", category: "Governance" },
    { control_id: "ISO-A.5.36", title: "A.5.36 Policies Review", description: "Compliance with policies and standards.", process: "Risk Management", category: "Governance" },
    { control_id: "ISO-A.5.37", title: "A.5.37 Operating Procedures", description: "Documented operating procedures.", process: "Operations (General)", category: "Governance" },

    // A.6 People (HR)
    { control_id: "ISO-A.6.1", title: "A.6.1 Screening", description: "Background verification checks for candidates.", process: "HR Security", category: "Governance" },
    { control_id: "ISO-A.6.2", title: "A.6.2 Terms of Employment", description: "Terms and conditions of employment.", process: "HR Security", category: "Governance" },
    { control_id: "ISO-A.6.3", title: "A.6.3 Awareness & Training", description: "Information security awareness, education, and training.", process: "HR Security", category: "Governance" },
    { control_id: "ISO-A.6.4", title: "A.6.4 Disciplinary Process", description: "Disciplinary process.", process: "HR Security", category: "Governance" },
    { control_id: "ISO-A.6.5", title: "A.6.5 Termination", description: "Responsibilities after termination or change of employment.", process: "HR Security", category: "Governance" },
    { control_id: "ISO-A.6.6", title: "A.6.6 NDA", description: "Confidentiality or non-disclosure agreements.", process: "HR Security", category: "Governance" },
    { control_id: "ISO-A.6.7", title: "A.6.7 Remote Work", description: "Security measures for remote working.", process: "Physical Security", category: "Governance" },
    { control_id: "ISO-A.6.8", title: "A.6.8 Event Reporting", description: "Information security event reporting.", process: "Incident & Resilience", category: "Governance" },

    // A.7 Physical
    { control_id: "ISO-A.7.1", title: "A.7.1 Physical Perimeters", description: "Security perimeters.", process: "Physical Security", category: "Physical" },
    { control_id: "ISO-A.7.2", title: "A.7.2 Physical Entry", description: "Physical entry controls.", process: "Physical Security", category: "Physical" },
    { control_id: "ISO-A.7.3", title: "A.7.3 Securing Offices", description: "Securing offices, rooms, and facilities.", process: "Physical Security", category: "Physical" },
    { control_id: "ISO-A.7.4", title: "A.7.4 Monitoring Physical", description: "Physical security monitoring.", process: "Physical Security", category: "Physical" },
    { control_id: "ISO-A.7.5", title: "A.7.5 Cabling", description: "Protecting against physical threats to cabling.", process: "Physical Security", category: "Physical" },
    { control_id: "ISO-A.7.6", title: "A.7.6 Maintenance", description: "Maintenance of equipment.", process: "Physical Security", category: "Physical" },
    { control_id: "ISO-A.7.7", title: "A.7.7 Clear Desk", description: "Clear desk and clear screen.", process: "Physical Security", category: "Governance" },
    { control_id: "ISO-A.7.8", title: "A.7.8 Equipment Siting", description: "Equipment siting and protection.", process: "Physical Security", category: "Physical" },
    { control_id: "ISO-A.7.9", title: "A.7.9 Off-Site Assets", description: "Security of assets off-premises.", process: "Physical Security", category: "Physical" },
    { control_id: "ISO-A.7.10", title: "A.7.10 Media", description: "Storage media.", process: "Asset Management", category: "Physical" },
    { control_id: "ISO-A.7.11", title: "A.7.11 Utilities", description: "Supporting utilities.", process: "Physical Security", category: "Physical" },
    { control_id: "ISO-A.7.12", title: "A.7.12 Cabling Security", description: "Cabling security.", process: "Physical Security", category: "Physical" },
    { control_id: "ISO-A.7.13", title: "A.7.13 Equipment Maintenance", description: "Equipment maintenance.", process: "Physical Security", category: "Physical" },
    { control_id: "ISO-A.7.14", title: "A.7.14 Disposal", description: "Secure disposal or re-use of equipment.", process: "Asset Management", category: "Physical" },

    // A.8 Technological
    { control_id: "ISO-A.8.1", title: "A.8.1 User Endpoint", description: "User endpoint devices.", process: "Operations (General)", category: "Technical" },
    { control_id: "ISO-A.8.2", title: "A.8.2 Privileged Access", description: "Privileged access rights.", process: "Access Control (IAM)", category: "Technical" },
    { control_id: "ISO-A.8.3", title: "A.8.3 Information Access", description: "Information access restriction.", process: "Access Control (IAM)", category: "Technical" },
    { control_id: "ISO-A.8.4", title: "A.8.4 Source Code Access", description: "Access to source code.", process: "SDLC (Development)", category: "Technical" },
    { control_id: "ISO-A.8.5", title: "A.8.5 Auth Systems", description: "Secure authentication.", process: "Access Control (IAM)", category: "Technical" },
    { control_id: "ISO-A.8.6", title: "A.8.6 Capacity Mgmt", description: "Capacity management.", process: "Operations (General)", category: "Technical" },
    { control_id: "ISO-A.8.7", title: "A.8.7 Malware", description: "Protection against malware.", process: "Operations (General)", category: "Technical" },
    { control_id: "ISO-A.8.8", title: "A.8.8 Vulnerability Mgmt", description: "Management of technical vulnerabilities.", process: "Vulnerability Management", category: "Technical" },
    { control_id: "ISO-A.8.9", title: "A.8.9 Config Mgmt", description: "Configuration management.", process: "Configuration Management", category: "Technical" },
    { control_id: "ISO-A.8.10", title: "A.8.10 Info Deletion", description: "Information deletion.", process: "Operations (General)", category: "Technical" },
    { control_id: "ISO-A.8.11", title: "A.8.11 Data Masking", description: "Data masking.", process: "Cryptography", category: "Technical" },
    { control_id: "ISO-A.8.12", title: "A.8.12 DLP", description: "Data leakage prevention.", process: "Operations (General)", category: "Technical" },
    { control_id: "ISO-A.8.13", title: "A.8.13 Backups", description: "Information backup.", process: "Backup Management", category: "Technical" },
    { control_id: "ISO-A.8.14", title: "A.8.14 Redundancy", description: "Redundancy of information processing facilities.", process: "Operations (General)", category: "Technical" },
    { control_id: "ISO-A.8.15", title: "A.8.15 Logging", description: "Logging.", process: "Logging & Monitoring", category: "Technical" },
    { control_id: "ISO-A.8.16", title: "A.8.16 Monitoring", description: "Monitoring activities.", process: "Logging & Monitoring", category: "Technical" },
    { control_id: "ISO-A.8.17", title: "A.8.17 Clock Sync", description: "Clock synchronization.", process: "Logging & Monitoring", category: "Technical" },
    { control_id: "ISO-A.8.18", title: "A.8.18 Privileged Utility", description: "Use of privileged utility programs.", process: "Operations (General)", category: "Technical" },
    { control_id: "ISO-A.8.19", title: "A.8.19 Operational Software", description: "Installation of software on operational systems.", process: "Operations (General)", category: "Technical" },
    { control_id: "ISO-A.8.20", title: "A.8.20 Network Security", description: "Networks security.", process: "Network Security", category: "Technical" },
    { control_id: "ISO-A.8.21", title: "A.8.21 Network Services", description: "Security of network services.", process: "Network Security", category: "Technical" },
    { control_id: "ISO-A.8.22", title: "A.8.22 Network Segregation", description: "Segregation of networks.", process: "Network Security", category: "Technical" },
    { control_id: "ISO-A.8.23", title: "A.8.23 Web Filtering", description: "Web filtering.", process: "Network Security", category: "Technical" },
    { control_id: "ISO-A.8.24", title: "A.8.24 Cryptography", description: "Use of cryptography.", process: "Cryptography", category: "Technical" },
    { control_id: "ISO-A.8.25", title: "A.8.25 Secure Dev Lifecycle", description: "Secure development lifecycle.", process: "SDLC (Development)", category: "Technical" },
    { control_id: "ISO-A.8.26", title: "A.8.26 App Requirements", description: "Application security requirements.", process: "SDLC (Development)", category: "Technical" },
    { control_id: "ISO-A.8.27", title: "A.8.27 Secure Architecture", description: "Secure system architecture and engineering principles.", process: "SDLC (Development)", category: "Technical" },
    { control_id: "ISO-A.8.28", title: "A.8.28 Secure Coding", description: "Secure coding.", process: "SDLC (Development)", category: "Technical" },
    { control_id: "ISO-A.8.29", title: "A.8.29 Security Testing", description: "Security testing in development and acceptance.", process: "SDLC (Development)", category: "Technical" },
    { control_id: "ISO-A.8.30", title: "A.8.30 Outsourced Dev", description: "Outsourced development.", process: "SDLC (Development)", category: "Technical" },
    { control_id: "ISO-A.8.31", title: "A.8.31 Env Separation", description: "Separation of development, test, and production environments.", process: "SDLC (Development)", category: "Technical" },
    { control_id: "ISO-A.8.32", title: "A.8.32 Change Mgmt", description: "Change management.", process: "SDLC (Development)", category: "Technical" },
    { control_id: "ISO-A.8.33", title: "A.8.33 Test Info", description: "Test information.", process: "SDLC (Development)", category: "Technical" },
    { control_id: "ISO-A.8.34", title: "A.8.34 Audit Protection", description: "Protection of information systems during audit testing.", process: "SDLC (Development)", category: "Technical" }
];

// ============================================================================
// SOC 2 - COSO MAPPED (USER DEFINED P1-P17)
// ============================================================================
export const SOC2_CONTROLS = [
    // --- SECURITY (CC) - COMMON CRITERIA ---
    // CC1: Control Environment (COSO 1-5)
    { control_id: "CC1.1", title: "CC1.1 - Integrity & Ethics", description: "The entity demonstrates a commitment to integrity and ethical values.", category: "Security" },
    { control_id: "CC1.2", title: "CC1.2 - Board Oversight", description: "The board demonstrates independence and exercises oversight of internal control.", category: "Security" },
    { control_id: "CC1.3", title: "CC1.3 - Structure & Authority", description: "Management establishes structures, reporting lines, and authorities.", category: "Security" },
    { control_id: "CC1.4", title: "CC1.4 - Competence", description: "The entity demonstrates a commitment to attract, develop, and retain competent individuals.", category: "Security" },
    { control_id: "CC1.5", title: "CC1.5 - Accountability", description: "The entity holds individuals accountable for internal control responsibilities.", category: "Security" },

    // CC2: Communication & Info (COSO 13-15)
    { control_id: "CC2.1", title: "CC2.1 - Quality Information", description: "The entity uses relevant, quality information to support internal control.", category: "Security" },
    { control_id: "CC2.2", title: "CC2.2 - Internal Communication", description: "The entity communicates information internally (objectives/responsibilities).", category: "Security" },
    { control_id: "CC2.3", title: "CC2.3 - External Communication", description: "The entity communicates with external parties regarding internal control matters.", category: "Security" },

    // CC3: Risk Assessment (COSO 6-9)
    { control_id: "CC3.1", title: "CC3.1 - Specific Objectives", description: "The entity specifies objectives with clarity to enable risk identification.", category: "Security" },
    { control_id: "CC3.2", title: "CC3.2 - Risk Identification", description: "The entity identifies and analyzes risks to the achievement of objectives.", category: "Security" },
    { control_id: "CC3.3", title: "CC3.3 - Fraud Risk", description: "The entity considers the potential for fraud in assessing risks.", category: "Security" },
    { control_id: "CC3.4", title: "CC3.4 - Change Management (Risk)", description: "The entity assesses changes that could impact the system of internal control.", category: "Security" },

    // CC4: Monitoring (COSO 16-17)
    { control_id: "CC4.1", title: "CC4.1 - Ongoing Evaluations", description: "The entity performs ongoing evaluations of internal control (Monitoring).", category: "Security" },
    { control_id: "CC4.2", title: "CC4.2 - Deficiency Reporting", description: "The entity communicates deficiencies timely to those responsible.", category: "Security" },

    // CC5: Control Activities (COSO 10-12)
    { control_id: "CC5.1", title: "CC5.1 - Risk Mitigation", description: "The entity selects control activities that mitigate risks to acceptable levels.", category: "Security" },
    { control_id: "CC5.2", title: "CC5.2 - Tech Controls", description: "The entity selects general control activities over technology.", category: "Security" },
    { control_id: "CC5.3", title: "CC5.3 - Policies", description: "The entity deploys control activities through policies and procedures.", category: "Security" },

    // CC6: Logical and Physical Access
    { control_id: "CC6.1", title: "CC6.1 - Logical Access", description: "The entity implements logical access security software, infrastructure, and architectures.", category: "Security" },
    { control_id: "CC6.2", title: "CC6.2 - User Registration", description: "Prior to issuing system credentials, the entity registers and authorizes new users.", category: "Security" },
    { control_id: "CC6.3", title: "CC6.3 - Access Modifications", description: "The entity authorizes and modifies access to protected information assets.", category: "Security" },
    { control_id: "CC6.4", title: "CC6.4 - Physical Access", description: "The entity restricts physical access to facilities and protected information assets.", category: "Security" },
    { control_id: "CC6.5", title: "CC6.5 - Disposal of Credentials", description: "The entity discontinues logical and physical access when no longer needed.", category: "Security" },
    { control_id: "CC6.6", title: "CC6.6 - External Access", description: "The entity implements controls to protect against unauthorized external access.", category: "Security" },
    { control_id: "CC6.7", title: "CC6.7 - Transmission Security", description: "The entity restricts the transmission of protected information over networks.", category: "Security" },
    { control_id: "CC6.8", title: "CC6.8 - Malware Protection", description: "The entity implements controls to prevent, detect, and act upon malicious software.", category: "Security" },

    // CC7: System Operations
    { control_id: "CC7.1", title: "CC7.1 - Configuration Monitoring", description: "The entity monitors system configuration for compliance with baselines.", category: "Security" },
    { control_id: "CC7.2", title: "CC7.2 - Vulnerability Management", description: "The entity monitors for vulnerabilities and remediates them.", category: "Security" },
    { control_id: "CC7.3", title: "CC7.3 - Incident Detection", description: "The entity evaluates security events to determine if they are incidents.", category: "Security" },
    { control_id: "CC7.4", title: "CC7.4 - Incident Response", description: "The entity responds to identified security incidents.", category: "Security" },
    { control_id: "CC7.5", title: "CC7.5 - Disaster Recovery", description: "The entity implements distinct procedures to restore operations after a disruption.", category: "Security" },

    // CC8: Change Management
    { control_id: "CC8.1", title: "CC8.1 - Change Management", description: "The entity authorizes, designs, develops, tests, approves, and implements changes.", category: "Security" },

    // CC9: Risk Mitigation
    { control_id: "CC9.1", title: "CC9.1 - Vendor Management", description: "The entity identifies, selects, and manages risks associated with vendors.", category: "Security" },
    { control_id: "CC9.2", title: "CC9.2 - Insider Threat", description: "The entity assesses and manages risks associated with vendors and business partners.", category: "Security" },

    // --- AVAILABILITY (A) ---
    { control_id: "A1.1", title: "A1.1 - Capacity Management", description: "The entity maintains, monitors, and evaluates current processing capacity.", category: "Availability" },
    { control_id: "A1.2", title: "A1.2 - Environmental Controls", description: "The entity authorizes, designs, develops, implements, operates, approves, and monitors environmental protections.", category: "Availability" },
    { control_id: "A1.3", title: "A1.3 - Data Backup & Recovery", description: "The entity tests recovery plan procedures to support the recovery of the system.", category: "Availability" },

    // --- CONFIDENTIALITY (C) ---
    { control_id: "C1.1", title: "C1.1 - Confidentiality", description: "The entity identifies and maintains confidential information to meet objectives.", category: "Confidentiality" },
    { control_id: "C1.2", title: "C1.2 - Disposal", description: "The entity disposes of confidential information to meet objectives.", category: "Confidentiality" },

    // --- PROCESSING INTEGRITY (PI) ---
    { control_id: "PI1.1", title: "PI1.1 - Processing Objective", description: "The entity obtains or generates, uses, and communicates relevant quality information regarding processing.", category: "Processing Integrity" },
    { control_id: "PI1.2", title: "PI1.2 - System Inputs", description: "The entity implements policies and procedures over system inputs (completeness/accuracy).", category: "Processing Integrity" },
    { control_id: "PI1.3", title: "PI1.3 - Data Processing", description: "The entity implements policies and procedures over system processing to meet objectives.", category: "Processing Integrity" },
    { control_id: "PI1.4", title: "PI1.4 - Data Storage", description: "The entity implements policies and procedures to direct data storage and maintenance.", category: "Processing Integrity" },
    { control_id: "PI1.5", title: "PI1.5 - System Outputs", description: "The entity implements policies and procedures over system outputs.", category: "Processing Integrity" },

    // --- PRIVACY (P) ---
    { control_id: "P1.0", title: "P1.0 - Notice", description: "The entity provides notice to privacy principals about its privacy practices.", category: "Privacy" },
    { control_id: "P2.0", title: "P2.0 - Choice and Consent", description: "The entity communicates choices available regarding personal information.", category: "Privacy" },
    { control_id: "P3.0", title: "P3.0 - Collection", description: "The entity collects personal information only as necessary.", category: "Privacy" },
    { control_id: "P4.0", title: "P4.0 - Use, Retention, Disposal", description: "The entity limits the use, retention, and disposal of personal information.", category: "Privacy" },
    { control_id: "P5.0", title: "P5.0 - Access", description: "The entity provides privacy principals with access to their personal information.", category: "Privacy" },
    { control_id: "P6.0", title: "P6.0 - Disclosure", description: "The entity discloses personal information to third parties only with consent.", category: "Privacy" },
    { control_id: "P7.0", title: "P7.0 - Quality", description: "The entity collects and maintains accurate, up-to-date, complete, and relevant personal information.", category: "Privacy" },
    { control_id: "P8.0", title: "P8.0 - Monitoring", description: "The entity monitors compliance to meet its objectives related to privacy.", category: "Privacy" }
];

export const HIPPA_CONTROLS = [
    { title: "Access Control", description: "Implement technical policies and procedures for electronic information systems that maintain electronic protected health information to allow access only to those persons or software programs that have been granted access rights.", category: "Technical Safeguards" }
];

export const NIST_CONTROLS = [
    { title: "ID.AM-1", description: "Physical devices and systems within the organization are inventoried.", category: "Identify" }
];

export const GDPR_CONTROLS = [
    { title: "Article 5", description: "Principles relating to processing of personal data.", category: "Principles" }
];
