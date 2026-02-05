
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import {
    ArrowLeft, Search, Filter, MoreHorizontal,
    Calendar, CheckCircle, FileText, AlertCircle,
    ChevronDown, Plus, Edit2, X, Upload, ExternalLink, Shield
} from 'lucide-react';

const API_URL = 'https://assurisk-backend.onrender.com/api/v1';

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

    // Additional Criteria
    "A1.1": "Availability: The entity maintains, monitors, and evaluates current processing capacity.",
    "A1.2": "Availability: Data backup and recovery.",
    "C1.1": "Confidentiality: The entity identifies and maintains confidential information.",
    "P1.0": "Privacy: Notice and choice.",
    "P2.0": "Privacy: Collection, use, retention, and disposal.",

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
    const [framework, setFramework] = useState(null);
    const [processes, setProcesses] = useState([]);
    const [socControls, setSocControls] = useState({});
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [stats, setStats] = useState({ total: 0, implemented: 0, percentage: 0 });
    const [searchTerm, setSearchTerm] = useState('');

    // DRAWER STATE
    const [selectedControl, setSelectedControl] = useState(null);

    useEffect(() => {
        fetchData();
    }, [id]);

    const fetchData = async () => {
        try {
            const token = localStorage.getItem('token');
            const headers = { Authorization: `Bearer ${token}` };

            const fwRes = await axios.get(`${API_URL}/frameworks/${id}`, { headers });
            const fwData = fwRes.data;
            const isSOC2 = fwData.code && fwData.code.includes("SOC2");

            const ctrlRes = await axios.get(`${API_URL}/controls/`, { headers });
            const allControls = ctrlRes.data.filter(c => c.framework_id === parseInt(id));

            if (isSOC2) {
                const grouped = {};
                allControls.forEach(c => {
                    const key = c.category || "Uncategorized";
                    if (!grouped[key]) grouped[key] = [];
                    grouped[key].push(c);
                });
                setSocControls(grouped);
                setProcesses([]);
            } else {
                const procRes = await axios.get(`${API_URL}/processes/`, { headers });
                const filteredProcesses = procRes.data.map(proc => {
                    const relevantSubs = proc.sub_processes.map(sub => {
                        return { ...sub, controls: sub.controls || [] };
                    }).filter(sub => sub.controls && sub.controls.length > 0);
                    return { ...proc, sub_processes: relevantSubs };
                }).filter(proc => proc.sub_processes.length > 0);
                setProcesses(filteredProcesses);
            }

            const total = allControls.length;
            const implemented = allControls.filter(c => c.status === 'IMPLEMENTED').length;
            setFramework(fwData);
            setStats({
                total,
                implemented,
                percentage: total > 0 ? Math.round((implemented / total) * 100) : 0
            });
            setLoading(false);

        } catch (err) {
            console.error(err);
            setError(`Failed to load data: ${err.message}`);
            setLoading(false);
        }
    };

    if (loading) return <div className="p-12 text-center text-gray-400">Loading Framework Data...</div>;
    if (error) return <div className="p-12 text-center text-red-500">{error}</div>;

    const isSOC2 = framework?.code?.includes("SOC2");

    const getFilteredControls = (controls) => {
        if (!searchTerm) return controls;
        return controls.filter(c => c.title && c.title.toLowerCase().includes(searchTerm.toLowerCase()));
    };

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

    // NEW LOGIC: Get Specific Requirements
    const getRequirements = (control) => {
        if (!control) return REQUIRED_EVIDENCE_DEFAULTS["DEFAULT"];

        // 1. Try Specific Title Match
        if (control.title && SPECIFIC_EVIDENCE_MAP[control.title]) {
            return SPECIFIC_EVIDENCE_MAP[control.title];
        }
        // 2. Try Category Match
        if (control.category && REQUIRED_EVIDENCE_DEFAULTS[control.category]) {
            return REQUIRED_EVIDENCE_DEFAULTS[control.category];
        }
        // 3. Fallback
        return REQUIRED_EVIDENCE_DEFAULTS["DEFAULT"];
    };

    return (
        <div className="min-h-screen bg-gray-50 pb-20 animate-fade-in relative">
            {/* TOP HEADER */}
            <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
                <div className="max-w-7xl mx-auto px-6 py-4">
                    <div className="flex justify-between items-center mb-4">
                        <div className="flex items-center gap-2 text-sm text-gray-500">
                            <a onClick={() => navigate('/dashboard')} className="hover:text-gray-900 cursor-pointer">DASHBOARD</a>
                            <span>/</span>
                            <span className="font-medium text-gray-900">{framework.code}</span>
                        </div>
                    </div>
                    <div className="flex justify-between items-end">
                        <h1 className="text-3xl font-bold text-gray-900">
                            {framework.name} {isSOC2 && <span className="text-sm font-normal text-blue-600 bg-blue-50 px-2 py-1 rounded-full align-middle">(COSO View)</span>}
                        </h1>
                    </div>
                </div>
            </div>

            <div className="max-w-7xl mx-auto px-6 py-8 space-y-8">
                {/* SEARCH */}
                <div className="flex items-center justify-between">
                    <div className="relative">
                        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                        <input
                            type="text"
                            placeholder="Search controls..."
                            className="pl-9 pr-4 py-2 border border-gray-300 rounded-lg text-sm w-64 focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                    </div>
                </div>

                {/* CONTENT AREA */}
                <div className="space-y-10">
                    {/* SOC 2 SPECIAL VIEW */}
                    {isSOC2 ? (
                        Object.keys(socControls).sort().map(category => {
                            const controls = getFilteredControls(socControls[category]);
                            if (controls.length === 0) return null;
                            const cosoText = COSO_DESCRIPTIONS[category] || COSO_DESCRIPTIONS["DEFAULT"];

                            return (
                                <div key={category} className="mb-8">
                                    <div className="mb-4">
                                        <h2 className="text-xl font-bold text-gray-900">{category}</h2>
                                        <p className="text-gray-600 font-medium text-sm mt-1 border-l-4 border-blue-500 pl-3">
                                            {cosoText}
                                        </p>
                                    </div>
                                    <div className="bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden">
                                        <table className="w-full">
                                            <thead>
                                                <tr className="bg-gray-50 border-b border-gray-200 text-left">
                                                    <th className="px-6 py-3 w-8"><input type="checkbox" className="rounded" /></th>
                                                    <th className="px-6 py-3 text-xs font-bold text-gray-500 uppercase">Control</th>
                                                    <th className="px-6 py-3 text-xs font-bold text-gray-500 uppercase">Evidence Status</th>
                                                    <th className="px-6 py-3 text-xs font-bold text-gray-500 uppercase">Standard Control</th>
                                                    <th className="px-6 py-3 text-xs font-bold text-gray-500 uppercase">Owner</th>
                                                </tr>
                                            </thead>
                                            <tbody className="divide-y divide-gray-100">
                                                {controls.map(c => {
                                                    const evStats = getEvidenceStats(c.control_id);
                                                    return (
                                                        <tr
                                                            key={c.id}
                                                            className="hover:bg-blue-50 transition-colors cursor-pointer group"
                                                            onClick={() => setSelectedControl(c)}
                                                        >
                                                            <td className="px-6 py-4" onClick={e => e.stopPropagation()}><input type="checkbox" className="rounded" /></td>
                                                            <td className="px-6 py-4 font-medium text-gray-900 group-hover:text-blue-700">{c.title}</td>
                                                            <td className="px-6 py-4">
                                                                <div className="flex items-center gap-2">
                                                                    <div className="flex gap-0.5">
                                                                        {[...Array(evStats.total)].map((_, i) => (
                                                                            <div key={i} className={`w-2 h-4 rounded-sm ${i < evStats.uploaded ? 'bg-green-500' : 'bg-gray-200'}`}></div>
                                                                        ))}
                                                                    </div>
                                                                    <span className="text-xs font-medium text-gray-500 ml-1">
                                                                        {evStats.uploaded}/{evStats.total}
                                                                    </span>
                                                                </div>
                                                            </td>
                                                            <td className="px-6 py-4 text-sm text-gray-500 bg-gray-50 font-mono">{category}</td>
                                                            <td className="px-6 py-4 text-sm text-gray-500">System</td>
                                                        </tr>
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
            {selectedControl && (
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
                            </div>
                            <h2 className="text-2xl font-bold text-gray-900 mb-2">{selectedControl.title}</h2>
                            <p className="text-gray-500 text-sm">
                                {COSO_DESCRIPTIONS[selectedControl.category] || selectedControl.description}
                            </p>
                        </div>

                        <div className="p-8 space-y-8 flex-1">

                            {/* STANDARD REQUIREMENTS SECTION */}
                            <div className="bg-blue-50 border border-blue-100 rounded-xl p-5">
                                <h3 className="text-sm font-bold text-blue-900 uppercase tracking-wider mb-4 flex items-center gap-2">
                                    <Shield className="w-5 h-5" /> Standard Requirements
                                </h3>

                                <div className="space-y-3">
                                    {(() => {
                                        const reqs = getRequirements(selectedControl);
                                        const stats = getEvidenceStats(selectedControl.control_id);

                                        return reqs.map((req, idx) => {
                                            const isMet = isRequirementMet(idx, stats.uploaded);
                                            return (
                                                <div key={idx} className="flex items-center justify-between bg-white p-3 rounded-lg border border-blue-100">
                                                    <div className="flex items-center gap-3">
                                                        <div className={`w-5 h-5 rounded-full flex items-center justify-center ${isMet ? 'bg-green-500 text-white' : 'bg-gray-100 border border-gray-300'}`}>
                                                            {isMet && <CheckCircle className="w-3.5 h-3.5" />}
                                                        </div>
                                                        <div>
                                                            <p className={`text-sm font-medium ${isMet ? 'text-gray-900' : 'text-gray-500'}`}>{req.name}</p>
                                                            <p className="text-xs text-blue-500">{req.type}</p>
                                                        </div>
                                                    </div>
                                                    {isMet ?
                                                        <span className="text-xs font-bold text-green-600 bg-green-50 px-2 py-1 rounded">EVIDENCE MET</span> :
                                                        <button className="text-xs font-bold text-orange-600 bg-orange-50 border border-orange-200 px-2 py-1 rounded hover:bg-orange-100">UPLOAD PENDING</button>
                                                    }
                                                </div>
                                            );
                                        });
                                    })()}
                                </div>
                            </div>

                            {/* MISSING EVIDENCE ACTIONS */}
                            <div>
                                <h3 className="text-sm font-bold text-gray-900 uppercase tracking-wider mb-4 flex items-center gap-2">
                                    <AlertCircle className="w-5 h-5 text-orange-500" /> Pending Actions
                                </h3>
                                <div className="bg-white border border-gray-200 rounded-xl divide-y divide-gray-100">
                                    {(() => {
                                        const reqs = getRequirements(selectedControl);
                                        const stats = getEvidenceStats(selectedControl.control_id);
                                        const missing = reqs.filter((_, idx) => !isRequirementMet(idx, stats.uploaded));

                                        if (missing.length === 0) return <div className="p-4 text-sm text-gray-500 italic">No pending actions. All requirements met.</div>;

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
                                                <button className="text-xs font-bold text-blue-600 border border-blue-200 px-3 py-1 rounded hover:bg-blue-50">Upload</button>
                                            </div>
                                        ));
                                    })()}
                                </div>
                            </div>

                        </div>

                        <div className="p-6 border-t border-gray-200 bg-gray-50">
                            <button className="w-full py-3 bg-blue-600 text-white rounded-lg font-bold hover:bg-blue-700 shadow-md">
                                Mark Control as Complete
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default FrameworkDetail;
