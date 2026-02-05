"""
Update all control descriptions to be task-oriented
Remove grey text (ai_explanation field)
Based on ISO 27001:2022 standard
"""

import sqlite3
import shutil
from datetime import datetime
from pathlib import Path

DB_PATH = "sql_app.db"
BACKUP_NAME = f"backup_update_descriptions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"

# ISO 27001:2022 Task-Oriented Descriptions
DESCRIPTIONS = {
    # Clause 4: Context of the organization
    "4.1": "External and internal issues relevant to the organization's purpose and that affect its ability to achieve the intended outcomes of the ISMS are determined and documented.",
    "4.2": "The needs and expectations of interested parties relevant to the ISMS are determined and documented.",
    "4.3": "The boundaries and applicability of the ISMS are determined and documented to establish the scope.",
    "4.4": "The processes needed for the ISMS and their interactions are established, implemented, maintained and continually improved.",
    
    # Clause 5: Leadership
    "5.1": "Top management demonstrates leadership and commitment to the ISMS by ensuring integration with business processes and availability of resources.",
    "5.2": "An information security policy appropriate to the organization is established, documented, communicated and made available.",
    "5.3": "Organizational roles, responsibilities and authorities for information security are assigned, communicated and understood.",
    
    # Clause 6: Planning
    "6.1.1": "Risks and opportunities that need to be addressed to achieve ISMS intended outcomes are determined.",
    "6.1.2": "Information security risks are assessed using an established risk assessment process.",
    "6.1.3": "Information security risks are treated in accordance with the risk treatment plan.",
    "6.2": "Information security objectives are established at relevant functions and levels, are measurable, and consistent with the policy.",
    "6.3": "Changes to the ISMS are planned and implemented in a controlled manner while maintaining the integrity of the ISMS.",
    
    # Clause 7: Support
    "7.1": "Resources needed to establish, implement, maintain and continually improve the ISMS are determined and provided.",
    "7.2": "Personnel performing work affecting information security are competent, based on appropriate education, training, skills and experience.",
    "7.3": "Personnel are made aware of the information security policy, their contribution to ISMS effectiveness, and the implications of not conforming.",
    "7.4": "Internal and external communications relevant to the ISMS are determined, including what, when, with whom and how to communicate.",
    "7.5.1": "Documented information required by the ISMS and this document is created, updated and controlled.",
    "7.5.2": "Documented information is created, updated and its format, media, and approval defined.",
    "7.5.3": "Documented information is controlled to ensure it is available, suitable, protected and preserved.",
    
    # Clause 8: Operation
    "8.1": "The processes needed to meet information security requirements are planned, implemented and controlled.",
    "8.2": "Information security risk assessments are performed at planned intervals or when significant changes occur.",
    "8.3": "The information security risk treatment plan is implemented.",
    
    # Clause 9: Performance evaluation
    "9.1": "Information security performance and ISMS effectiveness are monitored, measured, analyzed and evaluated.",
    "9.2.1": "An internal audit program is planned, established, implemented and maintained.",
    "9.2.2": "Internal audits are conducted at planned intervals to verify ISMS conformity and effectiveness.",
    "9.3.1": "Top management reviews the ISMS at planned intervals considering defined inputs.",
    "9.3.2": "Management review outputs include decisions related to continual improvement and any need for changes to the ISMS.",
    "9.3.3": "Evidence of management review results is retained as documented information.",
    
    # Clause 10: Improvement
    "10.1": "Nonconformities are identified, reacted to, evaluated and corrective actions taken.",
    "10.2": "The suitability, adequacy and effectiveness of the ISMS are continually improved.",
    
    # Annex A: Information security controls
    # A.5: Organizational controls
    "A.5.1": "Information security policies are defined, approved, published, communicated and acknowledged by relevant personnel.",
    "A.5.2": "Information security roles and responsibilities are defined, allocated and communicated.",
    "A.5.3": "Conflicting duties and areas of responsibility are segregated to reduce opportunities for unauthorized or unintentional modification.",
    "A.5.4": "Management responsibilities for implementing and operating the ISMS in accordance with policies are defined and allocated.",
    "A.5.5": "Relationships with authorities are established and maintained, and contact with relevant authorities is maintained.",
    "A.5.6": "Relationships with special interest groups or security forums are established and maintained.",
    "A.5.7": "Information about information security threats is collected and analyzed to produce threat intelligence.",
    "A.5.8": "Information security is integrated into project management activities regardless of project type.",
    "A.5.9": "An inventory of information and other associated assets is developed, maintained and includes ownership.",
    "A.5.10": "Rules for acceptable use and procedures for handling information and assets are identified, documented and implemented.",
    "A.5.11": "Personnel and external party users return all organizational assets in their possession upon change or termination of employment.",
    "A.5.12": "Information is classified according to legal, value, criticality and sensitivity requirements.",
    "A.5.13": "A set of procedures for information labelling is developed and implemented in accordance with the classification scheme.",
    "A.5.14": "Information transfer rules, procedures or agreements are established for all types of transfer facilities.",
    "A.5.15": "Rules to control physical and logical access to information and other associated assets are established and implemented.",
    "A.5.16": "The full life cycle of identities is managed including joiners, movers and leavers.",
    "A.5.17": "The allocation and management of authentication information is controlled through a management process including advising personnel on proper handling.",
    "A.5.18": "Access rights to information and other associated assets are provisioned, reviewed, modified and removed in accordance with the organization's policy.",
    "A.5.19": "Rules, responsibilities and procedures for information security in supplier relationships are established and agreed.",
    "A.5.20": "Requirements for information security are addressed within supplier agreements or arrangements.",
    "A.5.21": "Processes and procedures are established to manage information security risks associated with ICT products and services in the supply chain.",
    "A.5.22": "Performance of information security in supplier relationships is monitored, reviewed, evaluated and managed regularly.",
    "A.5.23": "Procedures for the use, protection and availability of cloud services are established in accordance with security requirements.",
    "A.5.24": "The organization plans, prepares and practices procedures for managing information security incidents.",
    "A.5.25": "Information security events are assessed to determine if they are to be classified as information security incidents.",
    "A.5.26": "Information security incidents are responded to in accordance with documented procedures.",
    "A.5.27": "Knowledge gained from information security incidents is used to strengthen and improve controls.",
    "A.5.28": "Rules and procedures for the identification, collection, acquisition and preservation of evidence are established and applied.",
    "A.5.29": "The organization plans how to maintain information security at an appropriate level during disruption.",
    "A.5.30": "ICT readiness is planned, implemented, maintained and tested based on business continuity objectives.",
    "A.5.31": "Legal, statutory, regulatory and contractual requirements relevant to information security are identified, documented and kept up to date.",
    "A.5.32": "Procedures are implemented to protect intellectual property rights and verify compliance with legal requirements.",
    "A.5.33": "Records are protected from loss, destruction, falsification, unauthorized access and unauthorized release.",
    "A.5.34": "Privacy and protection of personally identifiable information (PII) are ensured as required by law and regulations.",
    "A.5.35": "The organization's approach to managing information security and its implementation are reviewed independently at planned intervals.",
    "A.5.36": "Regular reviews are conducted to ensure continuing compliance with information security policies, rules and standards.",
    "A.5.37": "Operating procedures for information processing facilities are documented and made available to personnel who need them.",
    
    # A.6: People controls
    "A.6.1": "Background verification checks on all candidates for employment are carried out according to relevant laws and ethics.",
    "A.6.2": "Contractual agreements with personnel state their and the organization's responsibilities for information security.",
    "A.6.3": "Personnel receive appropriate awareness, education and training on information security, and regular updates on policies and procedures.",
    "A.6.4": "A formal disciplinary process is established to take action against personnel who have committed a security breach.",
    "A.6.5": "Information security responsibilities and duties that remain valid after termination or change of employment are communicated to personnel.",
    "A.6.6": "All relevant personnel and external parties sign appropriate confidentiality or non-disclosure agreements.",
    "A.6.7": "Security measures are implemented when personnel work remotely to protect information accessed, processed or stored.",
    "A.6.8": "Personnel are required to report observed or suspected information security events through appropriate channels in a timely manner.",
    
    # A.7: Physical controls
    "A.7.1": "Security perimeters are defined and used to protect areas containing information and other associated assets.",
    "A.7.2": "Secure areas are protected by appropriate entry controls to ensure only authorized personnel are allowed access.",
    "A.7.3": "Physical security for offices, rooms and facilities is designed and implemented.",
    "A.7.4": "Premises are continuously monitored for unauthorized physical access.",
    "A.7.5": "Physical protection against natural disasters, malicious attack or accidents is designed and implemented.",
    "A.7.6": "Security measures for working in secure areas are designed and implemented.",
    "A.7.7": "Clear desk rules for papers and removable storage media and clear screen rules are defined and appropriately enforced.",
    "A.7.8": "Equipment is sited and protected to reduce risks from environmental threats and hazards.",
    "A.7.9": "Assets off-premises are protected.",
    "A.7.10": "Storage media are managed throughout their life cycle in accordance with classification and handling requirements.",
    "A.7.11": "Equipment is protected from power failures and other disruptions caused by failures in supporting utilities.",
    "A.7.12": "Security of cabling is ensured to protect from interception, interference or damage.",
    "A.7.13": "Equipment is maintained correctly to ensure availability, integrity and confidentiality of information.",
    "A.7.14": "Items of equipment containing storage media are verified to ensure sensitive data has been removed before disposal or reuse.",
    
    # A.8: Technological controls
    "A.8.1": "User endpoint devices are configured and managed with consideration for security needs and business use.",
    "A.8.2": "Access rights to privileged utility programs are restricted and tightly controlled.",
    "A.8.3": "Access to information and application system functions is restricted in accordance with the access control policy.",
    "A.8.4": "Read and write access to source code is appropriately restricted.",
    "A.8.5": "Secure authentication methods are selected and implemented based on information access restrictions and the access control policy.",
    "A.8.6": "Resource use is monitored and projections of future capacity requirements are made to ensure required system performance.",
    "A.8.7": "Detection, prevention and recovery controls to protect against malware are implemented combined with appropriate user awareness.",
    "A.8.8": "Technical vulnerabilities of information systems in use are identified and appropriate measures taken in a timely manner.",
    "A.8.9": "Configurations of hardware, software, services and networks are established, documented, implemented, monitored and reviewed.",
    "A.8.10": "Information is deleted when no longer required in accordance with retention requirements and procedures.",
    "A.8.11": "Data masking is used in accordance with the access control policy and other related requirements.",
    "A.8.12": "Data leakage prevention measures are applied to systems, networks and other devices that process, store or transmit sensitive information.",
    "A.8.13": "Backup copies of information, software and systems are maintained and regularly tested in accordance with the agreed backup policy.",
    "A.8.14": "Redundant information processing facilities are implemented to achieve required availability levels.",
    "A.8.15": "Event logs recording user activities, exceptions, faults and information security events are produced, kept and regularly reviewed.",
    "A.8.16": "Information processing facilities and communication channels are monitored to detect anomalous behavior and information security events.",
    "A.8.17": "Clocks of all information processing systems within the organization or security domain are synchronized to a single reference time source.",
    "A.8.18": "Use of utility programs capable of overriding system and application controls is restricted and tightly controlled.",
    "A.8.19": "Rules governing the installation of software by users are established and implemented.",
    "A.8.20": "Networks and network devices are secured, managed and controlled to protect information in systems and applications.",
    "A.8.21": "Security mechanisms, service levels and service requirements of network services are identified, implemented and monitored.",
    "A.8.22": "Groups of information services, users and information systems are segregated in the organization's networks.",
    "A.8.23": "Access to external websites is managed to reduce exposure to malicious content.",
    "A.8.24": "Cryptographic controls are used to protect confidentiality, authenticity and/or integrity of information in accordance with policies.",
    "A.8.25": "Rules for the secure development of software and systems are established and applied.",
    "A.8.26": "Information security requirements are identified, specified and approved when developing or acquiring applications.",
    "A.8.27": "Secure system architecture and engineering principles are established, documented, maintained and applied.",
    "A.8.28": "Secure coding principles are applied to software development.",
    "A.8.29": "Security testing and acceptance criteria are defined and carried out during the development cycle.",
    "A.8.30": "Outsourced system development is directed, monitored and reviewed.",
    "A.8.31": "Development, testing and production environments are separated and secured.",
    "A.8.32": "Changes to information processing facilities and systems are subject to change management procedures.",
    "A.8.33": "Test data is selected, protected and controlled.",
    "A.8.34": "Information systems are protected from information loss or compromise during audit testing activities.",
}

def main():
    print("=" * 80)
    print("UPDATE CONTROL DESCRIPTIONS - TASK-ORIENTED FORMAT")
    print("=" * 80)
    
    if not Path(DB_PATH).exists():
        print(f"\n❌ ERROR: Database '{DB_PATH}' not found!")
        return 1
    
    # Backup
    print(f"\n1. Creating backup: {BACKUP_NAME}")
    try:
        shutil.copy2(DB_PATH, BACKUP_NAME)
        print(f"   ✅ Backup created successfully")
    except Exception as e:
        print(f"   ❌ Backup failed: {e}")
        return 1
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        print(f"\n2. Updating {len(DESCRIPTIONS)} control descriptions...")
        updated_count = 0
        
        for ctrl_id, description in DESCRIPTIONS.items():
            cursor.execute("""
                UPDATE controls
                SET description = ?,
                    ai_explanation = NULL
                WHERE framework_id = 13
                AND control_id = ?
            """, (description, ctrl_id))
            
            if cursor.rowcount > 0:
                updated_count += 1
        
        print(f"   ✅ Updated {updated_count} control descriptions")
        print(f"   ✅ Cleared ai_explanation field (removed grey text)")
        
        # Commit
        conn.commit()
        print(f"\n   ✅ Changes committed to database")
        
    except Exception as e:
        print(f"\n   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        conn.close()
        return 1
    
    # Verify
    print(f"\n3. Verification...")
    
    cursor.execute("""
        SELECT COUNT(*)
        FROM controls
        WHERE framework_id = 13
        AND (description IS NULL OR description = '')
    """)
    
    no_desc = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT COUNT(*)
        FROM controls
        WHERE framework_id = 13
        AND ai_explanation IS NOT NULL
    """)
    
    has_grey = cursor.fetchone()[0]
    
    # Show sample
    print(f"\n4. Sample updated descriptions:")
    cursor.execute("""
        SELECT control_id, description
        FROM controls
        WHERE framework_id = 13
        AND control_id IN ('4.1', '6.2', 'A.5.1', 'A.8.24')
        ORDER BY control_id
    """)
    
    for ctrl_id, desc in cursor.fetchall():
        print(f"\n   {ctrl_id}:")
        print(f"   {desc}")
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("UPDATE COMPLETE")
    print("=" * 80)
    
    print(f"\n   Updated: {updated_count} controls")
    print(f"   Without description: {no_desc}")
    print(f"   With grey text: {has_grey}")
    
    if no_desc == 0 and has_grey == 0:
        print(f"\n🎉 PERFECT!")
        print(f"   ✅ All controls have descriptions")
        print(f"   ✅ No grey text (ai_explanation cleared)")
    
    print(f"\n✅ Backup saved as: {BACKUP_NAME}")
    print(f"\n🔄 Next step: Restart backend and check frontend")
    
    return 0

if __name__ == "__main__":
    exit(main())
