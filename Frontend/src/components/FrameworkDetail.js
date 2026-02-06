import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useSearchParams, useLocation } from 'react-router-dom';
import axios from 'axios';
import {
    Zap, Activity, FileText,
    X, Shield, AlertCircle, Upload, ChevronUp, ChevronDown, ChevronRight, FileDown, CheckCircle, Clock, HelpCircle, Copy
} from 'lucide-react';
import { saveAs } from 'file-saver';
import htmlDocx from 'html-docx-js/dist/html-docx';
import { marked } from 'marked';
import FrameworkDetailHipaa from './FrameworkDetail_HIPAA';
import { AIService } from '../services/aiService';
import ControlsToolbar from './ControlsToolbar';
import FrameworkSwitcher from './FrameworkSwitcher';
import useFilters from '../hooks/useFilters';
import { BUSINESS_PROCESSES, normalizeProcessName } from '../constants/ProcessConstants';
import UserProcessView from './UserProcessView';
import EnhancedControlDetail from '../components/EnhancedControlDetail';

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

    "DEFAULT": [{ name: "AUTOGENERATE_BY_AI", type: "AI", desc: "Generating Actionable Requirements..." }]
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
};



const FrameworkDetail = () => {
    const { id, tenantId } = useParams();
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();
    const baseUrl = tenantId ? `/t/${tenantId}` : '';

    // TOOLBAR STATE
    const { filters, updateFilter, applyFilters } = useFilters({
        search: searchParams.get('search') || '',
        status: searchParams.get('status') || 'All'
    });
    // VIEW MODE STATE (Polymorphic Pivot)
    const [viewMode, setViewMode] = useState('intent'); // 'intent' (Business) or 'standard' (ISO/SOC2)

    const [framework, setFramework] = useState(null);
    const [processes, setProcesses] = useState([]);
    const [socControls, setSocControls] = useState({}); // This effectively becomes 'groupedControls'
    const [rawControls, setRawControls] = useState([]); // NEW: Store raw fetched controls
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [stats, setStats] = useState({ total: 0, implemented: 0, percentage: 0 });

    console.log("RENDER FrameworkDetail | ID:", id, "Tenant:", tenantId);
    console.log("Current State:", { framework, loading, error });
    // const [searchTerm, setSearchTerm] = useState(''); // REPLACED BY useFilters

    // DRAWER STATE
    const [selectedControl, setSelectedControl] = useState(null);
    const [evidenceList, setEvidenceList] = useState(null);
    const [expandedControlId, setExpandedControlId] = useState(null);
    const [expandedReq, setExpandedReq] = useState(null);

    // AI State
    const [aiRequirements, setAiRequirements] = useState(null);
    const [aiExplanation, setAiExplanation] = useState(null);
    const [loadingAi, setLoadingAi] = useState(false);
    const [aiError, setAiError] = useState(null);
    const [generatedPolicy, setGeneratedPolicy] = useState(null);
    const [isGenerating, setIsGenerating] = useState(false);
    const [uploadingRevision, setUploadingRevision] = useState(false);
    const [isConfidential, setIsConfidential] = useState(false);
    const [versionHistory, setVersionHistory] = useState([]);
    const [latestAiAnalysis, setLatestAiAnalysis] = useState(null);

    // --- DOCUMENT MANAGEMENT HANDLERS ---

    const getRequirements = (control) => {
        if (!control) return REQUIRED_EVIDENCE_DEFAULTS["DEFAULT"];

        // 0. AI/BACKEND EVIDENCE CHECKLIST (HIGHEST PRIORITY)
        if (aiRequirements && aiRequirements.length > 0) {
            // DETECT LEGACY GENERIC MAPPINGS
            const isGeneric = aiRequirements.some(req => {
                const n = (req.name || "").toLowerCase().trim();
                return n.includes("standard policy") ||
                    n.includes("evidence of execution") ||
                    n.includes("standard verification");
            });

            if (isGeneric) {
                console.log("Detected Generic Legacy Data -> Forcing Auto-Generation");
                return REQUIRED_EVIDENCE_DEFAULTS["DEFAULT"];
            }

            return aiRequirements;
        }

        // 1. Try Specific Title OR ID Match
        if (control.control_id) {
            const cleanId = control.control_id.trim();
            if (SPECIFIC_EVIDENCE_MAP[cleanId]) return SPECIFIC_EVIDENCE_MAP[cleanId];
        }
        if (control.title && SPECIFIC_EVIDENCE_MAP[control.title]) return SPECIFIC_EVIDENCE_MAP[control.title];

        // 2. Try Smart Keyword Match
        const titleLower = control.title.toLowerCase();
        if (titleLower.includes("policy")) return [{ name: "Approved Policy Document", type: "Policy" }, { name: "Evidence of Annual Review", type: "Log" }];
        if (titleLower.includes("training") || titleLower.includes("awareness")) return [{ name: "Training Slide Deck / Material", type: "Document" }, { name: "Attendance / Completion Log", type: "Log" }];
        if (titleLower.includes("vendor") || titleLower.includes("supplier") || titleLower.includes("third party")) return [{ name: "Vendor List", type: "List" }, { name: "Due Diligence Report", type: "Report" }];

        // 3. Try Category Match
        if (control.category && REQUIRED_EVIDENCE_DEFAULTS[control.category]) return REQUIRED_EVIDENCE_DEFAULTS[control.category];

        // 4. Fallback based on Code Prefix
        if (control.category) {
            if (control.category.startsWith("A1")) return [{ name: "Capacity/Availability Report", type: "Report" }];
            if (control.category.startsWith("C1")) return [{ name: "Confidentiality Policy", type: "Policy" }];
            if (control.category.startsWith("P")) return [{ name: "Privacy Notice", type: "Policy" }];
            if (control.category.startsWith("CC")) return [{ name: "Process Description", type: "Document" }, { name: "Evidence of Operation", type: "Evidence" }];
        }

        // 5. Ultimate Fallback
        return REQUIRED_EVIDENCE_DEFAULTS["DEFAULT"];
    };

    const handleDownloadWord = () => {
        if (!generatedPolicy || !selectedControl) return;

        try {
            const htmlContent = marked.parse(generatedPolicy);
            const fullHtml = `
                <!DOCTYPE html>
                <html>
                <head>
                    <style>
                        body { font-family: 'Calibri', sans-serif; font-size: 11pt; }
                        h1 { font-size: 16pt; color: #2E74B5; }
                        h2 { font-size: 14pt; color: #2E74B5; }
                        table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
                        td, th { border: 1px solid #CCC; padding: 8px; }
                        th { background-color: #F2F2F2; }
                    </style>
                </head>
                <body>
                    ${htmlContent}
                </body>
                </html>
            `;

            const blob = htmlDocx.asBlob(fullHtml);
            saveAs(blob, `${selectedControl.control_id}_Policy_Draft.docx`);
        } catch (err) {
            console.error("Export Error:", err);
            alert("Failed to export Word document.");
        }
    };

    const handleUploadRevision = async (e) => {
        const file = e.target.files[0];
        if (!file || !selectedControl) return;

        const formData = new FormData();
        formData.append("file", file);
        formData.append("control_id", formatControlId(selectedControl.control_id));
        formData.append("user_id", "admin"); // TODO: Real user
        formData.append('is_confidential', isConfidential); // Pass toggle state

        setUploadingRevision(true);
        try {
            const response = await axios.post(`${API_URL}/documents/upload-revision`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            alert("Revision uploaded successfully. Status set to Pending Review.");
            // Optionally trigger a Request Approval automatically
            handleRequestApproval(file.name);
        } catch (err) {
            console.error("Upload Error:", err);
            alert("Upload failed.");
        } finally {
            setUploadingRevision(false);
        }
    };

    // ZERO-KNOWLEDGE VERIFICATION TOOL
    const verifyLocalFile = async (e, expectedHash) => {
        const file = e.target.files[0];
        if (!file) return;

        try {
            const arrayBuffer = await file.arrayBuffer();
            const hashBuffer = await crypto.subtle.digest('SHA-256', arrayBuffer);
            const hashArray = Array.from(new Uint8Array(hashBuffer));
            const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');

            if (hashHex === expectedHash) {
                alert("✅ INTEGRITY VERIFIED: This local file matches the unique Witness Hash stored on server.");
            } else {
                alert("❌ MISMATCH: This file does NOT match the original evidence record.");
            }
        } catch (err) {
            console.error("Verification failed", err);
            alert("Verification error.");
        }
    };

    const handleRequestApproval = async (docName = "Policy Draft") => {
        if (!selectedControl) return;
        try {
            await axios.post(`${API_URL}/tasks/request-approval`, {
                title: `Review: ${selectedControl.control_id} - ${docName}`,
                description: `Approval requested for control ${selectedControl.control_id}`,
                control_id: selectedControl.control_id,
                document_id: "doc_pending" // Placeholder
            });
            alert("Approval Requested. Task created for Admin.");
        } catch (err) {
            console.error("Task Error:", err);
            alert("Failed to request approval.");
        }
    };

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

    const location = useLocation(); // Ensure useLocation is imported or available from router context

    const fetchData = async () => {
        try {
            const token = localStorage.getItem('token');
            const headers = { Authorization: `Bearer ${token}` };

            // CONTEXT SWITCHING for Admin viewing Tenant
            if (tenantId) {
                headers['X-Target-Tenant-ID'] = tenantId;
                console.log("Adding X-Target-Tenant-ID header:", tenantId);
            } else {
                console.log("No tenantId found in URL parameters.");
            }

            console.log("Fetching Framework Data...", { id, headers });

            const [fwRes, settingsRes] = await Promise.all([
                axios.get(`${API_URL}/frameworks/${id}`, { headers }),
                axios.get(`${API_URL}/settings`, { headers }).catch(() => ({ data: {} })) // Fail soft if settings missing
            ]);

            console.log("Framework Response:", fwRes.status, fwRes.data);
            console.log("Settings Response:", settingsRes.status, settingsRes.data);

            const fwData = fwRes.data;
            const scopeSettings = settingsRes.data?.content || {};

            const isSOC2 = fwData.code && fwData.code.includes("SOC2");
            const isISO27001 = fwData.code && fwData.code.includes("ISO27001");
            const isISO42001 = fwData.code && fwData.code.includes("ISO42001");
            const isNIST = fwData.code && fwData.code.includes("NIST");
            const isAI = fwData.code && fwData.code.includes("AI_FRAMEWORK");
            const useGroupedView = isSOC2 || isISO27001 || isISO42001 || isNIST || isAI;

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
                // Note: removed relevantSubs dependency as it seemed missing in context or global? 
                // Assuming it was a mistake in the original source or I need to find it. 
                // Wait, 'relevantSubs' was in the cut code. I should check if it survives.
                // In CUT code: `return { ...proc, sub_processes: relevantSubs };`
                // But `relevantSubs` is NOT defined in fetchData. It must be a ReferenceError IN fetchData too.
                // Let's comment it out or fix it to `[]` if not found to avoid another error.
                // Looking at the cut code, `relevantSubs` is just... there. 
                // I will change it to `[]` to be safe/fix the potential bug.
                const filteredProcesses = procRes.data.map(proc => {
                    return { ...proc, sub_processes: [] };
                }).filter(proc => proc.sub_processes.length > 0);
                setProcesses(filteredProcesses);
            } else {
                setProcesses([]);
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


    useEffect(() => {
        // STATE RESET: Clear previous framework data immediately on navigation
        setFramework(null);
        setRawControls([]);
        setProcesses([]);
        setSocControls({});
        setStats({ total: 0, implemented: 0, percentage: 0 });
        setLoading(true);

        fetchData();

        // CLEANUP: Ensure state is cleared when unmounting or changing contexts
        return () => {
            setRawControls([]);
            setFramework(null);
        };
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [id, location.pathname]); // THE LISTENER FIX: Explicit dependency on path

    // EFFECT: Handle Filtering & Grouping when rawControls or settings change
    // EFFECT: Handle Filtering & Grouping when rawControls or settings change
    useEffect(() => {
        if (!framework || !rawControls.length) return;

        const isSOC2 = framework?.code?.includes("SOC2");
        const isISO27001 = framework?.code?.includes("ISO27001");
        const isISO42001 = framework?.code?.includes("ISO42001");
        const isNIST = framework?.code?.includes("NIST");
        const isAI = framework?.code?.includes("AI_FRAMEWORK");
        const useGroupedView = isSOC2 || isISO27001 || isISO42001 || isNIST || isAI;

        if (useGroupedView) {
            // 1. FILTER
            const filtered = applyFilters(rawControls);

            // 2. DEDUPLICATE (Safety check)
            const uniqueControls = Array.from(new Map(filtered.map(item => [item.id, item])).values());

            // 2. GROUPING LOGIC (View Transformer)
            const grouped = {};
            uniqueControls.forEach(c => {
                let key;

                // --- MODE 1: STANDARD VIEW (Strict ISO/SOC2 Structure) ---
                if (viewMode === 'standard') {
                    if (isISO27001) {
                        // ... (Existing ISO 27001 Logic)
                        const id = c.control_id || "";
                        if (id.startsWith("a") || id.startsWith("A")) {
                            // Annex A Grouping (A.5, A.6, etc.)
                            const annexMatch = id.match(/A\.(\d+)/i);
                            const annexNum = annexMatch ? annexMatch[1] : "General";
                            const titles = {
                                "5": "Annex A.5: Organizational Controls",
                                "6": "Annex A.6: People Controls",
                                "7": "Annex A.7: Physical Controls",
                                "8": "Annex A.8: Technological Controls"
                            };
                            key = titles[annexNum] || "Annex A Controls";
                        } else {
                            // Clauses 4-10
                            const clauseMatch = id.match(/^(\d+)/);
                            const clauseNum = clauseMatch ? clauseMatch[1] : "Other";
                            const titles = {
                                "4": "Clause 4: Context of the Organization",
                                "5": "Clause 5: Leadership",
                                "6": "Clause 6: Planning",
                                "7": "Clause 7: Support",
                                "8": "Clause 8: Operation",
                                "9": "Clause 9: Performance Evaluation",
                                "10": "Clause 10: Improvement"
                            };
                            key = titles[clauseNum] || `Clause ${clauseNum}`;
                        }
                    } else if (isISO42001) {
                        // ISO 42001 Standard View (Annex A.2 - A.10 and Clauses)
                        const id = c.control_id || "";
                        // Check for "A.X" pattern first
                        if (id.includes("A.")) {
                            const annexMatch = id.match(/A\.(\d+)/);
                            const annexNum = annexMatch ? annexMatch[1] : null;
                            const titles = {
                                "2": "Annex A.2: AI Policy",
                                "3": "Annex A.3: Internal Organization",
                                "4": "Annex A.4: Resources for AI Systems",
                                "5": "Annex A.5: Assessing Impacts",
                                "6": "Annex A.6: AI System Life Cycle",
                                "7": "Annex A.7: Data for AI Systems",
                                "8": "Annex A.8: Information for Interested Parties",
                                "9": "Annex A.9: Use of AI Systems",
                                "10": "Annex A.10: Third-party Relationships"
                            };
                            key = titles[annexNum] || "Annex A Controls";
                        } else {
                            // Clauses 4-10
                            const clauseMatch = id.match(/-(\d+)\./) || id.match(/^(\d+)\./); // Match "ISO42001-4.1" or "4.1"
                            const clauseNum = clauseMatch ? clauseMatch[1] : "General";
                            const titles = {
                                "4": "Clause 4: Context of the Organization",
                                "5": "Clause 5: Leadership",
                                "6": "Clause 6: Planning",
                                "7": "Clause 7: Support",
                                "8": "Clause 8: Operation",
                                "9": "Clause 9: Performance Evaluation",
                                "10": "Clause 10: Improvement"
                            };
                            key = titles[clauseNum] || "General Requirements";
                        }
                    } else if (isNIST) {
                        // NIST Standard View: Group by Function with Code
                        const NIST_MAP = {
                            "GOVERN": "GOVERN (GV)",
                            "IDENTIFY": "IDENTIFY (ID)",
                            "PROTECT": "PROTECT (PR)",
                            "DETECT": "DETECT (DE)",
                            "RESPOND": "RESPOND (RS)",
                            "RECOVER": "RECOVER (RC)"
                        };

                        // Derive Function from ID prefix since domain now holds Business View
                        const id = c.control_id || "";
                        let cleanPrefix = "Uncategorized";
                        if (id.startsWith("GV")) cleanPrefix = "GOVERN";
                        else if (id.startsWith("ID")) cleanPrefix = "IDENTIFY";
                        else if (id.startsWith("PR")) cleanPrefix = "PROTECT";
                        else if (id.startsWith("DE")) cleanPrefix = "DETECT";
                        else if (id.startsWith("RS")) cleanPrefix = "RESPOND";
                        else if (id.startsWith("RC")) cleanPrefix = "RECOVER";

                        key = NIST_MAP[cleanPrefix] || "Uncategorized";
                    } else {
                        // Fallback for SOC2 etc (Already handled by previous logic, simplified here)
                        key = c.category || "General";
                    }
                }

                // --- MODE 2: BUSINESS VIEW (Strict Process Grouping) ---
                else {
                    // SOC 2 SPECIAL CASE: COSO PRINCIPLES VIEW
                    if (isSOC2) {
                        // ... (Existing SOC 2 Logic)
                        const id = (c.control_id || "").trim();

                        // COSO 1: Control Environment (Principles 1-5)
                        if (id.startsWith("CC1.")) {
                            if (id === "CC1.1") key = "Principle 1: Commitment to integrity and ethical values";
                            else if (id === "CC1.2") key = "Principle 2: Board independence and oversight";
                            else if (id === "CC1.3") key = "Principle 3: Structure, authority, and responsibility";
                            else if (id === "CC1.4") key = "Principle 4: Commitment to competence";
                            else if (id === "CC1.5") key = "Principle 5: Accountability";
                            else key = "COSO 1: Control Environment (General)";
                        }
                        // COSO 2: Communication & Information (Principles 13-15)
                        else if (id.startsWith("CC2.")) {
                            if (id === "CC2.1") key = "Principle 13: Use relevant, quality information";
                            else if (id === "CC2.2") key = "Principle 14: Internal communication";
                            else if (id === "CC2.3") key = "Principle 15: External communication";
                            else key = "COSO 4: Information and Communication (General)";
                        }
                        // COSO 3: Risk Assessment (Principles 6-9)
                        else if (id.startsWith("CC3.")) {
                            if (id === "CC3.1") key = "Principle 6: Specify suitable objectives";
                            else if (id === "CC3.2") key = "Principle 7: Identify and analyze risks";
                            else if (id === "CC3.3") key = "Principle 8: Assess fraud risk";
                            else if (id === "CC3.4") key = "Principle 9: Identify and analyze significant changes";
                            else key = "COSO 2: Risk Assessment (General)";
                        }
                        // COSO 4: Monitoring Activities (Principles 16-17)
                        else if (id.startsWith("CC4.")) {
                            if (id === "CC4.1") key = "Principle 16: Ongoing and separate evaluations";
                            else if (id === "CC4.2") key = "Principle 17: Communicate deficiencies";
                            else key = "COSO 5: Monitoring Activities (General)";
                        }
                        // COSO 5: Control Activities (Principles 10-12)
                        else if (id.startsWith("CC5.")) {
                            if (id === "CC5.1") key = "Principle 10: Select and develop control activities";
                            else if (id === "CC5.2") key = "Principle 11: General controls over technology";
                            else if (id === "CC5.3") key = "Principle 12: Deploy policies and procedures";
                            else key = "COSO 3: Control Activities (General)";
                        }

                        // TRUST SERVICES CRITERIA (Non-COSO)
                        else if (id.startsWith("CC6")) key = "CC6: Logical and Physical Access (TSC)";
                        else if (id.startsWith("CC7")) key = "CC7: System Operations (TSC)";
                        else if (id.startsWith("CC8")) key = "CC8: Change Management (TSC)";
                        else if (id.startsWith("CC9")) key = "CC9: Risk Mitigation (TSC)";
                        else if (id.startsWith("A")) key = "Availability (TSC)";
                        else if (id.startsWith("C")) key = "Confidentiality (TSC)";
                        else if (id.startsWith("PI")) key = "Processing Integrity (TSC)";
                        else if (id.startsWith("P")) key = "Privacy (TSC)";
                        else {
                            key = "Additional Criteria";
                        }

                    } else if (isISO42001) {
                        // ISO 42001 BUSINESS VIEW (Use Domain field from seeding)
                        // Maps to "Annex A: AI Controls" etc.
                        key = c.domain || "General";
                    } else if (isNIST) {
                        // NIST BUSINESS VIEW
                        key = c.domain || "General";
                    } else {
                        // STANDARD BUSINESS VIEW (ISO 27001 etc.)
                        const rawName = c.process_name ||
                            c.category ||
                            (c.domain && !c.domain.startsWith("Clause") && !c.domain.startsWith("Annex") ? c.domain : null) ||
                            "Uncategorized Controls";

                        key = normalizeProcessName(rawName);
                    }
                }

                // SAFETY FALLBACK: Ensure key is never null/undefined
                if (!key) key = "Uncategorized";
                if (!grouped[key]) grouped[key] = [];
                grouped[key].push(c);
            });
            console.log("DEBUG: Grouped Controls:", Object.keys(grouped), grouped);
            setSocControls(grouped);

            // 3. SORT KEYS
            const sortedGrouped = {};

            if (viewMode === 'intent') {
                // CANONICAL PROCESS SORT
                const keys = Object.keys(grouped).sort((a, b) => {
                    // ISO 42001 BUSINESS SORT
                    if (isISO42001) {
                        const AI_DOMAINS = [
                            "AI Ethics & Governance",
                            "Risk & Impact",
                            "Data & Privacy",
                            "AI Engineering (MLOps)",
                            "Model Security",
                            "Human-in-the-Loop",
                            "Third-Party / Supply Chain",
                            "People & Culture",
                            "Continuous Monitoring"
                        ];
                        const idxA = AI_DOMAINS.indexOf(a);
                        const idxB = AI_DOMAINS.indexOf(b);
                        if (idxA !== -1 && idxB !== -1) return idxA - idxB;
                        if (idxA !== -1) return -1;
                        if (idxB !== -1) return 1;
                        if (idxA !== -1) return -1;
                        if (idxB !== -1) return 1;
                        return a.localeCompare(b);
                    }

                    // NIST STANDARD SORT
                    if (isNIST) {
                        const NIST_ORDER = ["GOVERN", "IDENTIFY", "PROTECT", "DETECT", "RESPOND", "RECOVER"];
                        const idxA = NIST_ORDER.indexOf(a);
                        const idxB = NIST_ORDER.indexOf(b);
                        if (idxA !== -1 && idxB !== -1) return idxA - idxB;
                        if (idxA !== -1) return -1;
                        if (idxB !== -1) return 1;
                        return a.localeCompare(b);
                    }

                    // NIST BUSINESS SORT (When in Business View)
                    if (isNIST) {
                        const NIST_DOMAINS = [
                            "Governance & Strategy",
                            "Asset & Inventory",
                            "Identity & Access (IAM)",
                            "Risk & Vulnerability",
                            "Data Protection",
                            "Security Awareness (People)",
                            "Infrastructure & Network",
                            "Security Monitoring (SOC)",
                            "Incident Management",
                            "Business Continuity",
                            "Third-Party / Supply Chain"
                        ];
                        const idxA = NIST_DOMAINS.indexOf(a);
                        const idxB = NIST_DOMAINS.indexOf(b);
                        if (idxA !== -1 && idxB !== -1) return idxA - idxB;
                        if (idxA !== -1) return -1;
                        if (idxB !== -1) return 1;
                        return a.localeCompare(b);
                    }

                    // NIST STANDARD SORT (Fallback if logic leaks, but intended for Standard View block above usually)
                    // Actually, Standard View sorts in the 'else' block below or separate logic? 
                    // NO, 'standard' view uses Object.keys().sort() in the 'else' block of 'viewMode === intent'.
                    // This block IS 'viewMode === intent'. So we only need Business Sort here.

                    // SOC 2 COSO SORT
                    if (a.startsWith("Principle") || a.startsWith("COSO") || a.startsWith("TSC")) {
                        const getCosoScore = (k) => {
                            if (k.startsWith("Principle")) {
                                const match = k.match(/Principle (\d+)/);
                                return match ? parseInt(match[1]) : 0;
                            }
                            if (k.startsWith("COSO 1")) return 100; // Fallbacks
                            if (k.startsWith("COSO 2")) return 200;
                            if (k.startsWith("COSO 3")) return 300;
                            if (k.startsWith("COSO 4")) return 400;
                            if (k.startsWith("COSO 5")) return 500;

                            if (k.startsWith("TSC: Logical")) return 1000;
                            if (k.startsWith("TSC: System")) return 1001;
                            if (k.startsWith("TSC: Change")) return 1002;
                            if (k.startsWith("TSC: Risk")) return 1003;
                            if (k.startsWith("TSC: Avail")) return 1004;
                            if (k.startsWith("TSC: Confid")) return 1005;
                            if (k.startsWith("TSC: Process")) return 1006;
                            if (k.startsWith("TSC: Privacy")) return 1007;
                            return 9999;
                        };
                        return getCosoScore(a) - getCosoScore(b);
                    }

                    // STANDARD BUSINESS PROCESS SORT
                    const idxA = BUSINESS_PROCESSES.indexOf(a);
                    const idxB = BUSINESS_PROCESSES.indexOf(b);
                    if (idxA !== -1 && idxB !== -1) return idxA - idxB;
                    if (idxA !== -1) return -1;
                    if (idxB !== -1) return 1;
                    return a.localeCompare(b);
                });
                keys.forEach(k => sortedGrouped[k] = grouped[k]);
                setSocControls(sortedGrouped);
            } else {
                // Standard Sort (Re-using existing logic logic simplified)
                const keys = Object.keys(grouped).sort((a, b) => {
                    // Clause sort helper
                    const getScore = (k) => {
                        // NIST Standard Sort
                        if (k.includes("GOVERN")) return 1;
                        if (k.includes("IDENTIFY")) return 2;
                        if (k.includes("PROTECT")) return 3;
                        if (k.includes("DETECT")) return 4;
                        if (k.includes("RESPOND")) return 5;
                        if (k.includes("RECOVER")) return 6;

                        // ISO Standard Sort
                        if (k.startsWith("Clause 4")) return 10;
                        if (k.startsWith("Clause 5")) return 11;
                        if (k.startsWith("Clause 6")) return 12;
                        if (k.startsWith("Clause 7")) return 13;
                        if (k.startsWith("Clause 8")) return 14;
                        if (k.startsWith("Clause 9")) return 15;
                        if (k.startsWith("Clause 10")) return 16;

                        // ISO Annex A Sort
                        if (k.startsWith("Annex A.2")) return 20; // ISO 42001
                        if (k.startsWith("Annex A.3")) return 30;
                        if (k.startsWith("Annex A.4")) return 40;
                        if (k.startsWith("Annex A.5")) return 50;
                        if (k.startsWith("Annex A.6")) return 60;
                        if (k.startsWith("Annex A.7")) return 70;
                        if (k.startsWith("Annex A.8")) return 80;
                        if (k.startsWith("Annex A.9")) return 90;
                        if (k.startsWith("Annex A.10")) return 100;

                        // SOC2 / Fallback
                        return 999;
                    };
                    return getScore(a) - getScore(b);
                });
                keys.forEach(k => sortedGrouped[k] = grouped[k]);
                setSocControls(sortedGrouped);
            }
        }
    }, [rawControls, filters, viewMode, framework, applyFilters]);


    // Helper to format Control ID for display (removes Tenant UUID and ISO Prefix)
    const formatControlId = (controlId) => {
        if (!controlId) return "";
        let clean = controlId.split('#')[0]; // Remove Tenant UUID
        clean = clean.replace("ISO42001-", ""); // Remove ISO Prefix
        return clean;
    };

    // FETCH EVIDENCE & RESET AI WHEN CONTROL IS SELECTED
    useEffect(() => {
        if (selectedControl) {
            fetchEvidence(selectedControl.id);
            if (selectedControl.control_id) {
                fetchVersionHistory(formatControlId(selectedControl.control_id));
            }
            setGeneratedPolicy(null); // Reset AI draft
            setLatestAiAnalysis(null);
        } else {
            setEvidenceList([]);
            setVersionHistory([]);
            setGeneratedPolicy(null);
            setLatestAiAnalysis(null);
        }
    }, [selectedControl]);

    // FETCH AI SUGGESTIONS WHEN CONTROL OPENS
    useEffect(() => {
        if (selectedControl) {
            setAiRequirements(null);
            setAiError(false);
            fetchAiRequirements(selectedControl);
        }
        // eslint-disable-next-line
    }, [selectedControl]);

    const fetchAiRequirements = async (control, force = false) => {
        setLoadingAi(true);
        setAiError(false);
        try {
            // Use Clean ID for AI Analysis Context
            const cleanId = formatControlId(control.control_id);
            let data = await AIService.analyzeControlRequirements(control.title, control.description, control.category, cleanId, force);

            // LIVE OVERRIDE: Aggressive Healing DISABLED (User requested persistence)
            let isGeneric = false;
            /*
            if (data && data.requirements && data.requirements.length > 0) {
                isGeneric = data.requirements.some(r => {
                    const name = (r.name || "").toLowerCase();
                    return name.includes("standard policy") ||
                        name.includes("evidence of execution") ||
                        name.includes("autogenerate") ||
                        name.includes("standard verification") ||
                        name.includes("master intent library") ||
                        (data.explanation || "").toLowerCase().includes("generated by ai");
                });
            }
     
            if (isGeneric || !data || !data.requirements || data.requirements.length === 0) {
                console.log(`⚡ LIVE OVERRIDE: Generic/Empty Data Detected for ${cleanId}. Forcing Regeneration...`);
                // Force Backend Regeneration
                const regeneratedData = await AIService.analyzeControlRequirements(control.title, control.description, control.category, cleanId, true);
                if (regeneratedData && regeneratedData.requirements) {
                    data = regeneratedData;
                }
            }
            */

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

    const fetchVersionHistory = async (controlId) => {
        try {
            const token = localStorage.getItem('token');
            const res = await axios.get(`${API_URL}/documents/history/${controlId}`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setVersionHistory(res.data);
        } catch (e) {
            console.error("Failed to load history", e);
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
        formData.append('is_confidential', isConfidential); // Pass toggle state

        try {
            const token = localStorage.getItem('token');
            const response = await axios.post(`${API_URL}/evidence/upload`, formData, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'multipart/form-data'
                }
            });
            alert("File uploaded successfully!");
            // If upload returned analysis, set it
            if (response.data.ai_analysis) {
                setLatestAiAnalysis(response.data.ai_analysis);
            }

            fetchVersionHistory(formatControlId(selectedControl.control_id));
            setUploadingRevision(false);
            e.target.value = null; // Reset input

            if (response.data.ai_analysis && response.data.ai_analysis.final_verdict === "PASS") {
                alert("AI Review Passed! Document forwarded to Admin for approval.");
            } else {
                alert("AI Gap Analysis Complete. Please review the findings.");
            }

        } catch (error) {
            console.error("Upload failed", error);
            if (error.response && error.response.status === 400) {
                alert(`⚠️ UPLOAD BLOCKED: ${error.response.data.detail}`);
            } else {
                alert("Upload failed. Please try again.");
            }
            setUploadingRevision(false);
        }
    };







    // ROUTING TO SUB-COMPONENTS
    if (framework?.code === "HIPAA") {
        // eslint-disable-next-line
        return <FrameworkDetailHipaa />; // DELEGATE TO HIPAA COMPONENT
    }

    const isSOC2 = framework?.code?.includes("SOC2");
    const isISO27001 = framework?.code?.includes("ISO27001");
    const isISO42001 = framework?.code?.includes("ISO42001");
    const isNIST = framework?.code?.includes("NIST");
    const isAI = framework?.code?.includes("AI_FRAMEWORK");
    const useGroupedView = isSOC2 || isISO27001 || isISO42001 || isNIST || isAI;

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







    if (loading) return <div className="p-20 text-center">Loading Framework Data...</div>;
    if (error) return <div className="p-20 text-center text-red-500">Error: {error}</div>;
    if (!framework) return <div className="p-20 text-center">No framework found.</div>;

    return (
        <>
            <div className="min-h-screen bg-gray-50 pb-20 animate-fade-in relative">
                {/* PREMIUM HEADER */}
                <div className="bg-white border-b border-gray-200 sticky top-0 z-20 shadow-sm">
                    <div className="w-full px-8 py-6">

                        {/* TOP ROW: BREADCRUMB & ACTIONS */}
                        <div className="flex justify-between items-start mb-6">
                            <div>
                                <div className="flex items-center gap-2 text-xs font-bold text-gray-500 mb-1 uppercase tracking-wider">
                                    <button onClick={() => navigate(`${baseUrl}/dashboard`)} className="hover:text-blue-600 cursor-pointer transition-colors">Dashboard</button>
                                    <ChevronRight className="w-3 h-3" />
                                    <span>{framework.code}</span>
                                </div>
                                <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                                    {framework.name}
                                    {useGroupedView && <span className="text-xs font-bold text-blue-600 bg-blue-50 px-2 py-0.5 rounded-full border border-blue-100">PREMIUM</span>}
                                </h1>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="w-full px-8 py-6">

                    {/* MIDDLE ROW: DASHBOARD WIDGETS */}
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
                        {/* WIDGET 1: CONTROLS PROGRESS */}
                        <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm flex flex-col justify-between">
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

                            {/* --- AI DOCUMENT REVIEWER INSIGHTS --- */}
                            {latestAiAnalysis && (
                                <div className={`mt-6 p-4 rounded-lg border ${latestAiAnalysis.final_verdict === 'PASS' && latestAiAnalysis.date_check_passed ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}`}>
                                    <div className="flex items-center justify-between mb-2">
                                        <h4 className={`text-sm font-bold ${latestAiAnalysis.final_verdict === 'PASS' && latestAiAnalysis.date_check_passed ? 'text-green-800' : 'text-red-800'}`}>
                                            AI Document Analysis
                                        </h4>
                                        <span className="text-xs font-mono bg-white px-2 py-1 rounded border">
                                            {latestAiAnalysis.final_verdict === 'PASS' && latestAiAnalysis.date_check_passed ? 'PASSED' : 'ACTION REQUIRED'}
                                        </span>
                                    </div>

                                    {latestAiAnalysis.storage_status === "DELETED_CONFIDENTIAL" && (
                                        <div className="mb-4 bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden">
                                            {/* HEADER */}
                                            <div className="bg-gradient-to-r from-gray-50 to-white px-4 py-3 border-b border-gray-100 flex justify-between items-center">
                                                <h4 className="text-sm font-bold text-gray-800 flex items-center gap-2">
                                                    <Shield className="w-4 h-4 text-green-600" />
                                                    Compliance Attestation Card
                                                </h4>
                                                <span className="text-[10px] font-bold px-2 py-0.5 bg-green-100 text-green-800 rounded-full border border-green-200">
                                                    EVIDENCE VERIFIED BY AI
                                                </span>
                                            </div>

                                            {/* BODY */}
                                            <div className="p-4 space-y-4">
                                                {/* METADATA GRID */}
                                                <div className="grid grid-cols-2 gap-4">
                                                    <div>
                                                        <span className="text-[10px] text-gray-400 font-bold uppercase tracking-wider block mb-1">Status</span>
                                                        <span className="text-sm font-bold text-gray-700">Verified & Purged</span>
                                                    </div>
                                                    <div>
                                                        <span className="text-[10px] text-gray-400 font-bold uppercase tracking-wider block mb-1">Timestamp</span>
                                                        <span className="text-sm font-mono text-gray-600">{new Date().toLocaleString()}</span>
                                                    </div>
                                                </div>

                                                {/* SUMMARY */}
                                                <div>
                                                    <span className="text-[10px] text-gray-400 font-bold uppercase tracking-wider block mb-1">AI Witness Statement</span>
                                                    <p className="text-sm text-gray-700 italic border-l-2 border-green-500 pl-3 py-1 bg-green-50/50 rounded-r">
                                                        "{latestAiAnalysis.summary || "Evidence context extracted and verified."}"
                                                    </p>
                                                </div>

                                                {/* AUDIT RECEIPT */}
                                                <div className="bg-gray-50 rounded border border-gray-200 p-3">
                                                    <div className="flex justify-between items-center mb-1">
                                                        <span className="text-[10px] text-gray-500 font-bold flex items-center gap-1">
                                                            SHA-256 AUDIT RECEIPT
                                                            <div className="group relative inline-block">
                                                                <HelpCircle className="w-3 h-3 text-gray-400 cursor-help" />
                                                                <div className="hidden group-hover:block absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 w-48 bg-gray-900 text-white text-[10px] p-2 rounded z-50">
                                                                    Confidential data is not stored on our servers. This hash serves as a permanent, verifiable proof of your compliance record.
                                                                </div>
                                                            </div>
                                                        </span>
                                                        <button
                                                            onClick={() => {
                                                                navigator.clipboard.writeText(latestAiAnalysis.file_hash);
                                                                alert("Hash copied to clipboard!");
                                                            }}
                                                            className="text-[10px] text-blue-600 hover:text-blue-800 font-bold flex items-center gap-1"
                                                        >
                                                            <Copy className="w-3 h-3" /> Copy Hash
                                                        </button>
                                                    </div>
                                                    <div className="font-mono text-[10px] text-gray-500 break-all select-all">
                                                        {latestAiAnalysis.file_hash}
                                                    </div>

                                                    <div className="mt-3 pt-3 border-t border-gray-200">
                                                        <label className="flex items-center justify-center gap-2 cursor-pointer w-full text-xs font-bold text-gray-600 hover:text-gray-900 bg-white border border-gray-300 hover:bg-gray-50 py-2 rounded transition-colors">
                                                            <Upload className="w-3 h-3" /> Verify Local File Match
                                                            <input
                                                                type="file"
                                                                className="hidden"
                                                                onChange={(e) => verifyLocalFile(e, latestAiAnalysis.file_hash)}
                                                            />
                                                        </label>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    )}
                                    <p className="text-xs text-gray-700 mb-2 italic">"{latestAiAnalysis.summary}"</p>

                                    {/* PII WARNING */}
                                    {latestAiAnalysis.pii_status && latestAiAnalysis.pii_status.action !== "NONE" && (
                                        <div className="mb-3 bg-red-100 border border-red-300 p-2 rounded flex items-center gap-2">
                                            <span className="text-xl">🛡️</span>
                                            <div>
                                                <p className="text-xs font-bold text-red-800">PRIVACY WARNING: {latestAiAnalysis.pii_status.action} REQUIRED</p>
                                                <p className="text-xs text-red-700">{latestAiAnalysis.pii_status.reasoning}</p>
                                            </div>
                                        </div>
                                    )}

                                    {(!latestAiAnalysis.date_check_passed || latestAiAnalysis.final_verdict === 'FAIL') && (
                                        <div className="mt-2">
                                            <p className="text-xs font-semibold text-red-700">Gaps Identified:</p>
                                            <ul className="list-disc list-inside text-xs text-red-600 mt-1 space-y-1">
                                                {!latestAiAnalysis.date_check_passed && <li>Document Date is older than 12 months or missing.</li>}
                                                {latestAiAnalysis.gaps_found && latestAiAnalysis.gaps_found.map((gap, i) => (
                                                    <li key={i}>{gap}</li>
                                                ))}
                                            </ul>
                                        </div>
                                    )}

                                    {latestAiAnalysis.final_verdict === 'PASS' && latestAiAnalysis.date_check_passed && (
                                        <div className="mt-3 text-xs text-green-700 flex items-center">
                                            <span className="mr-2">✅</span>
                                            <span>Forwarded to Admin for Final Signature.</span>
                                        </div>
                                    )}
                                </div>
                            )}

                        </div>

                        {/* --- VERSION HISTORY --- AUDIT TIMELINE (MOCKED VISUAL) */}
                        <div className="bg-white rounded-xl border border-gray-200 p-5 shadow-sm flex flex-col">
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



                        </div>
                    </div>
                </div>
                <div className="w-full px-8 py-8 space-y-8">
                    {/* CONTROLS TOOLBAR (Actions Row) - Moved here for better layout */}
                    <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm flex flex-col md:flex-row justify-between items-center gap-4 transition-all">
                        <FrameworkSwitcher
                            viewMode={viewMode}
                            setViewMode={setViewMode}
                            frameworkCode={framework?.code}
                        />
                        <div className="flex-1 w-full md:w-auto flex justify-end">
                            <ControlsToolbar
                                filters={filters}
                                updateFilter={updateFilter}
                                availableGroups={socControls ? Object.keys(socControls).sort() : []}
                                framework={framework}
                            />
                        </div>
                    </div>
                    {/* CONTENT AREA starts here */}

                    {/* CONTENT AREA */}
                    <div className="space-y-10">
                        {/* GROUPED SPECIAL VIEW (SOC 2 & ISO) */}
                        {useGroupedView ?

                            // UNIFIED BUSINESS & STANDARD VIEW (List Based)
                            // We now use the same List renderer for both, just grouped differently.
                            (Object.keys(socControls).sort((a, b) => {
                                // NIST Sorting Logic
                                if (isNIST) {
                                    const NIST_ORDER = ["GOVERN", "IDENTIFY", "PROTECT", "DETECT", "RESPOND", "RECOVER"];
                                    const idxA = NIST_ORDER.indexOf(a);
                                    const idxB = NIST_ORDER.indexOf(b);
                                    if (idxA !== -1 && idxB !== -1) return idxA - idxB;
                                    if (idxA !== -1) return -1;
                                    if (idxB !== -1) return 1;
                                }

                                // ISO 42001 Sorting Logic
                                if (isISO42001) {
                                    const getScore = (k) => {
                                        if (k.startsWith("Clause 4")) return 4;
                                        if (k.startsWith("Clause 5")) return 5;
                                        if (k.startsWith("Clause 6")) return 6;
                                        if (k.startsWith("Clause 7")) return 7;
                                        if (k.startsWith("Clause 8")) return 8;
                                        if (k.startsWith("Clause 9")) return 9;
                                        if (k.startsWith("Clause 10")) return 10;
                                        if (k.startsWith("Annex A")) return 100 + parseInt(k.match(/A\.(\d+)/)?.[1] || 0);
                                        return 999;
                                    };
                                    return getScore(a) - getScore(b);
                                }

                                // SOC 2 COSO Principles Sorting (Numerical)
                                if (isSOC2 && viewMode === 'intent') {
                                    const getCosoScore = (k) => {
                                        // Extract Principle Number "Principle 10: ..."
                                        if (k.startsWith("Principle")) {
                                            const match = k.match(/Principle (\d+)/);
                                            return match ? parseInt(match[1]) : 0;
                                        }
                                        if (k.startsWith("COSO 1")) return 100;
                                        if (k.startsWith("COSO 2")) return 200;
                                        if (k.startsWith("COSO 3")) return 300;
                                        if (k.startsWith("COSO 4")) return 400;
                                        if (k.startsWith("COSO 5")) return 500;

                                        if (k.startsWith("TSC: Logical")) return 1000;
                                        if (k.startsWith("TSC: System")) return 1001;
                                        if (k.startsWith("TSC: Change")) return 1002;
                                        if (k.startsWith("TSC: Risk")) return 1003;
                                        if (k.startsWith("TSC: Avail")) return 1004;
                                        if (k.startsWith("TSC: Confid")) return 1005;
                                        if (k.startsWith("TSC: Process")) return 1006;
                                        if (k.startsWith("TSC: Privacy")) return 1007;
                                        return 9999;
                                    };
                                    return getCosoScore(a) - getCosoScore(b);
                                }

                                // Section Sorting Logic
                                if (viewMode === 'standard' && !isISO27001) { // Added !isISO27001 just in case, but 'framework' is not used for ISO generally in this context
                                    const ISO_THEMES = ["Organizational", "People", "Physical", "Technological"];
                                    return ISO_THEMES.indexOf(a) - ISO_THEMES.indexOf(b);
                                }

                                // ISO 27001 Section (Clause/Annex) Sorting
                                if (isISO27001 && viewMode === 'standard') {
                                    const getScore = (k) => {
                                        if (k.startsWith("Clause 4")) return 4;
                                        if (k.startsWith("Clause 5")) return 5;
                                        if (k.startsWith("Clause 6")) return 6;
                                        if (k.startsWith("Clause 7")) return 7;
                                        if (k.startsWith("Clause 8")) return 8;
                                        if (k.startsWith("Clause 9")) return 9;
                                        if (k.startsWith("Clause 10")) return 10;
                                        if (k.startsWith("Annex A")) return 100 + parseInt(k.match(/A\.(\d+)/)?.[1] || 0);
                                        return 999;
                                    };
                                    return getScore(a) - getScore(b);
                                }

                                // Default ISO 27001 Custom Sort Order for Domains
                                const ISO_ORDER = [
                                    "Governance & Policy",
                                    "HR Security",
                                    "Asset Management",
                                    "Access Control (IAM)",
                                    "Physical Security",
                                    "Operations (General)",
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
                                    <div key={`${category}-${viewMode}`} id={`section-${category}`} className="mb-8 scroll-mt-32">
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
                                                                        <div className="flex flex-col">
                                                                            <span className="text-sm font-bold text-gray-900 leading-snug mb-1 line-clamp-3" title={control.description}>
                                                                                {control.description}
                                                                            </span>
                                                                            <span className="text-xs text-gray-500 font-medium">
                                                                                {control.title}
                                                                            </span>
                                                                        </div>
                                                                        {viewMode === 'intent' && (
                                                                            <div className="inline-flex items-center gap-1 ml-2 align-middle bg-gradient-to-r from-indigo-50 to-purple-50 px-2 py-0.5 rounded border border-indigo-100 group relative">
                                                                                <span className="text-[10px] font-bold text-indigo-600 tracking-tight">IMPACT:</span>
                                                                                <div className="flex -space-x-1">
                                                                                    <div className="w-4 h-4 rounded-full bg-blue-100 border border-white flex items-center justify-center text-[8px] font-bold text-blue-700" title="ISO 27001">I</div>
                                                                                    <div className="w-4 h-4 rounded-full bg-green-100 border border-white flex items-center justify-center text-[8px] font-bold text-green-700" title="SOC 2 Type II">S</div>
                                                                                    <div className="w-4 h-4 rounded-full bg-purple-100 border border-white flex items-center justify-center text-[8px] font-bold text-purple-700" title="HIPAA">H</div>
                                                                                    <div className="w-4 h-4 rounded-full bg-gray-100 border border-white flex items-center justify-center text-[8px] text-gray-600">+2</div>
                                                                                </div>

                                                                                {/* TOOLTIP */}
                                                                                <div className="hidden group-hover:block absolute bottom-full left-0 mb-2 w-48 bg-gray-900 text-white text-xs rounded p-2 shadow-xl z-50 pointer-events-none">
                                                                                    <p className="font-bold mb-1">Universal Intent Multiplier</p>
                                                                                    <p className="text-gray-300">Completing this task satisfies requirements in 5 active standards.</p>
                                                                                </div>
                                                                            </div>
                                                                        )}
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
                                                                                {formatControlId(control.control_id)}
                                                                            </span>
                                                                        </div>
                                                                    </td>
                                                                    <td className="px-6 py-4">
                                                                        <span className="text-xs font-medium text-gray-500 bg-gray-100 px-2 py-1 rounded">
                                                                            System
                                                                        </span>
                                                                    </td>
                                                                    <td className="px-6 py-4">
                                                                        <div className="flex flex-col items-start gap-2">
                                                                            {/* 1. Work Type (Small Outline Badge) */}
                                                                            <span className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-medium border bg-white ${control.classification === 'AUTO' ? 'text-purple-700 border-purple-200' :
                                                                                control.classification === 'HYBRID' ? 'text-orange-700 border-orange-200' :
                                                                                    'text-blue-700 border-blue-200'
                                                                                }`}>
                                                                                {control.classification || "MANUAL"}
                                                                            </span>

                                                                            {/* 2. Functional Category (Solid Pill) */}
                                                                            <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-bold shadow-sm ${control.category === 'Technical' ? 'bg-purple-100 text-purple-800' :
                                                                                control.category === 'Operational' ? 'bg-green-100 text-green-800' :
                                                                                    control.category === 'People' ? 'bg-pink-100 text-pink-800' :
                                                                                        control.category === 'Legal' ? 'bg-orange-100 text-orange-800' :
                                                                                            'bg-blue-100 text-blue-800' // Governance (Default)
                                                                                }`}>
                                                                                {control.category || "Governance"}
                                                                            </span>
                                                                        </div>
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

                {/* CONTROL DRAWER — Enhanced with AI Requirements, Evidence, Cross-Framework & Policy */}
                {selectedControl && (
                    <EnhancedControlDetail
                        controlId={formatControlId(selectedControl.control_id)}
                        controlData={selectedControl}
                        onClose={() => setSelectedControl(null)}
                    />
                )}
            </div>
        </>
    );
};



export default FrameworkDetail;
