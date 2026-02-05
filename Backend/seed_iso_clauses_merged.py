"""
Seed script to populate ISO 27001:2022 ISMS Requirements (Clauses 4-10) into the MAIN ISO27001 framework
"""

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models.framework import Framework
from app.models.control import Control, ControlStatus

def get_db():
    db = SessionLocal()
    try:
        return db
    except Exception as e:
        db.close()
        raise e

def get_framework(db: Session):
    # Get the MAIN ISO framework
    existing = db.query(Framework).filter(Framework.code == "ISO27001").first()
    if not existing:
        print("ISO 27001 Framework not found! Run seed_iso27001.py first.")
        return None
    
    print(f"Targeting Framework: {existing.name} (ID: {existing.id})")
    return existing

def create_requirements(db: Session, framework_id: int):
    # COPY THE DATA from the previous file content (I will paste it here)
    # Since I cannot import easily, I'll include the dict.
    requirements_data = [
        # CLAUSE 4: CONTEXT OF THE ORGANIZATION
        {
            "control_id": "4.1",
            "title": "Understanding the organization and its context",
            "description": "The organization shall determine external and internal issues that are relevant to its purpose and that affect its ability to achieve the intended outcome(s) of its information security management system.",
            "category": "Clause 4: Context of the organization",
            "priority": "high"
        },
        {
            "control_id": "4.2",
            "title": "Understanding the needs and expectations of interested parties",
            "description": "The organization shall determine: a) interested parties that are relevant to the information security management system; and b) the requirements of these interested parties relevant to information security.",
            "category": "Clause 4: Context of the organization",
            "priority": "high"
        },
        {
            "control_id": "4.3",
            "title": "Determining the scope of the information security management system",
            "description": "The organization shall determine the boundaries and applicability of the information security management system to establish its scope. When determining this scope, the organization shall consider: a) the external and internal issues referred to in 4.1; b) the requirements referred to in 4.2; and c) interfaces and dependencies between activities performed by the organization, and those that are performed by other organizations.",
            "category": "Clause 4: Context of the organization",
            "priority": "high"
        },
        {
            "control_id": "4.4",
            "title": "Information security management system",
            "description": "The organization shall establish, implement, maintain and continually improve an information security management system, in accordance with the requirements of this document.",
            "category": "Clause 4: Context of the organization",
            "priority": "high"
        },
        
        # CLAUSE 5: LEADERSHIP
        {
            "control_id": "5.1",
            "title": "Leadership and commitment",
            "description": "Top management shall demonstrate leadership and commitment with respect to the information security management system by: a) ensuring the information security policy and the information security objectives are established and are compatible with the strategic direction of the organization; b) ensuring the integration of the information security management system requirements into the organization's processes; c) ensuring that the resources needed for the information security management system are available; d) communicating the importance of effective information security management and of conforming to the information security management system requirements; e) ensuring that the information security management system achieves its intended outcome(s); f) directing and supporting persons to contribute to the effectiveness of the information security management system; g) promoting continual improvement; and h) supporting other relevant management roles to demonstrate their leadership as it applies to their areas of responsibility.",
            "category": "Clause 5: Leadership",
            "priority": "high"
        },
        {
            "control_id": "5.2",
            "title": "Policy",
            "description": "Top management shall establish an information security policy that: a) is appropriate to the purpose of the organization; b) includes information security objectives (see 6.2) or provides the framework for setting information security objectives; c) includes a commitment to satisfy applicable requirements related to information security; and d) includes a commitment to continual improvement of the information security management system. The information security policy shall: e) be available as documented information; f) be communicated within the organization; and g) be available to interested parties, as appropriate.",
            "category": "Clause 5: Leadership",
            "priority": "high"
        },
        {
            "control_id": "5.3",
            "title": "Organizational roles, responsibilities and authorities",
            "description": "Top management shall ensure that the responsibilities and authorities for roles relevant to information security are assigned and communicated. Top management shall assign the responsibility and authority for: a) ensuring that the information security management system conforms to the requirements of this document; and b) reporting on the performance of the information security management system to top management.",
            "category": "Clause 5: Leadership",
            "priority": "high"
        },
        
        # CLAUSE 6: PLANNING
        {
            "control_id": "6.1.1",
            "title": "General (Actions to address risks and opportunities)",
            "description": "When planning for the information security management system, the organization shall consider the issues referred to in 4.1 and the requirements referred to in 4.2 and determine the risks and opportunities that need to be addressed to: a) ensure the information security management system can achieve its intended outcome(s); b) prevent, or reduce, undesired effects; and c) achieve continual improvement.",
            "category": "Clause 6: Planning",
            "priority": "high"
        },
        {
            "control_id": "6.1.2",
            "title": "Information security risk assessment",
            "description": "The organization shall define and apply an information security risk assessment process that: a) establishes and maintains information security risk criteria; b) ensures that repeated information security risk assessments produce consistent, valid and comparable results; c) identifies the information security risks (risk identification process, risk owners, risk criteria); d) analyses the information security risks (assess potential consequences, assess realistic likelihood, determine levels of risk); and e) evaluates the information security risks (compare results with risk criteria, prioritize for risk treatment).",
            "category": "Clause 6: Planning",
            "priority": "high"
        },
        {
            "control_id": "6.1.3",
            "title": "Information security risk treatment",
            "description": "The organization shall define and apply an information security risk treatment process to: a) select appropriate information security risk treatment options, taking account of the risk assessment results; b) determine all controls that are necessary to implement the information security risk treatment option(s) chosen; c) compare the controls determined in 6.1.3 b) above with those in Annex A and verify that no necessary controls have been omitted; d) produce a Statement of Applicability that contains the necessary controls and justification for inclusions and exclusions; e) formulate an information security risk treatment plan; and f) obtain risk owners' approval of the information security risk treatment plan and acceptance of the residual information security risks.",
            "category": "Clause 6: Planning",
            "priority": "high"
        },
        {
            "control_id": "6.2",
            "title": "Information security objectives and planning to achieve them",
            "description": "The organization shall establish information security objectives at relevant functions and levels. The information security objectives shall: a) be consistent with the information security policy; b) be measurable (if practicable); c) take into account applicable information security requirements, and results from risk assessment and risk treatment; d) be communicated; and e) be updated as appropriate. When planning how to achieve its information security objectives, the organization shall determine: what will be done; what resources will be required; who will be responsible; when it will be completed; and how the results will be evaluated.",
            "category": "Clause 6: Planning",
            "priority": "high"
        },
        {
            "control_id": "6.3",
            "title": "Planning of changes",
            "description": "When the organization determines the need for changes to the information security management system, the changes shall be carried out in a planned manner.",
            "category": "Clause 6: Planning",
            "priority": "medium"
        },
        
        # CLAUSE 7: SUPPORT
        {
            "control_id": "7.1",
            "title": "Resources",
            "description": "The organization shall determine and provide the resources needed for the establishment, implementation, maintenance and continual improvement of the information security management system.",
            "category": "Clause 7: Support",
            "priority": "high"
        },
        {
            "control_id": "7.2",
            "title": "Competence",
            "description": "The organization shall: a) determine the necessary competence of person(s) doing work under its control that affects its information security performance; b) ensure that these persons are competent on the basis of appropriate education, training, or experience; c) where applicable, take actions to acquire the necessary competence, and evaluate the effectiveness of the actions taken; and d) retain appropriate documented information as evidence of competence.",
            "category": "Clause 7: Support",
            "priority": "high"
        },
        {
            "control_id": "7.3",
            "title": "Awareness",
            "description": "Persons doing work under the organization's control shall be aware of: a) the information security policy; b) their contribution to the effectiveness of the information security management system, including the benefits of improved information security performance; and c) the implications of not conforming with the information security management system requirements.",
            "category": "Clause 7: Support",
            "priority": "high"
        },
        {
            "control_id": "7.4",
            "title": "Communication",
            "description": "The organization shall determine the need for internal and external communications relevant to the information security management system including: a) on what to communicate; b) when to communicate; c) with whom to communicate; and d) who shall communicate.",
            "category": "Clause 7: Support",
            "priority": "medium"
        },
        {
            "control_id": "7.5.1",
            "title": "General (Documented information)",
            "description": "The organization's information security management system shall include: a) documented information required by this document; and b) documented information determined by the organization as being necessary for the effectiveness of the information security management system.",
            "category": "Clause 7: Support",
            "priority": "high"
        },
        {
            "control_id": "7.5.2",
            "title": "Creating and updating (Documented information)",
            "description": "When creating and updating documented information the organization shall ensure appropriate: a) identification and description (e.g. a title, date, author, or reference number); b) format (e.g. language, software version, graphics) and media (e.g. paper, electronic); and c) review and approval for suitability and adequacy.",
            "category": "Clause 7: Support",
            "priority": "medium"
        },
        {
            "control_id": "7.5.3",
            "title": "Control of documented information",
            "description": "Documented information required by the information security management system and by this document shall be controlled to ensure: a) it is available and suitable for use, where and when it is needed; and b) it is adequately protected (e.g. from loss of confidentiality, improper use, or loss of integrity). For the control of documented information, the organization shall address distribution, access, retrieval and use; storage and preservation, including preservation of legibility; control of changes; retention and disposition.",
            "category": "Clause 7: Support",
            "priority": "medium"
        },
        
        # CLAUSE 8: OPERATION
        {
            "control_id": "8.1",
            "title": "Operational planning and control",
            "description": "The organization shall plan, implement and control the processes needed to meet information security requirements, and to implement the actions determined in Clause 6. The organization shall also implement plans to achieve information security objectives determined in 6.2. The organization shall keep documented information to the extent necessary to have confidence that the processes have been carried out as planned. The organization shall control planned changes and review the consequences of unintended changes, taking action to mitigate any adverse effects, as necessary.",
            "category": "Clause 8: Operation",
            "priority": "high"
        },
        {
            "control_id": "8.2",
            "title": "Information security risk assessment",
            "description": "The organization shall perform information security risk assessments at planned intervals or when significant changes are proposed or occur, taking account of the criteria established in 6.1.2 a). The organization shall retain documented information of the results of the information security risk assessments.",
            "category": "Clause 8: Operation",
            "priority": "high"
        },
        {
            "control_id": "8.3",
            "title": "Information security risk treatment",
            "description": "The organization shall implement the information security risk treatment plan. The organization shall retain documented information of the results of the information security risk treatment.",
            "category": "Clause 8: Operation",
            "priority": "high"
        },
        
        # CLAUSE 9: PERFORMANCE EVALUATION
        {
            "control_id": "9.1",
            "title": "Monitoring, measurement, analysis and evaluation",
            "description": "The organization shall evaluate the information security performance and the effectiveness of the information security management system. The organization shall determine: a) what needs to be monitored and measured, including information security processes and controls; b) the methods for monitoring, measurement, analysis and evaluation, as applicable, to ensure valid results; c) when the monitoring and measuring shall be performed; d) who shall monitor and measure; e) when the results from monitoring and measurement shall be analysed and evaluated; and f) who shall analyse and evaluate these results. The organization shall retain appropriate documented information as evidence of the monitoring and measurement results.",
            "category": "Clause 9: Performance evaluation",
            "priority": "high"
        },
        {
            "control_id": "9.2.1",
            "title": "Internal audit - General",
            "description": "The organization shall conduct internal audits at planned intervals to provide information on whether the information security management system conforms to own requirements and standards.",
            "category": "Clause 9: Performance evaluation",
            "priority": "high"
        },
        {
            "control_id": "9.2.2",
            "title": "Internal audit programme",
            "description": "The organization shall plan, establish, implement and maintain an audit programme(s), including the frequency, methods, responsibilities, planning requirements and reporting.",
            "category": "Clause 9: Performance evaluation",
            "priority": "high"
        },
        {
            "control_id": "9.3.1",
            "title": "Management review - General",
            "description": "Top management shall review the organization's information security management system at planned intervals to ensure its continuing suitability, adequacy and effectiveness.",
            "category": "Clause 9: Performance evaluation",
            "priority": "high"
        },
        {
            "control_id": "9.3.2",
            "title": "Management review inputs",
            "description": "The management review shall include consideration of the status of actions from previous reviews, changes in external/internal issues, and feedback on information security performance.",
            "category": "Clause 9: Performance evaluation",
            "priority": "high"
        },
        {
            "control_id": "9.3.3",
            "title": "Management review results",
            "description": "The outputs of the management review shall include decisions related to continual improvement opportunities and any need for changes to the information security management system.",
            "category": "Clause 9: Performance evaluation",
            "priority": "high"
        },
        
        # CLAUSE 10: IMPROVEMENT
        {
            "control_id": "10.1",
            "title": "Continual improvement",
            "description": "The organization shall continually improve the suitability, adequacy and effectiveness of the information security management system.",
            "category": "Clause 10: Improvement",
            "priority": "high"
        },
        {
            "control_id": "10.2",
            "title": "Nonconformity and corrective action",
            "description": "When a nonconformity occurs, the organization shall: a) react to the nonconformity and, as applicable: 1) take action to control and correct it; and 2) deal with the consequences; b) evaluate the need for action to eliminate the causes of the nonconformity, in order that it does not recur or occur elsewhere, by: 1) reviewing the nonconformity; 2) determining the causes of the nonconformity; and 3) determining if similar nonconformities exist, or could potentially occur; c) implement any action needed; d) review the effectiveness of any corrective action taken; and e) make changes to the information security management system, if necessary. Corrective actions shall be appropriate to the effects of the nonconformities encountered. The organization shall retain documented information as evidence of: a) the nature of the nonconformities and any subsequent actions taken; and b) the results of any corrective action.",
            "category": "Clause 10: Improvement",
            "priority": "high"
        }
    ]
    
    created_count = 0
    skipped_count = 0
    
    for requirement_data in requirements_data:
        # Check if requirement already exists
        existing = db.query(Control).filter(
            Control.control_id == requirement_data["control_id"],
            Control.framework_id == framework_id
        ).first()
        
        if existing:
            skipped_count += 1
            continue
        
        requirement = Control(
            framework_id=framework_id,
            status=ControlStatus.NOT_STARTED,
            **requirement_data
        )
        db.add(requirement)
        created_count += 1
    
    db.commit()
    print(f"Created {created_count} Clause controls in Main ISO Framework.")
    print(f"Skipped {skipped_count} existing.")

def main():
    db = get_db()
    try:
        fw = get_framework(db)
        if fw:
            create_requirements(db, fw.id)
    finally:
        db.close()

if __name__ == "__main__":
    main()
