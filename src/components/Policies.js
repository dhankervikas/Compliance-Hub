import React, { useState, useEffect } from 'react';
import axios from '../services/api';
import config from '../config';
import { useNavigate } from 'react-router-dom';
import {
    Plus,
    Search,
    MoreHorizontal,
    Loader2
} from 'lucide-react';

const StatusBadge = ({ status }) => {
    // Vanta Style: Dot + Text
    let dotColor = "bg-gray-400";
    let textColor = "text-gray-600";
    let label = status;

    if (status === 'Approved' || status === 'OK') {
        dotColor = "bg-green-500";
        textColor = "text-green-700";
        label = "OK";
    } else if (status === 'Pending Approval') {
        dotColor = "bg-amber-400";
        textColor = "text-amber-700";
    } else {
        // Draft / Not Started
        dotColor = "bg-gray-400";
        textColor = "text-gray-600";
        label = status === "Review" ? "Draft" : status; // Map 'Review' to 'Draft' for UI match
    }

    return (
        <div className={`flex items-center gap-2 px-2 py-1 rounded-full border border-gray-200 bg-white w-fit shadow-sm`}>
            <div className={`w-2 h-2 rounded-full ${dotColor}`} />
            <span className={`text-xs font-semibold ${textColor}`}>{label}</span>
        </div>
    );
};

const StandardsBadge = ({ frameworks }) => {
    if (!frameworks) return <span className="text-gray-400 text-xs">—</span>;

    const list = frameworks.split(',').map(s => s.trim());
    const display = list.slice(0, 2);
    const remainder = list.length - 2;

    return (
        <div className="flex gap-1 flex-wrap">
            {display.map((fw, i) => (
                <span key={i} className="px-2 py-1 bg-white border border-gray-200 rounded text-[10px] font-medium text-gray-600 shadow-sm whitespace-nowrap">
                    {fw}
                </span>
            ))}
            {remainder > 0 && (
                <span className="px-2 py-1 bg-gray-50 border border-gray-200 rounded text-[10px] font-medium text-gray-500 shadow-sm">
                    +{remainder}
                </span>
            )}
        </div>
    );
};

const Policies = ({ readOnly = false }) => {
    const navigate = useNavigate();
    const [policies, setPolicies] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [scopeSettings, setScopeSettings] = useState(null);

    // Template Modal State
    const [showTemplateModal, setShowTemplateModal] = useState(false);
    const [templates, setTemplates] = useState([]);
    const [loadingTemplates, setLoadingTemplates] = useState(false);

    const fetchData = async () => {
        try {
            const [pRes, sRes] = await Promise.all([
                axios.get('/policies/'),
                axios.get(`${config.API_BASE_URL}/settings/scope`).catch(() => ({ data: { content: {} } }))
            ]);
            setPolicies(pRes.data);
            setScopeSettings(sRes.data.content || {});
        } catch (error) {
            console.error("Failed to fetch data", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    const fetchTemplates = async () => {
        setLoadingTemplates(true);
        try {
            const res = await axios.get('/master-templates/');
            setTemplates(res.data);
        } catch (err) {
            console.error("Failed to fetch templates", err);
        } finally {
            setLoadingTemplates(false);
        }
    };

    useEffect(() => {
        if (showTemplateModal) {
            fetchTemplates();
        }
    }, [showTemplateModal]);

    const handleCreateFromTemplate = async (templateId) => {
        try {
            // Updated endpoint to clone master
            const res = await axios.post(`/policies/clone-master/${templateId}`);
            setShowTemplateModal(false);
            navigate(`/policies/${res.data.id}`);
        } catch (error) {
            console.error("Failed to create from template", error);
            alert("Failed to create policy from template.");
        }
    };

    const handleCreateCustom = async () => {
        if (readOnly) return;
        try {
            const res = await axios.post('/policies/', {
                name: `New Custom Policy`,
                content: "# New Policy\n\n## Purpose\nDescribe the purpose...",
                status: "Draft",
                owner: "Compliance",
                version: "0.1"
            });
            navigate(`/policies/${res.data.id}`);
        } catch (error) {
            console.error("Failed to create policy", error);
        }
    };

    const getLastApprovedInfo = (policy) => {
        if (policy.status === 'Approved') {
            const date = new Date(policy.updated_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
            return (
                <div className="flex flex-col">
                    <span className="text-sm font-medium text-gray-900">{date}</span>
                    <span className="text-xs text-gray-500">version {policy.version}</span>
                </div>
            );
        }
        return <span className="text-gray-400">—</span>;
    };

    // Prioritization Logic
    const isPrioritized = (policy) => {
        if (!scopeSettings || !scopeSettings.soc2_selected_principles) return false;
        if (!policy.linked_frameworks) return false;

        // Check for Optional Principles in Linked Frameworks
        const principles = scopeSettings.soc2_selected_principles; // e.g. ["Security", "Availability"]

        // We look for keyword matches in the linked_framework string
        if (principles.includes('Availability') && policy.linked_frameworks.includes('Availability')) return true;
        if (principles.includes('Privacy') && policy.linked_frameworks.includes('Privacy')) return true;
        if (principles.includes('Confidentiality') && policy.linked_frameworks.includes('Confidentiality')) return true;
        if (principles.includes('Processing Integrity') && policy.linked_frameworks.includes('Processing Integrity')) return true;

        return false;
    };

    const filteredPolicies = policies
        .filter(p =>
            p.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
            (p.owner && p.owner.toLowerCase().includes(searchTerm.toLowerCase()))
        )
        .sort((a, b) => {
            // Sort Priority first
            const pA = isPrioritized(a);
            const pB = isPrioritized(b);
            if (pA && !pB) return -1;
            if (!pA && pB) return 1;
            return 0;
        });

    return (
        <div className="space-y-6 h-full p-6 bg-gray-50/50 relative">
            {/* Header */}
            <div className="flex justify-between items-center bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">Policies</h1>
                    <p className="text-sm text-gray-500 mt-1">Manage, edit, and approve your governance documents.</p>
                </div>
                <div className="flex gap-3">
                    {!readOnly && (
                        <>
                            <button
                                onClick={() => setShowTemplateModal(true)}
                                className="px-4 py-2 bg-indigo-50 border border-indigo-100 text-indigo-700 rounded-lg text-sm font-medium hover:bg-indigo-100 shadow-sm flex items-center gap-2"
                            >
                                <Plus className="w-4 h-4" />
                                New from Template
                            </button>
                            <button
                                onClick={handleCreateCustom}
                                className="px-4 py-2 bg-white border border-gray-200 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-50 shadow-sm flex items-center gap-2"
                            >
                                <Plus className="w-4 h-4" />
                                Custom Policy
                            </button>
                        </>
                    )}
                </div>
            </div>

            {/* Filters Bar */}
            <div className="flex gap-4 items-center">
                <div className="relative flex-1 max-w-md">
                    <Search className="absolute left-3 top-2.5 w-4 h-4 text-gray-400" />
                    <input
                        type="text"
                        placeholder="Search by name"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="pl-9 pr-4 py-2 w-full text-sm border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none shadow-sm"
                    />
                </div>

                <div className="h-8 w-px bg-gray-300 mx-2" />

                {/* Active Scope Badges (Visual Only) */}
                {scopeSettings?.soc2_selected_principles?.map(p => (
                    p !== 'Security' && (
                        <span key={p} className="px-2 py-1 bg-orange-50 text-orange-700 rounded text-xs font-bold border border-orange-100 flex items-center gap-1">
                            <Loader2 className="w-3 h-3 animate-spin duration-3000" /> Prioritizing {p}
                        </span>
                    )
                ))}
            </div>

            {/* Policies Table */}
            {loading ? (
                <div className="flex justify-center py-12">
                    <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
                </div>
            ) : (
                <div className="bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden">
                    <table className="w-full text-left">
                        <thead className="bg-gray-50 border-b border-gray-200">
                            <tr>
                                <th className="px-6 py-3 text-xs font-bold text-gray-500 uppercase tracking-wider">Name</th>
                                <th className="px-6 py-3 text-xs font-bold text-gray-500 uppercase tracking-wider">Standards</th>
                                <th className="px-6 py-3 text-xs font-bold text-gray-500 uppercase tracking-wider">Status</th>
                                <th className="px-6 py-3 text-xs font-bold text-gray-500 uppercase tracking-wider">Last Approved Version</th>
                                <th className="px-6 py-3 text-xs font-bold text-gray-500 uppercase tracking-wider text-right"></th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-100">
                            {filteredPolicies.map((policy) => {
                                const active = isPrioritized(policy);
                                return (
                                    <tr
                                        key={policy.id}
                                        onClick={() => navigate(`/policies/${policy.id}`)}
                                        className={`hover:bg-gray-50 transition-colors group cursor-pointer ${active ? 'bg-orange-50/30' : ''}`}
                                    >
                                        <td className="px-6 py-4">
                                            <div className="flex items-center gap-2">
                                                <span className="text-sm font-semibold text-gray-900">{policy.name}</span>
                                                {active && (
                                                    <span className="bg-orange-100 text-orange-700 text-[10px] font-bold px-1.5 py-0.5 rounded border border-orange-200">
                                                        PRIORITY
                                                    </span>
                                                )}
                                            </div>
                                        </td>
                                        <td className="px-6 py-4">
                                            <StandardsBadge frameworks={policy.linked_frameworks} />
                                        </td>
                                        <td className="px-6 py-4">
                                            <StatusBadge status={policy.status} />
                                        </td>
                                        <td className="px-6 py-4">
                                            {getLastApprovedInfo(policy)}
                                        </td>
                                        <td className="px-6 py-4 text-right">
                                            {policy.status !== 'Approved' ? (
                                                <button className="px-3 py-1.5 bg-white border border-gray-200 rounded text-xs font-medium text-gray-700 hover:bg-gray-50 shadow-sm mr-2" onClick={(e) => { e.stopPropagation(); navigate(`/policies/${policy.id}`) }}>
                                                    Start
                                                </button>
                                            ) : (
                                                <button className="p-1 hover:bg-gray-200 rounded-full text-gray-400">
                                                    <MoreHorizontal className="w-5 h-5" />
                                                </button>
                                            )}
                                        </td>
                                    </tr>
                                )
                            })}
                        </tbody>
                    </table>
                    {filteredPolicies.length === 0 && (
                        <div className="px-6 py-12 text-center text-gray-500">
                            No policies found.
                        </div>
                    )}
                </div>
            )}

            {/* Template Selection Modal */}
            {showTemplateModal && (
                <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
                    <div className="bg-white rounded-xl shadow-xl w-full max-w-2xl max-h-[80vh] flex flex-col">
                        <div className="p-6 border-b border-gray-200 flex justify-between items-center">
                            <h2 className="text-xl font-bold text-gray-900">Select a Template</h2>
                            <button onClick={() => setShowTemplateModal(false)} className="text-gray-400 hover:text-gray-600">
                                <Plus className="w-6 h-6 rotate-45" />
                            </button>
                        </div>
                        <div className="p-6 overflow-y-auto flex-1">
                            {loadingTemplates ? (
                                <div className="flex justify-center py-12">
                                    <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
                                </div>
                            ) : (
                                <div className="grid gap-3">
                                    {templates.map(tmpl => (
                                        <button
                                            key={tmpl.id}
                                            onClick={() => handleCreateFromTemplate(tmpl.id)}
                                            className="text-left p-4 border border-gray-200 rounded-lg hover:border-indigo-500 hover:bg-indigo-50 transition-all group"
                                        >
                                            <div className="flex justify-between items-start">
                                                <span className="font-semibold text-gray-900 group-hover:text-indigo-700">{tmpl.title}</span>
                                                <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">{tmpl.original_filename}</span>
                                            </div>
                                            <p className="text-sm text-gray-500 mt-1">master_id: {tmpl.id} | control_id: {tmpl.control_id || 'N/A'}</p>
                                        </button>
                                    ))}
                                    {templates.length === 0 && <p className="text-center text-gray-500 py-4">No master templates found.</p>}
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Policies;
