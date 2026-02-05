import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import axios from 'axios';
import {
    Zap, Activity, FileText,
    X, Shield, AlertCircle, Upload, ChevronUp, ChevronDown, ChevronRight
} from 'lucide-react';
import FrameworkDetailHipaa from './FrameworkDetail_HIPAA';
import { AIService } from '../services/aiService';
import ControlsToolbar from './ControlsToolbar';
import useFilters from '../hooks/useFilters';

// ... (existing code)

// For local development, use localhost. For prod, use Render.
// Ideally usage: const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';
import config from '../config';

const API_URL = config.API_BASE_URL;

// COSO DESCRIPTIONS MAP
const COSO_DESCRIPTIONS = {
    // CC1: Control Environment (COSO 1-5)
    "CC1.1": "COSO Principle 1: The entity demonstrates a commitment to integrity and ethical values.",
    "CC1.2": "COSO Principle 2: The board of directors exercises oversight of the development and performance of internal control.",
    "CC1.3": "COSO Principle 3: Management establishes structures, reporting lines, and appropriate authorities.",
    "CC1.4": "COSO Principle 4: The entity demonstrates a commitment to attract, develop, and retain competent individuals.",
    "CC1.5": "COSO Principle 5: The entity holds individuals accountable for their internal control responsibilities.",

    // CC2: Communication & Information (COSO 13-15)
    "CC2.1": "COSO Principle 13: The entity obtains or generates and uses relevant, quality information.",
    "CC2.2": "COSO Principle 14: The entity internally communicates information.",
    "CC2.3": "COSO Principle 15: The entity communicates with external parties.",

    // CC3: Risk Assessment (COSO 6-9)
    "CC3.1": "COSO Principle 6: The entity specifies objectives with sufficient clarity.",
    "CC3.2": "COSO Principle 7: The entity identifies risks to the achievement of its objectives.",
    "CC3.3": "COSO Principle 8: The entity considers the potential for fraud in assessing risks.",
    "CC3.4": "COSO Principle 9: The entity identifies and assesses changes that could significantly impact the system.",

    // CC4: Monitoring Activities (COSO 16-17)
    "CC4.1": "COSO Principle 16: The entity selects, develops, and performs ongoing and/or separate evaluations.",
    "CC4.2": "COSO Principle 17: The entity evaluates and communicates internal control deficiencies.",

    // CC5: Control Activities (COSO 10-12)
    "CC5.1": "COSO Principle 10: The entity selects and develops control activities.",
    "CC5.2": "COSO Principle 11: The entity selects and develops general control activities over technology.",
    "CC5.3": "COSO Principle 12: The entity deploys control activities through policies and procedures.",

    // CC6-9: SOC 2 Specifics
    "CC6.1": "Logical Access: The entity implements logical access security software, infrastructure, and architectures.",
    "CC6.2": "Logical Access: Prior to issuing credentials, the entity identifies and authenticates users.",
    "CC6.3": "Logical Access: The entity authorizes access to protected information assets.",
    "CC6.6": "Logical Access: The entity restricts physical access.",
    "CC7.1": "System Operations: The entity identifies and manages system vulnerabilities.",
    "CC8.1": "Change Management: The entity authorizes, designs, develops, tests, and implements changes.",

    // Generic Categories
    "Availability": "Availability: The entity limits availability of information and systems to authorized people.",
    "Confidentiality": "Confidentiality: The entity protects confidential information.",
    "Security": "Security: The entity protects against unauthorized access.",

    // Additional Criteria
    "A1.1": "Availability: The entity maintains, monitors, and evaluates current processing capacity.",
    "A1.2": "Availability: Data backup and recovery.",
    "C1.1": "Confidentiality: The entity identifies and maintains confidential information.",
    "P1.0": "Privacy: Notice and choice.",
    "P2.0": "Privacy: Collection, use, retention, and disposal.",

    // ISO 27001 PROCESS GROUPS (Custom Restructure)
    "Governance & Policy": "Clauses 4-7 & Annex A.5: Leadership, Policies, and Organizational Context",
    "HR Security": "Clauses 7 & Annex A.6: Human Resource Security (Screening to Termination)",
    "Asset Management": "Annex A.5, A.7, A.8: Inventory, Responsibility, and Media Handling",
    "Access Control (IAM)": "Annex A.5 & A.8: Logical Access, User Rights, and Authentication",
    "Physical Security": "Annex A.7: Secure Areas, Equipment, and Physical Entry",
    "Operations (General)": "Annex A.8: Malware, Backup, Logging, and Data Protection",
    "Configuration Management": "Annex A.8.9: Secure Configurations",
    "Cryptography": "Annex A.8.24: Encryption and Key Management",
    "Logging & Monitoring": "Annex A.8.15-16: Event Logging and System Monitoring",
    "Clock Synchronization": "Annex A.8.17: Time Synchronization (NTP)",
    "Vulnerability Management": "Annex A.8.8: Technical Vulnerabilities",
    "Capacity Management": "Annex A.8.6: Resource Management",
    "Backup Management": "Annex A.8.13: Information Backup",
    "Network Security": "Annex A.5 & A.8: Network Services, Segregation, and Transfer",
    "SDLC (Development)": "Annex A.8: Secure Development, Testing, and Change Management",
    "Supplier Mgmt": "Annex A.5: Supplier Relationships and Service Monitoring",
    "Incident & Resilience": "Clause 7.4 & Annex A.5: Incident Management and Business Continuity",
    "Threat Intel": "Annex A.5.7: Threat Intelligence",
    "Legal & Compliance": "Annex A.5 & A.8: Legal Requirements, Privacy, and IPR",
    "Risk Management": "Clauses 6 & 8: Risk Assessment and Treatment",
    "Performance Evaluation": "Clauses 9 & Annex A.5: Audit, Review, and Monitoring",
    "Improvement": "Clause 10: Corrective Action and Continual Improvement",

    // NEW STANDARD ISO MAPPINGS
    "Clause 4: Context of the organization": "Clause 4: External/Internal Issues, Interested Parties, Scope, and SMS",
    "Clause 5: Leadership": "Clause 5: Leadership, Policy, and Roles",
    "Clause 6: Planning": "Clause 6: Risk Assessment, Treatment, and Objectives",
    "Clause 7: Support": "Clause 7: Resources, Competence, Awareness, and Documented Information",
    "Clause 8: Operation": "Clause 8: Operational Planning and Risk Control",
    "Clause 9: Performance evaluation": "Clause 9: Monitoring, Measurement, Audit, and Management Review",
    "Clause 10: Improvement": "Clause 10: Nonconformity and Continual Improvement",
    "Organizational controls": "Annex A.5: Information Security Policies, Organization, and Human Resources",
    "People controls": "Annex A.6: People Security",
    "Physical controls": "Annex A.7: Physical Security",
    "Technological controls": "Annex A.8: Technological Security",

    "DEFAULT": "Standard requirement for this criteria."
};

// GRANULAR EVIDENCE MAPPING (Keyed by Control Title Partial Match or Exact ID)
// This overrides the generic category map for specific controls.
const SPECIFIC_EVIDENCE_MAP = {
    "Background checks performed for new hires": [
        { name: "Background Check Policy", type: "Policy" },
        { name: "Sample Background Check Reports (Anonymized)", type: "Evidence" },
        { name: "New Hire Checklist (showing check completion)", type: "Log" }
    ],
    "Code of Conduct acknowledged by contractors": [
        { name: "Code of Conduct Policy", type: "Policy" },
        { name: "Contractor Acknowledgement Log", type: "Log" },
        { name: "Sample Signed Contractor Agreements", type: "Contract" }
    ],
    // --- NEW: EXPLICITLY REQUESTED ---
    "Confidentiality Agreement acknowledged by contractors": [
        { name: "NDA Template (Contractor)", type: "Policy" },
        { name: "Contractor NDA Registry", type: "Log" },
        { name: "Sample Signed NDAs (Contractors)", type: "Evidence" }
    ],
    "Supplier Code of Conduct Review": [
        { name: "Supplier Code of Conduct", type: "Policy" },
        { name: "Vendor Acknowledgement Log", type: "Log" }
    ],
    "Board meeting minutes review (Quarterly)": [
        { name: "Board Meeting Minutes (Q1)", type: "Minutes" },
        { name: "Board Meeting Minutes (Q2)", type: "Minutes" },
        { name: "Board Meeting Minutes (Q3)", type: "Minutes" },
        { name: "Board Meeting Minutes (Q4)", type: "Minutes" }
    ],
    "independent Director Review of Internal Findings": [
        { name: "Board Independence Statement", type: "Policy" },
        { name: "Internal Audit Review Minutes", type: "Report" }
    ],
    "Whistleblower Policy (Review & Communication)": [
        { name: "Whistleblower Policy", type: "Policy" },
        { name: "Evidence of Communication (Email/Intranet)", type: "Evidence" }
    ],
    "Whistleblower Hotline Availability Test": [
        { name: "Hotline Test Log", type: "Log" },
        { name: "Anonymous Reporting Mechanism Screenshot", type: "Evidence" }
    ],
    "Performance Reviews (Biannual)": [
        { name: "Performance Review Schedule", type: "Policy" },
        { name: "Sample Completed Review Forms (Anonymized)", type: "HR Doc" }
    ],
    "Security Awareness Training (Onboarding)": [
        { name: "Security Training Slides/Material", type: "Document" },
        { name: "New Hire Training Completion Log", type: "Log" }
    ],
    "Quarterly User Access Review": [
        { name: "User Access Review Policy", type: "Policy" },
        { name: "Completed Access Review (Q1-Q4)", type: "Review" },
        { name: "Evidence of Revocation (if applicable)", type: "Ticket" }
    ],
    "Quarterly security compliance report to Board": [
        { name: "Security Presentation Deck (Q1)", type: "Report" },
        { name: "Security Presentation Deck (Q3)", type: "Report" }
    ],
    "Charter of the Audit Committee": [
        { name: "Audit Committee Charter Document", type: "Policy" },
        { name: "Committee Member List", type: "List" }
    ],
    "Organizational Chart is current": [
        { name: "Current Organizational Chart", type: "Diagram" },
        { name: "HR System Export", type: "List" }
    ],
    "Job Descriptions include security responsibilities": [
        { name: "Sample Job Descriptions (Engineering)", type: "HR Doc" },
        { name: "Sample Job Descriptions (Admin)", type: "HR Doc" }
    ],
    "Segregation of Duties Matrix": [
        { name: "Segregation of Duties (SoD) Matrix", type: "Sheet" },
        { name: "Access Rights Review Log", type: "Log" }
    ],
    // --- NEW MAPPINGS FOR FULL EXPANSION ---
    "Daily Database Backups": [
        { name: "Backup Policy", type: "Policy" },
        { name: "Sample Restore Test Report", type: "Evidence" },
        { name: "Backup Automated Logs (30 days)", type: "Log" }
    ],
    "Business Continuity Plan": [
        { name: "Business Continuity Plan (BCP)", type: "Document" },
        { name: "Disaster Recovery Test Results", type: "Report" }
    ],
    "Production Change Logs": [
        { name: "Change Management Policy", type: "Policy" },
        { name: "List of Production Changes (Q1-Q4)", type: "Sheet" },
        { name: "Sample Change Ticket with Approval", type: "Evidence" }
    ],
    "Patch Management Policy": [
        { name: "Patch Management Policy", type: "Policy" },
        { name: "Vulnerability Scan Report (Patched)", type: "Report" }
    ],
    "Privacy Policy Updated": [
        { name: "Privacy Policy (Public URL)", type: "Link" },
        { name: "Annual Privacy Policy Review", type: "Log" }
    ],
    "Subject Access Request (SAR) Log": [
        { name: "SAR Process/Procedure", type: "Policy" },
        { name: "Anonymized SAR Request Log", type: "Log" }
    ],

    // --- SOC 2 SPECIFIC MAPPINGS (USER REQUESTED) ---
    "CC1.1": [
        { name: "Code of Conduct", type: "Policy", desc: "Signed by all employees." },
        { name: "Employee Handbook (Signed)", type: "HR Doc", desc: "Acknowledgement page." },
        { name: "Whistleblower Policy", type: "Policy", desc: "Mechanism for anonymous reporting." }
    ],
    "CC1.2": [
        { name: "Board Meeting Minutes", type: "Minutes", desc: "Quarterly minutes showing oversight." },
        { name: "Organizational Chart", type: "Diagram", desc: "Current year org structure." }
    ],
    "A1.1": [
        { name: "Cloud Monitoring Dashboard Export", type: "Report", desc: "CPU/RAM utilization trends." },
        { name: "Uptime SLA Reports", type: "Report", desc: "Monthly uptime % against 99.9% target." }
    ],
    "The entity authorizes, designs, develops, tests, and implements changes.": [ // CC8.1 (Mapping to A1.2 context roughly or explicit A criteria if titles match)
        // Note: User asked for A1.2 Disaster Recovery separately.
    ],
    // A1.2 Title from Seed: "The entity authorizes, designs, develops or acquires, implements, operates, approves, maintains, and monitors environmental protections." (Wait, standard A1.2 is environmental? No, TSC 2017 A1.2 is Environmental. User prompt said A1.2 = Disaster Recovery which is usually A1.3 or CC9. Let's map based on the USER'S specific titles from their prompt or the seed data titles.)

    // Let's rely on the IDs or Titles from the Seed Data I generated. 
    // Seed Data A1.2 Title: "Environmental Protections"
    // Seed Data A1.3 Title: "Backups and Recovery"

    // User Request said: "A1.2 (Disaster Recovery): Link to BCP/DR Plan" -> User might have a slight mismatch with AICPA 2017 standard text vs their mental model, OR they want me to map to the controls that *deal* with this.
    // I will map to the Titles present in `seed_soc2_unified.py` that match the INTENT.

    "A1.2": [ // Environmental & BCP
        { name: "BCP/DR Plan", type: "Document", desc: "Business Continuity & Strategy" },
        { name: "Physical Security Policy", type: "Policy" },
        { name: "Data Center SOC 2 Report", type: "Report", desc: "AWS/Azure Compliance Report" }
    ],
    "A1.3": [ // Backups and Recovery
        { name: "BCP/DR Plan", type: "Document", desc: "Business Continuity & Disaster Recovery Strategy" },
        { name: "Backup Configuration Screenshots", type: "Evidence", desc: "Retention settings & frequency" },
        { name: "Off-site Storage Proof", type: "Evidence", desc: "Replication config (e.g. S3 Cross-Region)" },
        { name: "Annual DR Test Report", type: "Report", desc: "Summary of last failover test" },
        { name: "Backup Restoration Test Logs", type: "Log", desc: "Success logs of sample restores" }
    ]
};

// FALLBACK CATEGORY MAP
const REQUIRED_EVIDENCE_DEFAULTS = {
    "CC1.1": [{ name: "Ethics Policy", type: "Policy" }],
    "CC6.1": [{ name: "Access Logs", type: "Log" }],
    "DEFAULT": [{ name: "Standard Policy Document", type: "Policy" }, { name: "Evidence of Execution", type: "Evidence" }]
};

const FrameworkDetail = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();

    // TOOLBAR STATE
    const { filters, updateFilter, applyFilters } = useFilters({
        search: searchParams.get('search') || '',
        status: searchParams.get('status') || 'All'
    });
    const [grouping, setGrouping] = useState({ groupBy: 'section', sort: 'default' });

    const [framework, setFramework] = useState(null);
    const [processes, setProcesses] = useState([]);
    const [socControls, setSocControls] = useState({}); // This effectively becomes 'groupedControls'
    const [rawControls, setRawControls] = useState([]); // NEW: Store raw fetched controls
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [stats, setStats] = useState({ total: 0, implemented: 0, percentage: 0 });
    // const [searchTerm, setSearchTerm] = useState(''); // REPLACED BY useFilters

    // DRAWER STATE
    const [selectedControl, setSelectedControl] = useState(null);
    const [evidenceList, setEvidenceList] = useState(null);
    const [expandedControlId, setExpandedControlId] = useState(null);
    const [expandedReq, setExpandedReq] = useState(null);

    // AI State
    const [aiRequirements, setAiRequirements] = useState(null);
    const [aiExplanation, setAiExplanation] = useState("");
    const [loadingAi, setLoadingAi] = useState(false);
    const [aiError, setAiError] = useState(false);
    const [generatedPolicy, setGeneratedPolicy] = useState("");
    const [isGenerating, setIsGenerating] = useState(false);

    // FILTER STATE
    // const [statusFilter, setStatusFilter] = useState('All'); // REPLACED BY useFilters

    // JUMP TO SECTION HANDLER REMOVED (Moved to ControlsToolbar)

    // GAP ANALYSIS STATE
    const [gapAnalysis, setGapAnalysis] = useState(null);
    const [analyzingGap, setAnalyzingGap] = useState(false);



    const handleGapAnalysis = async () => {
        if (!selectedControl) return;
        setAnalyzingGap(true);
        try {
            // Use AI requirements if available, else defaults
            const reqs = aiRequirements || getRequirements(selectedControl);

            const result = await AIService.evaluateGapAnalysis(
                selectedControl.title,
                reqs,
                evidenceList || []
            );
            setGapAnalysis(result);
        } catch (e) {
            console.error(e);
        } finally {
            setAnalyzingGap(false);
        }
    };

    const handleGenerateArtifact = async (requirement) => {
        setIsGenerating(true);
        // Reuse generatedPolicy state for now to show in the "AI Policy Drafter" box
        // Ideally we should have a modal, but let's reuse the existing UI box for speed.
        try {
            const draft = await AIService.generateArtifact(
                selectedControl.title,
                requirement.name,
                requirement.desc
            );
            setGeneratedPolicy(draft); // Reuse this state to display result in drawer
            // Scroll to top of drawer
            const drawer = document.querySelector('.animate-slide-in-right');
            if (drawer) drawer.scrollTop = 0;
        } catch (e) {
            console.error(e);
            alert("Failed to generate artifact.");
        } finally {
            setIsGenerating(false);
        }
    };

    useEffect(() => {
        fetchData();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [id]);

    // EFFECT: Handle Filtering & Grouping when rawControls or settings change
    // EFFECT: Handle Filtering & Grouping when rawControls or settings change
    useEffect(() => {
        if (!framework || !rawControls.length) return;

        const isSOC2 = framework?.code?.includes("SOC2");
        const isISO = framework?.code?.includes("ISO27001");
        const isNIST = framework?.code?.includes("NIST");
        const useGroupedView = isSOC2 || isISO || isNIST;

        if (useGroupedView) {
            // 1. FILTER
            const filtered = applyFilters(rawControls);

            // 2. GROUP
            const grouped = {};
            filtered.forEach(c => {
                let key;
                if (grouping.groupBy === 'framework') {
                    if (isISO) {
                        // ISO 27001 Theme Mappings (2022)
                        const ISO_THEMES = {
                            "A.5": "Organizational",
                            "A.6": "People",
                            "A.7": "Physical",
                            "A.8": "Technological"
                        };
                        const themeKey = Object.keys(ISO_THEMES).find(k => c.control_id && c.control_id.startsWith(k));
                        key = themeKey ? ISO_THEMES[themeKey] : "General";
                    } else if (isSOC2) {
                        // SOC 2 COSO MAPPING
                        const id = c.control_id || "";
                        if (id.startsWith("CC1")) key = "CC1: Control Environment (COSO)";
                        else if (id.startsWith("CC2")) key = "CC2: Communication & Info (COSO)";
                        else if (id.startsWith("CC3")) key = "CC3: Risk Assessment (COSO)";
                        else if (id.startsWith("CC4")) key = "CC4: Monitoring Activities (COSO)";
                        else if (id.startsWith("CC5")) key = "CC5: Control Activities (COSO)";
                        else if (id.startsWith("CC6")) key = "CC6: Logical & Physical Access";
                        else if (id.startsWith("CC7")) key = "CC7: System Operations";
                        else if (id.startsWith("CC8")) key = "CC8: Change Management";
                        else if (id.startsWith("CC9")) key = "CC9: Risk Mitigation";
                        else if (id.startsWith("A")) key = "Availability Criteria";
                        else if (id.startsWith("C")) key = "Confidentiality Criteria";
                        else if (id.startsWith("PI")) key = "Processing Integrity Criteria";
                        else if (id.startsWith("P")) key = "Privacy Criteria";
                        else key = c.category || "Uncategorized";
                    } else if (isNIST) {
                        // NIST CSF 2.0 MAPPING
                        const id = c.control_id || "";
                        if (id.startsWith("GV")) key = "GOVERN";
                        else if (id.startsWith("ID")) key = "IDENTIFY";
                        else if (id.startsWith("PR")) key = "PROTECT";
                        else if (id.startsWith("DE")) key = "DETECT";
                        else if (id.startsWith("RS")) key = "RESPOND";
                        else if (id.startsWith("RC")) key = "RECOVER";
                        else key = "Other";
                    } else {
                        key = c.category || "General";
                    }
                } else {
                    // Default SECTION Grouping (Technical Domains or Process)
                    if (isSOC2) {
                        // FORCE COSO MAPPING FOR SOC 2 DEFAULT VIEW ALSO
                        const id = c.control_id || "";
                        if (id.startsWith("CC1")) key = "CC1: Control Environment (COSO)";
                        else if (id.startsWith("CC2")) key = "CC2: Communication & Info (COSO)";
                        else if (id.startsWith("CC3")) key = "CC3: Risk Assessment (COSO)";
                        else if (id.startsWith("CC4")) key = "CC4: Monitoring Activities (COSO)";
                        else if (id.startsWith("CC5")) key = "CC5: Control Activities (COSO)";
                        else if (id.startsWith("CC6")) key = "CC6: Logical & Physical Access";
                        else if (id.startsWith("CC7")) key = "CC7: System Operations";
                        else if (id.startsWith("CC8")) key = "CC8: Change Management";
                        else if (id.startsWith("CC9")) key = "CC9: Risk Mitigation";
                        else if (id.startsWith("A")) key = "Availability Criteria";
                        else if (id.startsWith("C")) key = "Confidentiality Criteria";
                        else if (id.startsWith("PI")) key = "Processing Integrity Criteria";
                        else if (id.startsWith("P")) key = "Privacy Criteria";
                        else key = c.category || "Uncategorized";
                    } else if (isNIST) {
                        // FORCE NIST GROUPING
                        const id = c.control_id || "";
                        if (id.startsWith("GV")) key = "GOVERN";
                        else if (id.startsWith("ID")) key = "IDENTIFY";
                        else if (id.startsWith("PR")) key = "PROTECT";
                        else if (id.startsWith("DE")) key = "DETECT";
                        else if (id.startsWith("RS")) key = "RESPOND";
                        else if (id.startsWith("RC")) key = "RECOVER";
                        else key = "Other";
                    } else {
                        key = c.process;
                        if (!key) {
                            // Fallback to Category
                            const parts = (c.category || "").split('|');
                            key = parts[0] || "Uncategorized";
                        }
                    }
                }
                if (!grouped[key]) grouped[key] = [];
                grouped[key].push(c);
            });
            setSocControls(grouped);
        }
    }, [rawControls, filters, grouping, framework, applyFilters]);


    // FETCH EVIDENCE & RESET AI WHEN CONTROL IS SELECTED
    useEffect(() => {
        if (selectedControl) {
            fetchEvidence(selectedControl.id);
            setGeneratedPolicy(null); // Reset AI draft
        } else {
            setEvidenceList([]);
            setGeneratedPolicy(null);
        }
    }, [selectedControl]);

    // FETCH AI SUGGESTIONS WHEN CONTROL OPENS
    useEffect(() => {
        if (selectedControl) {
            setAiRequirements(null);
            setAiError(false);
            fetchAiRequirements(selectedControl);
        }
    }, [selectedControl]);

    const fetchAiRequirements = async (control) => {
        setLoadingAi(true);
        setAiError(false);
        try {
            const data = await AIService.analyzeControlRequirements(control.title, control.description, control.category, control.id);
            console.log("AI Data:", data);
            if (data && data.requirements) {
                setAiRequirements(data.requirements);
                setAiExplanation(data.explanation || "");
            }
        } catch (err) {
            console.error(err);
            setAiError(true);
        } finally {
            setLoadingAi(false);
        }
    };

    const handleGeneratePolicy = async () => {
        setIsGenerating(true);
        try {
            const policy = await AIService.generatePolicy(selectedControl.title, selectedControl.description);
            setGeneratedPolicy(policy);
        } catch (err) {
            alert(err.message);
        } finally {
            setIsGenerating(false);
        }
    };

    const fetchEvidence = async (controlId) => {
        try {
            const token = localStorage.getItem('token');
            const res = await axios.get(`${API_URL}/evidence/control/${controlId}`, { headers: { Authorization: `Bearer ${token}` } });
            setEvidenceList(res.data);
        } catch (e) {
            console.error("Failed to load evidence", e);
        }
    };

    const handleReviewDocument = async (evidence) => {
        try {
            alert(`Reviewing ${evidence.filename}... This may take a few seconds.`);
            const result = await AIService.reviewDocument(selectedControl.id, evidence.id);
            console.log("Review Result:", result);
            alert(`AI Verdict: ${result.status} \n\nReasoning: ${result.reasoning} `);
            fetchEvidence(selectedControl.id);
        } catch (error) {
            alert("Review Failed: " + error.message);
        }
    };

    const handleFileUpload = async (e, controlId) => {
        const file = e.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append("file", file);
        formData.append("control_id", controlId);
        formData.append("title", file.name);
        formData.append("description", "Uploaded via Dashboard");

        try {
            const token = localStorage.getItem('token');
            await axios.post(`${API_URL}/evidence/upload`, formData, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'multipart/form-data'
                }
            });
            alert("File uploaded successfully!");
            // Refresh main data AND specific control evidence
            fetchData();
            fetchEvidence(controlId);
        } catch (error) {
            console.error("Upload failed", error);
            alert("Upload failed. Please try again.");
        }
    };

    const fetchData = async () => {
        try {
            const token = localStorage.getItem('token');
            const headers = { Authorization: `Bearer ${token}` };

            const [fwRes, settingsRes] = await Promise.all([
                axios.get(`${API_URL}/frameworks/${id}`, { headers }),
                axios.get(`${API_URL}/settings/scope`, { headers }).catch(() => ({ data: {} })) // Fail soft if settings missing
            ]);

            const fwData = fwRes.data;
            const scopeSettings = settingsRes.data?.content || {};

            const isSOC2 = fwData.code && fwData.code.includes("SOC2");
            const isISO = fwData.code && fwData.code.includes("ISO27001");
            const useGroupedView = isSOC2 || isISO;

            const ctrlRes = await axios.get(`${API_URL}/controls/?limit=10000`, { headers });

            // Filter by Framework AND check for SoA Applicability
            let allControls = ctrlRes.data
                .filter(c => c.framework_id === parseInt(id))
                .filter(c => c.is_applicable !== false);

            // SOC 2 DYNAMIC SCOPING FILTER
            if (isSOC2 && scopeSettings.soc2_selected_principles) {
                const selected = scopeSettings.soc2_selected_principles; // e.g. ["Security", "Availability"]
                if (selected && selected.length > 0) {
                    // Security is mandatory, but should be in the list coming from settings.
                    // Filter controls where category is in the selected list.
                    // Ensure we normalize case if needed, but Wizard saves exact strings "Security", "Availability" etc.
                    allControls = allControls.filter(c => selected.includes(c.category));
                }
            }

            setRawControls(allControls); // Store raw for local filtering

            if (!useGroupedView) {
                // If not SOC2/ISO, we use the process API mainly?
                // Actually the original code had a fork. For now let's keep the existing logic for non-grouped.
                const procRes = await axios.get(`${API_URL}/processes/`, { headers });
                const filteredProcesses = procRes.data.map(proc => {
                    const relevantSubs = proc.sub_processes.map(sub => {
                        return { ...sub, controls: sub.controls || [] };
                    }).filter(sub => sub.controls && sub.controls.length > 0);
                    return { ...proc, sub_processes: relevantSubs };
                }).filter(proc => proc.sub_processes.length > 0);
                setProcesses(filteredProcesses);
            }

            // STATS are calculated on ALL Applicable controls (Post-Scope Filtering)
            const total = allControls.length;
            const implemented = allControls.filter(c => c.status === 'IMPLEMENTED').length;
            setFramework(fwData);

            // Advanced Stats Calculation
            const techControls = allControls.filter(c =>
                (c.category && (c.category === "Technical" || c.category.includes("Technological") || c.category.startsWith("A.8") || c.category.startsWith("CC7"))) ||
                (c.classification === "Technical")
            );
            const docControls = allControls.filter(c => !techControls.find(tc => tc.id === c.id));

            setStats({
                total,
                implemented,
                percentage: total > 0 ? Math.round((implemented / total) * 100) : 0,
                // Advanced Breakdown
                tests: {
                    total: techControls.length,
                    passing: techControls.filter(c => c.status === 'IMPLEMENTED').length,
                    percentage: techControls.length > 0 ? Math.round((techControls.filter(c => c.status === 'IMPLEMENTED').length / techControls.length) * 100) : 0
                },
                documents: {
                    total: docControls.length,
                    ready: docControls.filter(c => c.status === 'IMPLEMENTED').length,
                    percentage: docControls.length > 0 ? Math.round((docControls.filter(c => c.status === 'IMPLEMENTED').length / docControls.length) * 100) : 0
                }
            });
            setLoading(false);

        } catch (err) {
            console.error(err);
            setError(`Failed to load data: ${err.message} `);
            setLoading(false);
        }
    };

    if (loading) return <div className="p-12 text-center text-gray-400">Loading Framework Data...</div>;
    if (error) return <div className="p-12 text-center text-red-500">{error}</div>;

    // ROUTING TO SUB-COMPONENTS
    if (framework?.code === "HIPAA") {
        // eslint-disable-next-line
        return <FrameworkDetailHipaa />; // DELEGATE TO HIPAA COMPONENT
    }

    const isSOC2 = framework?.code?.includes("SOC2");
    const isISO = framework?.code?.includes("ISO27001");
    const isNIST = framework?.code?.includes("NIST");
    const useGroupedView = isSOC2 || isISO || isNIST;

    // FILTER LOGIC
    // eslint-disable-next-line
    const filteredControls = (controls) => applyFilters(controls);

    // MOCK EVIDENCE CALCULATOR (Random consistency for demo)
    const getEvidenceStats = (controlId) => {
        if (!controlId || typeof controlId !== 'string') return { uploaded: 0, total: 3 };
        const hash = controlId.split('').reduce((a, b) => a + b.charCodeAt(0), 0);
        const total = (hash % 3) + 2; // 2 to 4 files needed
        const uploaded = hash % (total + 1); // 0 to total
        return { uploaded, total };
    };

    // Helper to determine if a specific mock requirement is met based on the random 'uploaded' count
    const isRequirementMet = (index, uploadedCount) => {
        return index < uploadedCount;
    };





    const getRequirements = (control) => {
        if (!control) return REQUIRED_EVIDENCE_DEFAULTS["DEFAULT"];

        // 1. Try Specific Title OR ID Match (PRIORITY OVER AI)
        if (control.control_id) {
            const cleanId = control.control_id.trim();
            console.log("Looking up requirements for ID:", cleanId);
            if (SPECIFIC_EVIDENCE_MAP[cleanId]) {
                return SPECIFIC_EVIDENCE_MAP[cleanId];
            }
        }
        if (control.title && SPECIFIC_EVIDENCE_MAP[control.title]) {
            return SPECIFIC_EVIDENCE_MAP[control.title];
        }

        // 0. AI PRIORITY (If no specific map)
        if (aiRequirements) {
            return aiRequirements;
        }

        // 2. Try Smart Keyword Match (Dynamic)
        const titleLower = control.title.toLowerCase();
        if (titleLower.includes("policy")) {
            return [{ name: "Approved Policy Document", type: "Policy" }, { name: "Evidence of Annual Review", type: "Log" }];
        }
        if (titleLower.includes("training") || titleLower.includes("awareness")) {
            return [{ name: "Training Slide Deck / Material", type: "Document" }, { name: "Attendance / Completion Log", type: "Log" }];
        }

        if (titleLower.includes("vendor") || titleLower.includes("supplier") || titleLower.includes("third party")) {
            return [{ name: "Vendor List", type: "List" }, { name: "Due Diligence Report", type: "Report" }];
        }

        // 3. Try Category Match (Expanded)
        if (control.category && REQUIRED_EVIDENCE_DEFAULTS[control.category]) {
            return REQUIRED_EVIDENCE_DEFAULTS[control.category];
        }

        // 4. Fallback based on Code Prefix if Category is Missing/Mismatch
        // e.g., if category is "CC6.1" but not in defaults
        if (control.category) {
            if (control.category.startsWith("A1")) return [{ name: "Capacity/Availability Report", type: "Report" }];
            if (control.category.startsWith("C1")) return [{ name: "Confidentiality Policy", type: "Policy" }];
            if (control.category.startsWith("P")) return [{ name: "Privacy Notice", type: "Policy" }];
            if (control.category.startsWith("CC")) return [{ name: "Process Description", type: "Document" }, { name: "Evidence of Operation", type: "Evidence" }];
        }

        // 5. Ultimate Fallback
        return REQUIRED_EVIDENCE_DEFAULTS["DEFAULT"];
    };

    return (
        <div className="min-h-screen bg-gray-50 pb-20 animate-fade-in relative">
            {/* PREMIUM HEADER */}
            <div className="bg-white border-b border-gray-200 sticky top-0 z-20 shadow-sm">
                <div className="max-w-7xl mx-auto px-6 py-6">

                    {/* TOP ROW: BREADCRUMB & ACTIONS */}
                    <div className="flex justify-between items-start mb-6">
                        <div>
                            <div className="flex items-center gap-2 text-xs font-bold text-gray-500 mb-1 uppercase tracking-wider">
                                <button onClick={() => navigate('/dashboard')} className="hover:text-blue-600 cursor-pointer transition-colors">Dashboard</button>
                                <ChevronRight className="w-3 h-3" />
                                <span>{framework.code}</span>
                            </div>
                            <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                                {framework.name}
                                {useGroupedView && <span className="text-xs font-bold text-blue-600 bg-blue-50 px-2 py-0.5 rounded-full border border-blue-100">PREMIUM</span>}
                            </h1>
                        </div>
                        <div className="flex gap-2">
                            <button
                                onClick={async () => {
                                    if (window.confirm("RESET Data? This destroys progress.")) {
                                        try {
                                            await fetch(`${API_URL}/frameworks/${framework.id}/seed-controls`, { method: 'POST' });
                                            window.location.reload();
                                        } catch (e) { alert(e); }
                                    }
                                }}
                                className="text-xs font-bold text-red-600 bg-red-50 hover:bg-red-100 px-3 py-2 rounded-lg transition-colors"
                            >
                                Repair Data
                            </button >
                        </div >
                    </div >

                    {/* MIDDLE ROW: DASHBOARD WIDGETS */}
                    < div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6" >
                        {/* WIDGET 1: CONTROLS PROGRESS */}
                        < div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm flex flex-col justify-between" >
                            <div className="flex justify-between items-start mb-4">
                                <h3 className="text-lg font-bold text-gray-900">Controls</h3>
                                <button className="text-xs font-bold text-gray-500 hover:text-gray-900 border border-gray-200 px-2 py-1 rounded">View analytics</button>
                            </div>

                            <div className="flex gap-8 items-end">
                                {/* MAIN PROGRESS */}
                                <div className="flex-1">
                                    <div className="text-4xl font-extrabold text-gray-900 mb-2">{stats.percentage}%</div>
                                    <div className="w-full bg-gray-100 rounded-full h-2 mb-2">
                                        <div className="bg-green-500 h-2 rounded-full transition-all duration-1000" style={{ width: `${stats.percentage}%` }}></div>
                                    </div>
                                    <div className="text-xs font-medium text-gray-500 flex justify-between">
                                        <span>{stats.implemented} completed</span>
                                        <span>{stats.total} total</span>
                                    </div>
                                </div>

                                {/* BREAKDOWN */}
                                <div className="flex-1 space-y-3 pl-6 border-l border-gray-100">
                                    <div>
                                        <div className="flex justify-between text-xs font-bold text-gray-700 mb-1">
                                            <span>Tests</span>
                                            <span className="text-gray-400">{stats.tests?.passing || 0}/{stats.tests?.total || 0}</span>
                                        </div>
                                        <div className="w-full bg-gray-100 rounded-full h-1.5">
                                            <div className="bg-blue-500 h-1.5 rounded-full" style={{ width: `${stats.tests?.percentage || 0}%` }}></div>
                                        </div>
                                    </div>
                                    <div>
                                        <div className="flex justify-between text-xs font-bold text-gray-700 mb-1">
                                            <span>Documents</span>
                                            <span className="text-gray-400">{stats.documents?.ready || 0}/{stats.documents?.total || 0}</span>
                                        </div>
                                        <div className="w-full bg-gray-100 rounded-full h-1.5">
                                            <div className="bg-purple-500 h-1.5 rounded-full" style={{ width: `${stats.documents?.percentage || 0}%` }}></div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div >

                        {/* WIDGET 2: AUDIT TIMELINE (MOCKED VISUAL) */}
                        < div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm flex flex-col" >
                            <div className="flex justify-between items-start mb-6">
                                <div className="flex items-center gap-3">
                                    <h3 className="text-lg font-bold text-gray-900">Audit timeline</h3>
                                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold bg-orange-50 text-orange-700 border border-orange-100">
                                        <div className="w-1.5 h-1.5 rounded-full bg-orange-500 animate-pulse"></div>
                                        In audit
                                    </span>
                                </div>
                                <div className="flex gap-2">
                                    <button className="text-xs font-bold text-gray-600 border border-gray-200 px-3 py-1.5 rounded hover:bg-gray-50">View as auditor</button>
                                </div>
                            </div>

                            <p className="text-xs font-medium text-gray-500 mb-4">Now until July 26 <AlertCircle className="w-3 h-3 inline ml-1 text-gray-400" /></p>

                            {/* TIMELINE VISUAL */}
                            <div className="relative mt-2">
                                <div className="absolute top-1/2 left-0 right-0 h-0.5 bg-gray-200 -z-10 transform -translate-y-1/2"></div>
                                <div className="absolute top-1/2 left-0 w-1/3 h-0.5 bg-orange-500 -z-10 transform -translate-y-1/2"></div>

                                <div className="flex justify-between items-center relative">
                                    {['Now', 'May', 'Jul', 'Sep', 'Nov', 'Jan'].map((month, i) => (
                                        <div key={month} className="flex flex-col items-center gap-2">
                                            <div className={`w-3 h-3 rounded-full border-2 ${i < 3 ? 'bg-orange-500 border-orange-500' : 'bg-white border-gray-300'}`}></div>
                                            <span className="text-[10px] font-bold text-gray-400 uppercase tracking-wide">{month}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div >
                    </div >

                    {/* CONTROLS TOOLBAR (Refactored) */}
                    <ControlsToolbar
                        filters={filters}
                        updateFilter={updateFilter}
                        grouping={grouping}
                        setGrouping={setGrouping}
                        availableGroups={socControls ? Object.keys(socControls).sort() : []}
                        framework={framework}
                    />
                </div >
            </div >

            <div className="max-w-7xl mx-auto px-6 py-8 space-y-8">
                {/* CONTENT AREA starts here */}

                {/* CONTENT AREA */}
                <div className="space-y-10">
                    {/* GROUPED SPECIAL VIEW (SOC 2 & ISO) */}
                    {useGroupedView ? (
                        Object.keys(socControls).sort((a, b) => {
                            // NIST Sorting Logic
                            if (isNIST) {
                                const NIST_ORDER = ["GOVERN", "IDENTIFY", "PROTECT", "DETECT", "RESPOND", "RECOVER"];
                                const idxA = NIST_ORDER.indexOf(a);
                                const idxB = NIST_ORDER.indexOf(b);
                                if (idxA !== -1 && idxB !== -1) return idxA - idxB;
                                if (idxA !== -1) return -1;
                                if (idxB !== -1) return 1;
                            }

                            // Section Sorting Logic
                            if (grouping.groupBy === 'framework') {
                                const ISO_THEMES = ["Organizational", "People", "Physical", "Technological"];
                                return ISO_THEMES.indexOf(a) - ISO_THEMES.indexOf(b);
                            }

                            // Default ISO 27001 Custom Sort Order for Domains
                            const ISO_ORDER = [
                                "Governance",
                                "HR Security",
                                "Asset Management",
                                "Access Control (IAM)",
                                "Physical Security",
                                "Operations",
                                "Configuration Management",
                                "Cryptography",
                                "Logging & Monitoring",
                                "Clock Synchronization",
                                "Vulnerability Management",
                                "Capacity Management",
                                "Backup Management",
                                "Network Security",
                                "SDLC (Development)",
                                "Supplier Mgmt",
                                "Incident & Resilience",
                                "Threat Intel",
                                "Legal & Compliance",
                                "Risk Management",
                                "Performance Evaluation",
                                "Improvement"
                            ];

                            const idxA = ISO_ORDER.indexOf(a);
                            const idxB = ISO_ORDER.indexOf(b);

                            if (idxA !== -1 && idxB !== -1) return idxA - idxB;
                            if (idxA !== -1) return -1;
                            if (idxB !== -1) return 1;
                            return a.localeCompare(b);
                        }).map(category => {
                            // Create copy with slice() before sorting to avoid mutation errors
                            const controls = (socControls[category] || []).slice().sort((a, b) => {
                                const idA = (a.control_id || "").trim();
                                const idB = (b.control_id || "").trim();

                                // Weight: Clauses (4-10) = 1, Annex A = 2
                                const typeA = idA.startsWith("A") || idA.startsWith("a") ? 2 : 1;
                                const typeB = idB.startsWith("A") || idB.startsWith("a") ? 2 : 1;

                                if (typeA !== typeB) return typeA - typeB;

                                // Both are same type. Semantic sort.
                                // Strip non-numeric prefix
                                const partsA = idA.replace(/^[A-Za-z]+\./, '').split('.').map(x => parseInt(x, 10));
                                const partsB = idB.replace(/^[A-Za-z]+\./, '').split('.').map(x => parseInt(x, 10));

                                const len = Math.max(partsA.length, partsB.length);
                                for (let i = 0; i < len; i++) {
                                    const valA = partsA[i] !== undefined ? partsA[i] : 0;
                                    const valB = partsB[i] !== undefined ? partsB[i] : 0;
                                    if (valA !== valB) return valA - valB;
                                }
                                return 0;
                            });
                            if (controls.length === 0) return null;
                            // eslint-disable-next-line no-unused-vars
                            const cosoText = COSO_DESCRIPTIONS[category] || COSO_DESCRIPTIONS["DEFAULT"];

                            return (
                                <div key={category} id={`section-${category}`} className="mb-8 scroll-mt-32">
                                    <div className="mb-4">
                                        <h2 className="text-xl font-bold text-gray-900">{category}</h2>
                                    </div>
                                    <div className="bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden">
                                        <table className="w-full">
                                            <thead>
                                                <tr className="bg-gray-50 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider border-b">
                                                    <th className="px-6 py-3 w-12">
                                                        <input
                                                            type="checkbox"
                                                            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                                        />
                                                    </th>
                                                    <th className="px-6 py-3">Control</th>
                                                    <th className="px-6 py-3 w-48">Evidence Status</th>
                                                    <th className="px-6 py-3 w-32">Standard Control</th>
                                                    <th className="px-6 py-3 w-24">Owner</th>
                                                    <th className="px-6 py-3 w-32">Category</th>
                                                    <th className="px-6 py-3 w-20"></th>
                                                </tr>
                                            </thead>
                                            <tbody className="divide-y divide-gray-200">
                                                {controls.map(control => {
                                                    const stats = getEvidenceStats(control.control_id); // Changed from c to control
                                                    // eslint-disable-next-line no-unused-vars
                                                    const evidenceStatus = stats.uploaded > 0
                                                        ? (stats.uploaded >= stats.total ? "Met" : "Partial")
                                                        : "Not Met";

                                                    return (
                                                        <React.Fragment key={control.id}>
                                                            <tr
                                                                className={`hover:bg-gray-50 transition-colors cursor-pointer ${expandedControlId === control.id ? 'bg-blue-50/50' : ''}`}
                                                                onClick={() => setSelectedControl(control)}
                                                            >
                                                                <td className="px-6 py-4">
                                                                    <input
                                                                        type="checkbox"
                                                                        className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                                                    />
                                                                </td>
                                                                <td className="px-6 py-4">
                                                                    <div className="text-sm font-medium text-gray-900">
                                                                        {control.description}
                                                                    </div>
                                                                </td>
                                                                <td className="px-6 py-4">
                                                                    <div className="flex items-center gap-2">
                                                                        {/* Audit Status Logic */}
                                                                        <div className="flex gap-1">
                                                                            {Array.from({ length: 4 }).map((_, i) => ( // Mock bars
                                                                                <div
                                                                                    key={i}
                                                                                    className={`h-3 w-1.5 rounded-full ${i < (stats.uploaded > 0 ? (stats.uploaded / stats.total) * 4 : 0) ? 'bg-green-500' : 'bg-gray-200'}`}
                                                                                />
                                                                            ))}
                                                                        </div>
                                                                        <span className="text-xs text-gray-500">
                                                                            {stats.uploaded}/{stats.total}
                                                                        </span>
                                                                    </div>
                                                                </td>
                                                                <td className="px-6 py-4">
                                                                    <div className="flex items-center">
                                                                        <span className="text-sm text-gray-500 font-mono">
                                                                            {control.control_id}
                                                                        </span>
                                                                    </div>
                                                                </td>
                                                                <td className="px-6 py-4">
                                                                    <span className="text-xs font-medium text-gray-500 bg-gray-100 px-2 py-1 rounded">
                                                                        System
                                                                    </span>
                                                                </td>
                                                                <td className="px-6 py-4">
                                                                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${control.classification === 'AUTO' ? 'bg-purple-100 text-purple-800 border-purple-200' : control.classification === 'HYBRID' ? 'bg-orange-100 text-orange-800 border-orange-200' : 'bg-blue-100 text-blue-800 border-blue-200'}`}>
                                                                        {control.classification || "MANUAL"}
                                                                    </span>
                                                                    <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                                                                        {(() => {
                                                                            const parts = (control.category || "").split('|');
                                                                            return parts[1] || parts[0] || "General";
                                                                        })()}
                                                                    </span>
                                                                </td>
                                                                <td className="px-6 py-4 text-right">
                                                                    <button
                                                                        onClick={() => setExpandedControlId(expandedControlId === control.id ? null : control.id)}
                                                                        className="text-gray-400 hover:text-blue-600 p-1"
                                                                    >
                                                                        {expandedControlId === control.id ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                                                                    </button>
                                                                </td>
                                                            </tr>
                                                        </React.Fragment>
                                                    );
                                                })}
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            );
                        })
                    ) : (
                        /* STANDARD VIEW */
                        processes.length > 0 ? processes.map(process => (
                            <div key={process.id} className="text-center py-12">Standard View Loaded</div>
                        )) : <div className="text-center py-12">No data</div>
                    )}
                </div>
            </div>

            {/* CONTROL DRAWER */}
            {
                selectedControl && (
                    <div className="fixed inset-0 z-50 flex justify-end">
                        <div className="absolute inset-0 bg-black bg-opacity-30 backdrop-blur-sm" onClick={() => setSelectedControl(null)}></div>
                        <div className="relative w-full max-w-2xl bg-white h-full shadow-2xl flex flex-col transform transition-transform animate-slide-in-right overflow-y-auto">
                            <button
                                onClick={() => setSelectedControl(null)}
                                className="absolute top-4 right-4 p-2 bg-gray-100 rounded-full hover:bg-gray-200"
                            >
                                <X className="w-5 h-5 text-gray-600" />
                            </button>


                            <div className="p-8 pb-4 border-b border-gray-100">
                                <div className="flex gap-2 mb-2">
                                    <span className="text-xs font-bold text-blue-600 px-2 py-1 bg-blue-50 rounded inline-block">
                                        {selectedControl.category}
                                    </span>
                                    <span className="text-xs font-bold text-gray-500 px-2 py-1 bg-gray-100 rounded inline-block font-mono">
                                        {selectedControl.control_id}
                                    </span>
                                    <span className={`text-xs font-bold px-2 py-1 rounded inline-block border ${selectedControl.classification === 'AUTO' ? 'bg-purple-50 text-purple-700 border-purple-200' : 'bg-blue-50 text-blue-700 border-blue-200'}`}>
                                        {selectedControl.classification || "MANUAL"}
                                    </span>
                                </div>
                                <h2 className="text-2xl font-bold text-gray-900 mb-2">{selectedControl.title}</h2>
                                <p className="text-gray-500 text-sm mb-4">
                                    {COSO_DESCRIPTIONS[selectedControl.category] || selectedControl.description}
                                </p>

                                {/* AUDITOR'S PERSPECTIVE (POINTS OF FOCUS) */}
                                <div className="mb-6 bg-amber-50 border border-amber-200 rounded-lg p-4">
                                    <h3 className="text-xs font-bold text-amber-800 uppercase tracking-wider mb-2 flex items-center gap-2">
                                        <Activity className="w-4 h-4" /> Auditor's Perspective (Points of Focus)
                                    </h3>
                                    <p className="text-sm text-amber-900 leading-relaxed">
                                        {COSO_DESCRIPTIONS[(selectedControl.control_id || "").trim()] ||
                                            COSO_DESCRIPTIONS[(selectedControl.control_id || "").split('.')[0]] ||
                                            COSO_DESCRIPTIONS[selectedControl.category] ||
                                            "Auditors will verify that this control is consistently operating and supported by non-repudiable evidence."}
                                    </p>
                                    <div className="mt-3 flex gap-4">
                                        <div className="flex-1">
                                            <span className="text-[10px] font-bold text-amber-700 uppercase block mb-1">What to look for</span>
                                            <span className="text-xs text-amber-800">
                                                Ensure evidence dates align with the audit period. Signatures must be visible.
                                            </span>
                                        </div>
                                        <div className="flex-1">
                                            <span className="text-[10px] font-bold text-amber-700 uppercase block mb-1">Common Pitfalls</span>
                                            <span className="text-xs text-amber-800">
                                                Uploading drafts instead of final versions. Missing timestamp metadata.
                                            </span>
                                        </div>
                                    </div>
                                </div>

                                {/* AI POLICY GENERATOR */}
                                <div className="bg-purple-50 border border-purple-100 rounded-lg p-4 mb-4">
                                    <div className="flex justify-between items-center mb-2">
                                        <h3 className="text-sm font-bold text-purple-900 flex items-center gap-2">
                                            <Shield className="w-4 h-4" /> AI Policy Drafter
                                        </h3>
                                        {!generatedPolicy && (
                                            <button
                                                onClick={handleGeneratePolicy}
                                                disabled={isGenerating}
                                                className="text-xs bg-purple-600 text-white px-3 py-1.5 rounded-md font-bold hover:bg-purple-700 disabled:opacity-50 transition-colors"
                                            >
                                                {isGenerating ? "Drafting..." : "Auto-Generate Policy"}
                                            </button>
                                        )}
                                    </div>
                                    {generatedPolicy ? (
                                        <div className="text-xs text-gray-700 whitespace-pre-wrap bg-white p-3 rounded border border-purple-100 max-h-60 overflow-y-auto">
                                            {generatedPolicy}
                                        </div>
                                    ) : (
                                        <p className="text-xs text-purple-700 italic">
                                            Need a formal policy? Click generate to draft one instantly using AI.
                                        </p>
                                    )}
                                </div>
                            </div>

                            <div className="p-8 space-y-8 flex-1">


                                {/* STANDARD REQUIREMENTS SECTION */}
                                <div className={`border rounded-xl p-5 ${aiRequirements ? 'bg-purple-50 border-purple-100' : 'bg-blue-50 border-blue-100'}`}>
                                    <h3 className={`text-sm font-bold uppercase tracking-wider mb-4 flex items-center gap-2 ${aiRequirements ? 'text-purple-900' : 'text-blue-900'}`}>
                                        {aiRequirements ? <Zap className="w-5 h-5 text-purple-600" /> : <Shield className="w-5 h-5" />}
                                        {aiRequirements ? "AI-Suggested Requirements" : "Standard Requirements"}
                                    </h3>

                                    <div className="space-y-3">
                                        {aiExplanation && (
                                            <div className="mb-4 text-sm text-gray-700 bg-white p-3 rounded-lg border border-purple-100 shadow-sm leading-relaxed">
                                                <span className="font-bold text-purple-800">Clause Requirement: </span>
                                                {typeof aiExplanation === 'object' ? JSON.stringify(aiExplanation) : aiExplanation}
                                            </div>
                                        )}

                                        {loadingAi && (
                                            <div className="p-4 bg-blue-50 text-blue-600 rounded-lg flex items-center gap-2 animate-pulse">
                                                <Shield className="w-5 h-5" />
                                                <span className="text-sm font-semibold">Analyzing control requirements with AI...</span>
                                            </div>
                                        )}

                                        {aiError && (
                                            <div className="p-3 bg-red-50 text-red-600 rounded-lg flex items-center justify-between">
                                                <span className="text-sm font-medium">AI Analysis Failed. showing defaults.</span>
                                                <button
                                                    onClick={() => fetchAiRequirements(selectedControl)}
                                                    className="text-xs bg-white border border-red-200 px-3 py-1 rounded hover:bg-red-100 font-bold"
                                                >
                                                    Retry
                                                </button>
                                            </div>
                                        )}

                                        {!loadingAi && (() => {
                                            const reqs = getRequirements(selectedControl);


                                            return (
                                                <div className="bg-white rounded-lg border border-gray-200 overflow-hidden shadow-sm">
                                                    <table className="w-full text-left border-collapse">
                                                        <thead>
                                                            <tr className="bg-gray-50 border-b border-gray-100 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                                                                <th className="p-3 w-1/4">Requirement</th>
                                                                <th className="p-3 w-1/4">Description</th>
                                                                <th className="p-3 w-1/12">Source</th>
                                                                <th className="p-3 w-1/12">Owner</th>
                                                                <th className="p-3 w-1/12">Status</th>
                                                                <th className="p-3 w-1/6">Last Update</th>
                                                                <th className="p-3 w-1/12 text-center">Actions</th>
                                                            </tr>
                                                        </thead>
                                                        <tbody className="divide-y divide-gray-100">
                                                            {reqs.map((req, idx) => {
                                                                // SMART STATUS SYNC LOGIC
                                                                // Check if any uploaded evidence matches the requirement name or type
                                                                const isMet = evidenceList && evidenceList.some(ev =>
                                                                    (ev.title && ev.title.toLowerCase().includes(req.name.toLowerCase())) ||
                                                                    (ev.filename && ev.filename.toLowerCase().includes(req.name.toLowerCase()))
                                                                );
                                                                const isExpanded = expandedReq === idx;

                                                                return (
                                                                    <React.Fragment key={idx}>
                                                                        <tr
                                                                            onClick={() => setExpandedReq(isExpanded ? null : idx)}
                                                                            className={`cursor-pointer hover:bg-slate-50 transition-colors ${isExpanded ? 'bg-slate-50' : ''}`}
                                                                        >
                                                                            <td className="p-3 text-sm font-medium text-gray-900 border-l-4 border-transparent hover:border-purple-400">
                                                                                <div className="flex items-center gap-2">
                                                                                    {isExpanded ? <ChevronDown className="w-4 h-4 text-gray-400" /> : <ChevronRight className="w-4 h-4 text-gray-400" />}
                                                                                    {req.name}
                                                                                </div>
                                                                            </td>
                                                                            <td className="p-3 text-xs text-gray-600">
                                                                                {req.desc ? (
                                                                                    <div>
                                                                                        <span className="font-bold text-gray-700">Example:</span> {req.desc}
                                                                                    </div>
                                                                                ) : (
                                                                                    <span className="italic text-gray-400">Standard verification.</span>
                                                                                )}
                                                                            </td>
                                                                            <td className="p-3 text-xs text-gray-500">
                                                                                {selectedControl.category === "Technical" ?
                                                                                    <span className="flex items-center gap-1"><Zap className="w-3 h-3" /> Auto</span> :
                                                                                    "Manual"
                                                                                }
                                                                            </td>
                                                                            <td className="p-3 text-xs text-gray-500">
                                                                                <div className="flex items-center gap-1">
                                                                                    <div className="w-4 h-4 bg-gray-200 rounded-full flex items-center justify-center text-[8px] font-bold">SY</div>
                                                                                    <span>System</span>
                                                                                </div>
                                                                            </td>
                                                                            <td className="p-3">
                                                                                {isMet ? (
                                                                                    <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-bold bg-green-100 text-green-800 border border-green-200">
                                                                                        VERIFIED
                                                                                    </span>
                                                                                ) : (
                                                                                    <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-bold bg-orange-100 text-orange-800 border border-orange-200 animate-pulse">
                                                                                        PENDING
                                                                                    </span>
                                                                                )}
                                                                            </td>
                                                                            <td className="p-3 text-xs text-gray-400">
                                                                                {new Date().toLocaleDateString()}
                                                                            </td>
                                                                            <td className="p-3 text-right flex justify-end gap-2" onClick={(e) => e.stopPropagation()}>
                                                                                <input
                                                                                    type="file"
                                                                                    id={`file-upload-req-${idx}`}
                                                                                    className="hidden"
                                                                                    onChange={(e) => handleFileUpload(e, selectedControl.id)}
                                                                                />
                                                                                <button
                                                                                    onClick={() => document.getElementById(`file-upload-req-${idx}`).click()}
                                                                                    title="Upload Evidence"
                                                                                    className="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded"
                                                                                >
                                                                                    <Upload className="w-4 h-4" />
                                                                                </button>
                                                                                <button
                                                                                    onClick={() => handleGenerateArtifact(req)}
                                                                                    title="Auto-Generate Draft"
                                                                                    className="p-1.5 text-gray-400 hover:text-purple-600 hover:bg-purple-50 rounded"
                                                                                >
                                                                                    <Zap className="w-4 h-4" />
                                                                                </button>
                                                                            </td>
                                                                        </tr>
                                                                        {isExpanded && (
                                                                            <tr className="bg-slate-50">
                                                                                <td colSpan="7" className="p-4 pl-12">
                                                                                    <div className="space-y-4">
                                                                                        <div className="grid grid-cols-2 gap-4">
                                                                                            <div>
                                                                                                <h4 className="text-xs font-bold text-gray-500 uppercase tracking-widest mb-1">Auditor Context</h4>
                                                                                                <p className="text-sm text-gray-700 leading-relaxed">
                                                                                                    This artifact is critical for demonstrating operating effectiveness.
                                                                                                    <br />
                                                                                                    <span className="font-bold text-green-700">Good:</span> Final, signed PDF with visible dates.
                                                                                                    <br />
                                                                                                    <span className="font-bold text-red-700">Bad:</span> Editable Word doc, missing signatures, or out of date.
                                                                                                </p>
                                                                                            </div>
                                                                                            <div>
                                                                                                <h4 className="text-xs font-bold text-gray-500 uppercase tracking-widest mb-1">Validation Logic</h4>
                                                                                                <code className="text-xs bg-gray-100 p-2 rounded block font-mono text-gray-600">
                                                                                                    Expected: "{req.name}"
                                                                                                    <br />
                                                                                                    Found: {isMet ? "MATCH" : "NO MATCH"}
                                                                                                </code>
                                                                                            </div>
                                                                                        </div>
                                                                                    </div>
                                                                                </td>
                                                                            </tr>
                                                                        )}
                                                                    </React.Fragment>
                                                                );
                                                            })}
                                                        </tbody>
                                                    </table>
                                                </div>
                                            );
                                        })()}
                                    </div>
                                </div>

                                {/* GAP ANALYSIS SECTION */}
                                <div className="border border-indigo-100 bg-indigo-50 rounded-xl p-5 mt-4">
                                    <div className="flex justify-between items-center mb-4">
                                        <h3 className="text-sm font-bold text-indigo-900 uppercase tracking-wider flex items-center gap-2">
                                            <Activity className="w-5 h-5 text-indigo-600" /> Compliance Status Engine
                                        </h3>
                                        {gapAnalysis && (
                                            <span className={`text-xs font-bold px-3 py-1 rounded-full ${gapAnalysis.status === 'MET' ? 'bg-green-100 text-green-700' :
                                                gapAnalysis.status === 'PARTIAL' ? 'bg-orange-100 text-orange-700' : 'bg-red-100 text-red-700'
                                                }`}>
                                                AI VERDICT: {gapAnalysis.status}
                                            </span>
                                        )}
                                    </div>

                                    {!gapAnalysis ? (
                                        <div className="text-center py-6">
                                            <p className="text-sm text-indigo-800 mb-3">Analyze uploaded evidence against requirements to determine automated status.</p>
                                            <button
                                                onClick={handleGapAnalysis}
                                                disabled={analyzingGap}
                                                className="px-4 py-2 bg-indigo-600 text-white text-sm font-bold rounded-lg shadow-sm hover:bg-indigo-700 disabled:opacity-50 flex items-center gap-2 mx-auto"
                                            >
                                                {analyzingGap ? <span className="animate-spin">⌛</span> : <Zap className="w-4 h-4" />}
                                                {analyzingGap ? "Analyzing Compliance..." : "Run Gap Analysis"}
                                            </button>
                                        </div>
                                    ) : (
                                        <div className="space-y-3">
                                            <div className="bg-white p-4 rounded-lg border border-indigo-100 text-sm text-gray-700">
                                                <strong className="block text-gray-900 mb-1">Reasoning:</strong>
                                                {gapAnalysis.reasoning}
                                            </div>
                                            {gapAnalysis.missing_items && gapAnalysis.missing_items.length > 0 && (
                                                <div className="bg-red-50 p-4 rounded-lg border border-red-100">
                                                    <strong className="block text-red-800 text-xs uppercase mb-2">Missing Evidence:</strong>
                                                    <ul className="list-disc pl-5 text-sm text-red-700 space-y-1">
                                                        {gapAnalysis.missing_items.map((item, i) => (
                                                            <li key={i}>{item}</li>
                                                        ))}
                                                    </ul>
                                                </div>
                                            )}
                                            <button
                                                onClick={handleGapAnalysis}
                                                className="text-xs text-indigo-600 hover:text-indigo-800 font-bold underline mt-2 block text-center"
                                            >
                                                Re-run Analysis
                                            </button>
                                        </div>
                                    )}
                                </div>

                                {/* MISSING EVIDENCE ACTIONS */}
                                <div>
                                    <h3 className="text-sm font-bold text-gray-900 uppercase tracking-wider mb-4 flex items-center gap-2">
                                        <AlertCircle className="w-5 h-5 text-orange-500" /> Pending Actions
                                    </h3>
                                    <div className="bg-white border border-gray-200 rounded-xl divide-y divide-gray-100 overflow-hidden">
                                        {selectedControl.category === "Technical" ? (
                                            <div className="p-8 text-center bg-slate-50">
                                                <div className="mx-auto w-12 h-12 bg-white rounded-full flex items-center justify-center border border-gray-200 shadow-sm mb-3">
                                                    <Zap className="w-6 h-6 text-purple-600" />
                                                </div>
                                                <h4 className="text-sm font-bold text-gray-900">Automated Check Enabled</h4>
                                                <p className="text-xs text-gray-500 mt-1 max-w-xs mx-auto">
                                                    This is a technical control. Evidence is automatically collected and verified by the system. Manual uploads are disabled.
                                                </p>
                                            </div>
                                        ) : (
                                            (() => {
                                                const reqs = getRequirements(selectedControl);
                                                const stats = getEvidenceStats(selectedControl.control_id);
                                                const missing = reqs.filter((_, idx) => !isRequirementMet(idx, stats.uploaded));

                                                if (missing.length === 0) return <div className="p-4 text-sm text-gray-500 italic text-center">No pending actions. All requirements met.</div>;

                                                return missing.map((req, i) => (
                                                    <div key={i} className="p-4 flex justify-between items-center group hover:bg-gray-50 cursor-pointer">
                                                        <div className="flex items-center gap-3">
                                                            <div className="w-8 h-8 rounded-lg bg-orange-100 flex items-center justify-center text-orange-600">
                                                                <Upload className="w-4 h-4" />
                                                            </div>
                                                            <div>
                                                                <p className="text-sm font-medium text-gray-900">Upload {req.name}</p>
                                                                <p className="text-xs text-gray-500">Required for compliance.</p>
                                                            </div>
                                                        </div>
                                                        <div className="flex items-center gap-2">
                                                            <input
                                                                type="file"
                                                                id={`file-upload-${i}`}
                                                                className="hidden"
                                                                onChange={(e) => handleFileUpload(e, selectedControl.id)}
                                                            />
                                                            <button
                                                                onClick={() => document.getElementById(`file-upload-${i}`).click()}
                                                                className="text-xs font-bold text-blue-600 border border-blue-200 px-3 py-1 rounded hover:bg-blue-50"
                                                            >
                                                                Upload
                                                            </button>
                                                            {/* Generate Option for Policies/Procedures */}
                                                            {(req.type === 'Policy' || req.type === 'Procedure' || req.name.toLowerCase().includes('policy') || req.name.toLowerCase().includes('plan')) && (
                                                                <button
                                                                    onClick={(e) => {
                                                                        e.stopPropagation();
                                                                        handleGenerateArtifact(req);
                                                                    }}
                                                                    className="text-xs font-bold text-purple-600 border border-purple-200 px-3 py-1 rounded hover:bg-purple-50 flex items-center gap-1"
                                                                >
                                                                    <Zap className="w-3 h-3" /> Draft
                                                                </button>
                                                            )}
                                                        </div>
                                                    </div>
                                                ));
                                            })()
                                        )}
                                    </div>
                                </div>

                                {/* UPLOADED EVIDENCE SECTION */}
                                {evidenceList && evidenceList.length > 0 && (
                                    <div className="mt-8">
                                        <h3 className="text-sm font-bold text-gray-900 uppercase tracking-wider mb-4 flex items-center gap-2">
                                            <FileText className="w-5 h-5 text-blue-500" /> Uploaded Evidence
                                        </h3>
                                        <div className="bg-white border border-gray-200 rounded-xl divide-y divide-gray-100 overflow-hidden">
                                            {evidenceList.map((ev, i) => (
                                                <div key={ev.id} className="p-4 flex justify-between items-start group hover:bg-gray-50">
                                                    <div className="flex gap-3">
                                                        <div className="w-8 h-8 rounded-lg bg-blue-50 flex items-center justify-center text-blue-600 mt-1">
                                                            <FileText className="w-4 h-4" />
                                                        </div>
                                                        <div>
                                                            <p className="text-sm font-medium text-gray-900">{ev.filename}</p>
                                                            <p className="text-xs text-gray-500">{new Date(ev.uploaded_at || Date.now()).toLocaleDateString()} • {ev.title}</p>
                                                            {ev.validation_source !== 'manual' && (
                                                                <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium bg-green-100 text-green-800 mt-1">
                                                                    Verified by AI
                                                                </span>
                                                            )}
                                                        </div>
                                                    </div>
                                                    <button
                                                        onClick={() => handleReviewDocument(ev)}
                                                        className="text-xs bg-white border border-indigo-200 text-indigo-700 px-3 py-1 rounded hover:bg-indigo-50 font-bold flex items-center gap-1 shadow-sm"
                                                    >
                                                        <Zap className="w-3 h-3" /> Review
                                                    </button>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}

                            </div>

                            <div className="p-6 border-t border-gray-200 bg-gray-50">
                                <div className="text-xs text-center text-gray-500 italic">
                                    {selectedControl.classification === "AUTO" ?
                                        "Control status is managed by automated compliance checks." :
                                        "Control status is automatically updated based on evidence uploads."}
                                </div>
                            </div>
                        </div>
                    </div>
                )
            }
        </div >
    );
};

export default FrameworkDetail;
