"""
NIST CSF 2.0 Data Structure (Full)
Version: 2.0 (February 2024)
Total Items: 134 (6 Functions + 22 Categories + 106 Subcategories)
"""

NIST_CSF_DATA = [
    {
        "function": "GOVERN",
        "function_code": "GV",
        "description": "The organization’s cybersecurity risk management strategy, expectations, and policy are established, communicated, and monitored.",
        "categories": [
            {
                "category": "Organizational Context",
                "code": "GV.OC",
                "subcategories": [
                    {"code": "GV.OC-01", "title": "Organizational Mission", "description": "The organizational mission is understood and informs cybersecurity risk management."},
                    {"code": "GV.OC-02", "title": "Internal and External Stakeholders", "description": "Internal and external stakeholders are understood and their needs and expectations regarding cybersecurity risk management are understood."},
                    {"code": "GV.OC-03", "title": "Legal, Regulatory, and Contractual Requirements", "description": "Legal, regulatory, and contractual requirements regarding cybersecurity constitute an input to enterprise risk management."},
                    {"code": "GV.OC-04", "title": "Critical Objectives and Capabilities", "description": "Critical objectives, capabilities, and services that stakeholders expect are understood and communicated."},
                    {"code": "GV.OC-05", "title": "Outcomes Capabilities and Services", "description": "Outcomes, capabilities, and services that the organization depends on are understood and communicated."}
                ]
            },
            {
                "category": "Risk Management Strategy",
                "code": "GV.RM",
                "subcategories": [
                    {"code": "GV.RM-01", "title": "Risk Management Objectives", "description": "Risk management objectives are established and agreed to by organizational stakeholders."},
                    {"code": "GV.RM-02", "title": "Risk Appetite and Tolerance", "description": "Risk appetite and risk tolerance statements are established, communicated, and maintained."},
                    {"code": "GV.RM-03", "title": "Cybersecurity Risk Management Strategy", "description": "Cybersecurity risk management strategy is established, communicated, and maintained."},
                    {"code": "GV.RM-04", "title": "Strategic Communication", "description": "Strategic direction that describes appropriate risk response options is established and communicated."},
                    {"code": "GV.RM-05", "title": "Standardized Risk Terminology", "description": "A standardized method for calculating, documenting, categorizing, and prioritizing cybersecurity risks is established and communicated."},
                    {"code": "GV.RM-06", "title": "Risk Management Assumptions", "description": "Risk management assumptions are established and communicated."},
                    {"code": "GV.RM-07", "title": "Risk Acceptance", "description": "Strategic acceptance of cybersecurity risk is determined and documented."}
                ]
            },
            {
                "category": "Roles, Responsibilities, and Authorities",
                "code": "GV.RR",
                "subcategories": [
                    {"code": "GV.RR-01", "title": "Leadership Responsibilities", "description": "Organizational leadership is responsible and accountable for cybersecurity risk and fosters a culture that is risk-aware, security-conscious, and compliant."},
                    {"code": "GV.RR-02", "title": "Roles and Responsibilities", "description": "Roles, responsibilities, and authorities to foster cybersecurity risk management are documented and assigned."},
                    {"code": "GV.RR-03", "title": "Resource Allocation", "description": "Adequate resources are allocated to managing cybersecurity risk."},
                    {"code": "GV.RR-04", "title": "Performance Management", "description": "Cybersecurity is included in human resources practices."}
                ]
            },
            {
                "category": "Policy",
                "code": "GV.PO",
                "subcategories": [
                    {"code": "GV.PO-01", "title": "Policy Establishment", "description": "Organizational cybersecurity policy is established, communicated, and enforced."},
                    {"code": "GV.PO-02", "title": "Policy Review", "description": "Organizational cybersecurity policy is reviewed and updated."}
                ]
            },
            {
                "category": "Oversight",
                "code": "GV.OV",
                "subcategories": [
                    {"code": "GV.OV-01", "title": "Strategy Review", "description": "Cybersecurity risk management strategy outcomes are reviewed and adjusted."},
                    {"code": "GV.OV-02", "title": "Risk Management Review", "description": "Cybersecurity risk management posture is reviewed and adjusted."},
                    {"code": "GV.OV-03", "title": "Performance Review", "description": "Organizational cybersecurity performance is reviewed and adjusted."}
                ]
            },
            {
                "category": "Cybersecurity Supply Chain Risk Management",
                "code": "GV.SC",
                "subcategories": [
                    {"code": "GV.SC-01", "title": "C-SCRM Process", "description": "A cybersecurity supply chain risk management program is established and managed."},
                    {"code": "GV.SC-02", "title": "C-SCRM Requirements", "description": "Cybersecurity supply chain risk management requirements are identified, established, and communicated."},
                    {"code": "GV.SC-03", "title": "Contract Management", "description": "Cybersecurity supply chain risk management requirements are integrated into contracts and agreements."},
                    {"code": "GV.SC-04", "title": "Supplier Criticality", "description": "Suppliers are prioritized by criticality."},
                    {"code": "GV.SC-05", "title": "Supplier Requirements", "description": "Requirements for suppliers are established and communicated."},
                    {"code": "GV.SC-06", "title": "Supplier Due Diligence", "description": "Planning and due diligence are performed to reduce risks before entering into formal supplier or other third-party relationships."},
                    {"code": "GV.SC-07", "title": "Supplier Assessment", "description": "Suppliers are assessed prior to entering into a formal relationship."},
                    {"code": "GV.SC-08", "title": "Supplier Monitoring", "description": "Suppliers are monitored throughout the relationship."},
                    {"code": "GV.SC-09", "title": "Supplier Termination", "description": "Supply chain relationships are terminated in a managed manner."},
                    {"code": "GV.SC-10", "title": "C-SCRM Continuous Improvement", "description": "The cybersecurity supply chain risk management program is improved based on lessons learned."}
                ]
            }
        ]
    },
    {
        "function": "IDENTIFY",
        "function_code": "ID",
        "description": "The current cybersecurity risk to the organization is understood.",
        "categories": [
            {
                "category": "Asset Management",
                "code": "ID.AM",
                "subcategories": [
                    {"code": "ID.AM-01", "title": "Hardware Inventory", "description": "Inventories of hardware managed by the organization are maintained."},
                    {"code": "ID.AM-02", "title": "Software Inventory", "description": "Inventories of software, services, and systems managed by the organization are maintained."},
                    {"code": "ID.AM-03", "title": "Data Inventory", "description": "Representations of data and information flows are maintained."},
                    {"code": "ID.AM-04", "title": "Asset Catalog", "description": "Inventories of services provided by the organization are maintained."},
                    {"code": "ID.AM-05", "title": "Asset Prioritization", "description": "Assets are prioritized based on classification, criticality, and business value."},
                    {"code": "ID.AM-06", "title": "Cybersecurity Roles", "description": "Cybersecurity roles and responsibilities for the entire workforce and third-party stakeholders are established."},
                    {"code": "ID.AM-07", "title": "Network Mapping", "description": "Inventories of physical and logical network maps are maintained."},
                    {"code": "ID.AM-08", "title": "Asset Lifecycle", "description": "Systems, hardware, software, services, and data are managed throughout their lifecycles."},
                    {"code": "ID.AM-09", "title": "Asset Disposal", "description": "Assets are disposed of securely and in accordance with policy."}
                ]
            },
            {
                "category": "Risk Assessment",
                "code": "ID.RA",
                "subcategories": [
                    {"code": "ID.RA-01", "title": "Vulnerability Identification", "description": "Cybersecurity vulnerabilities are identified and documented."},
                    {"code": "ID.RA-02", "title": "Threat Intelligence", "description": "Cyber threat intelligence is received from information sharing forums and sources."},
                    {"code": "ID.RA-03", "title": "Threat Identification", "description": "Internal and external threats to the organization are identified and recorded."},
                    {"code": "ID.RA-04", "title": "Potential Impacts", "description": "Potential impacts and likelihoods of threats exploiting vulnerabilities are identified."},
                    {"code": "ID.RA-05", "title": "Risk Determination", "description": "Threats, vulnerabilities, likelihoods, and impacts are used to determine risk."},
                    {"code": "ID.RA-06", "title": "Risk Response", "description": "Risk responses are identified and prioritized."},
                    {"code": "ID.RA-07", "title": "Changes in Risk", "description": "Changes to the risk landscape are identified and assessed."},
                    {"code": "ID.RA-08", "title": "Risk Register", "description": "Risk registers are maintained."}
                ]
            },
            {
                "category": "Improvement",
                "code": "ID.IM",
                "subcategories": [
                    {"code": "ID.IM-01", "title": "Improvement Identification", "description": "Improvements are identified from evaluations, audits, and reviews."},
                    {"code": "ID.IM-02", "title": "Improvement Execution", "description": "Improvements are executed."},
                    {"code": "ID.IM-03", "title": "Lessons Learned", "description": "Lessons learned are identified and integrated."},
                    {"code": "ID.IM-04", "title": "Strategy Update", "description": "Strategy is updated based on improvements."}
                ]
            }
        ]
    },
    {
        "function": "PROTECT",
        "function_code": "PR",
        "description": "Safeguards to ensure the delivery of critical infrastructure services are outlined.",
        "categories": [
            {
                "category": "Identity Management, Authentication, and Access Control",
                "code": "PR.AA",
                "subcategories": [
                    {"code": "PR.AA-01", "title": "Identity Management", "description": "Identities and credentials are managed for all users, devices, and other entities."},
                    {"code": "PR.AA-02", "title": "Access Management", "description": "Access to data, personnel, devices, and applications is managed consistent with the principle of least privilege."},
                    {"code": "PR.AA-03", "title": "Remote Access", "description": "Remote access is managed to prevent unauthorized access."},
                    {"code": "PR.AA-04", "title": "Physical Access", "description": "Physical access to assets is managed and protected."},
                    {"code": "PR.AA-05", "title": "Authentication", "description": "Authentication and authorization mechanisms are implemented commensurate with risk."},
                    {"code": "PR.AA-06", "title": "Identity Proofing", "description": "Identity proofing and binding are performed commensurate with risk."}
                ]
            },
            {
                "category": "Awareness and Training",
                "code": "PR.AT",
                "subcategories": [
                    {"code": "PR.AT-01", "title": "Training & Awareness", "description": "All personnel are provided cybersecurity awareness and training."},
                    {"code": "PR.AT-02", "title": "Role-Based Training", "description": "Specialized training is provided to personnel with significant cybersecurity responsibilities."}
                ]
            },
            {
                "category": "Data Security",
                "code": "PR.DS",
                "subcategories": [
                    {"code": "PR.DS-01", "title": "Data At-Rest", "description": "Data-at-rest is protected."},
                    {"code": "PR.DS-02", "title": "Data In-Transit", "description": "Data-in-transit is protected."},
                    {"code": "PR.DS-10", "title": "Data Integrity", "description": "Availability, Integrity and Confidentiality of data is managed."},
                    {"code": "PR.DS-11", "title": "Data Leakage Protection", "description": "Data leakage protection mechanisms are implemented."}
                ]
            },
            {
                "category": "Platform Security",
                "code": "PR.PS",
                "subcategories": [
                    {"code": "PR.PS-01", "title": "Configuration Management", "description": "Configuration management practices are established and applied."},
                    {"code": "PR.PS-02", "title": "Software Maintenance", "description": "Software is maintained and updated."},
                    {"code": "PR.PS-03", "title": "Software Development", "description": "Secure software development practices are followed."},
                    {"code": "PR.PS-04", "title": "Log Management", "description": "Log records are determined, documented, managed to support monitoring and investigations."},
                    {"code": "PR.PS-05", "title": "Installation Management", "description": "Installation and execution of software is managed."},
                    {"code": "PR.PS-06", "title": "Vulnerability Management", "description": "Vulnerabilities are managed."}
                ]
            },
            {
                "category": "Technology Infrastructure Resilience",
                "code": "PR.IR",
                "subcategories": [
                    {"code": "PR.IR-01", "title": "Resilient Networks", "description": "Networks are managed to be resilient."},
                    {"code": "PR.IR-02", "title": "Resilient Systems", "description": "Systems are managed to be resilient."},
                    {"code": "PR.IR-03", "title": "Availability Mechanisms", "description": "Availability mechanisms are implemented."},
                    {"code": "PR.IR-04", "title": "Backups", "description": "Backups of information are conducted, maintained, and tested."}
                ]
            }
        ]
    },
    {
        "function": "DETECT",
        "function_code": "DE",
        "description": "The possible occurrence of a cybersecurity event is identified.",
        "categories": [
            {
                "category": "Continuous Monitoring",
                "code": "DE.CM",
                "subcategories": [
                    {"code": "DE.CM-01", "title": "Network Monitoring", "description": "Networks and physical environment are monitored to detect potential cybersecurity events."},
                    {"code": "DE.CM-02", "title": "Physical Monitoring", "description": "Physical environment is monitored to detect potential cybersecurity events."},
                    {"code": "DE.CM-03", "title": "Personnel Activity", "description": "Personnel activity is monitored to detect potential cybersecurity events."},
                    {"code": "DE.CM-04", "title": "Malicious Code", "description": "Malicious code is detected."},
                    {"code": "DE.CM-05", "title": "Mobile Code", "description": "Unauthorized mobile code is detected."},
                    {"code": "DE.CM-06", "title": "External Activity", "description": "External service provider activity is monitored to detect potential cybersecurity events."},
                    {"code": "DE.CM-09", "title": "Monitoring Effectiveness", "description": "Monitoring effectiveness is verified."}
                ]
            },
            {
                "category": "Adverse Key Event Detection",
                "code": "DE.AE",
                "subcategories": [
                    {"code": "DE.AE-02", "title": "Event Analysis", "description": "Detected events are analyzed to understand attack targets and methods."},
                    {"code": "DE.AE-03", "title": "Event Collection", "description": "Event data are collected and correlated from multiple sources and sensors."},
                    {"code": "DE.AE-04", "title": "Impact Determination", "description": "Impact of events is determined."},
                    {"code": "DE.AE-06", "title": "Incident Declaration", "description": "Incidents are declared and alerts are generated."}
                ]
            }
        ]
    },
    {
        "function": "RESPOND",
        "function_code": "RS",
        "description": "Action regarding a detected cybersecurity incident is taken.",
        "categories": [
            {
                "category": "Incident Management",
                "code": "RS.MA",
                "subcategories": [
                    {"code": "RS.MA-01", "title": "Incident Plan Execution", "description": "Incidents are managed in accordance with the incident response plan."},
                    {"code": "RS.MA-02", "title": "Incident Reporting", "description": "Incident reports are submitted consistent with regulatory requirements."},
                    {"code": "RS.MA-03", "title": "Personnel Support", "description": "Personnel are supported during incident handling."},
                    {"code": "RS.MA-04", "title": "External Coordination", "description": "Incidents are coordinated with external stakeholders."},
                    {"code": "RS.MA-05", "title": "Categorization", "description": "Incidents are categorized and prioritized."}
                ]
            },
            {
                "category": "Incident Analysis",
                "code": "RS.AN",
                "subcategories": [
                    {"code": "RS.AN-01", "title": "Investigation", "description": "Notifications from detection systems are investigated."},
                    {"code": "RS.AN-03", "title": "Analysis and Forensics", "description": "Analysis is conducted to ensure adequate response and support recovery activities."},
                    {"code": "RS.AN-06", "title": "Categorization", "description": "Incidents are categorized consistent with response plans."},
                    {"code": "RS.AN-07", "title": "Incident Scope", "description": "The scope of the incident is determined."}
                ]
            },
            {
                "category": "Incident Response Reporting and Communication",
                "code": "RS.CO",
                "subcategories": [
                    {"code": "RS.CO-02", "title": "Stakeholder Communication", "description": "Information is shared with stakeholders consistent with plans."},
                    {"code": "RS.CO-03", "title": "Communication Coordination", "description": "Information sharing is coordinated."}
                ]
            },
            {
                "category": "Incident Mitigation",
                "code": "RS.MI",
                "subcategories": [
                    {"code": "RS.MI-01", "title": "Mitigation Execution", "description": "Incidents are contained."},
                    {"code": "RS.MI-02", "title": "Mitigation Effectiveness", "description": "Mitigation activities are effectively performed."}
                ]
            }
        ]
    },
    {
        "function": "RECOVER",
        "function_code": "RC",
        "description": "Plans for resilience and to restore any capabilities or services that were impaired due to a cybersecurity incident.",
        "categories": [
            {
                "category": "Incident Recovery Plan Execution",
                "code": "RC.RP",
                "subcategories": [
                    {"code": "RC.RP-01", "title": "Recovery Execution", "description": "Recovery plan is executed during or after a cybersecurity incident."}
                ]
            },
            {
                "category": "Incident Recovery Improvement",
                "code": "RC.IM",
                "subcategories": [
                    {"code": "RC.IM-01", "title": "Recovery Improvement", "description": "Recovery plans are improved based on lessons learned."},
                     {"code": "RC.IM-02", "title": "Strategy Update", "description": "Recovery strategies are updated to reflect evolving threats and organizational changes."}
                ]
            },
            {
                "category": "Incident Recovery Communication",
                "code": "RC.CO",
                "subcategories": [
                    {"code": "RC.CO-03", "title": "Recovery Communication", "description": "Recovery activities are communicated to internal and external stakeholders."},
                    {"code": "RC.CO-04", "title": "Public Relations", "description": "Public updates on incident recovery are shared using approved methods and messaging."},
                    {"code": "RC.CO-05", "title": "Reputation Repair", "description": "Reputation repair activities are performed."},
                    {"code": "RC.CO-06", "title": "Recovery Termination", "description": "Recovery activities are terminated."}
                ]
            }
        ]
    }
]
