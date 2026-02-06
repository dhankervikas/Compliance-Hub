import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
    ChevronRight, ChevronDown, CheckCircle, UserPlus, Server, Upload, FileText, Zap, Link
} from 'lucide-react';
import config from '../config';

const API_URL = config.API_BASE_URL;

// --- UTILS ---
const escapeRegExp = (string) => {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
};

const highlightText = (text, query) => {
    if (!query || !text) return text;
    try {
        const parts = text.split(new RegExp(`(${escapeRegExp(query)})`, 'gi'));
        return parts.map((part, i) =>
            part.toLowerCase() === query.toLowerCase()
                ? `<span key="${i}" class="bg-yellow-100 text-yellow-800 font-bold px-1 rounded">${part}</span>`
                : part
        ).join('');
    } catch (e) {
        return text;
    }
};

const getInitials = (name) => {
    if (!name) return "?";
    return name.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase();
};

const getCategoryColor = (category) => {
    const map = {
        'Governance & Policy': 'bg-blue-500',
        'Asset Management': 'bg-indigo-500',
        'Access Control (IAM)': 'bg-purple-500',
        'Risk Management': 'bg-orange-500',
        'Operations (General)': 'bg-emerald-500',
        'Physical Security': 'bg-slate-500',
        'Legal & Compliance': 'bg-red-500',
        'Human Resources': 'bg-pink-500',
    };
    return map[category] || 'bg-gray-400';
};

// --- COMPONENTS ---

// 1. Evidence Micro-Bar (High Fidelity)
const EvidenceMicroBar = ({ count = 0, total = 4, hasSynced = false }) => {
    const percentage = Math.min((count / total) * 100, 100);
    return (
        <div className="flex flex-col justify-center w-24 space-y-1.5 cursor-help group/evidence relative">
            <div className="flex justify-between items-end">
                <span className="text-xs font-bold text-gray-700 bg-gray-100 px-1.5 rounded-sm group-hover/evidence:bg-blue-100 group-hover/evidence:text-blue-700 transition-colors flex items-center gap-1">
                    {count}/{total} Tests
                    {hasSynced && (
                        <Link className="w-3 h-3 text-blue-500" />
                    )}
                </span>
            </div>
            <div className="h-2 w-full bg-gray-100 rounded-full overflow-hidden">
                <div
                    className={`h-full rounded-full transition-all duration-500 ${percentage === 100 ? 'bg-emerald-500' : 'bg-blue-500'}`}
                    style={{ width: `${percentage}%` }}
                />
            </div>
        </div>
    );
};

// 2. Status Indicator (Vanta Style: Check or 4-Dots)
const StatusIndicator = ({ status }) => {
    if (status === 'implemented') {
        return (
            <div className="flex items-center space-x-2" title="Compliant">
                <CheckCircle className="w-4 h-4 text-emerald-500 fill-emerald-50" />
                <span className="text-xs font-semibold text-emerald-700">Compliant</span>
            </div>
        );
    }

    // 4-Dot Indicator for Non-Compliant Items
    // In Progress = 1 dot amber? Not Started = 0 dots (4 gray)?
    // User said "4-dot progress indicator".
    const filled = status === 'in_progress' ? 1 : 0;

    return (
        <div className="flex items-center space-x-3" title={status === 'in_progress' ? 'Partial' : 'Not Started'}>
            <div className="flex space-x-1">
                {[1, 2, 3, 4].map(i => (
                    <div
                        key={i}
                        className={`w-2 h-2 rounded-full transition-colors ${i <= filled ? 'bg-amber-400' : 'bg-gray-200'}`}
                    />
                ))}
            </div>
        </div>
    );
};

// Ref Badge Component
const RefBadge = ({ id }) => {
    if (!id) return null;
    const strId = id.toString();
    // Logic: Strictly use the ID from the database. 
    // The backend now guarantees "A.5.x" for Annex A and "4.x" for Clauses.
    const displayId = strId;

    return (
        <span className="inline-flex items-center px-2 py-1 rounded font-bold bg-gray-100 text-sm text-gray-500 tracking-wide border border-gray-200 select-all mr-2">
            {displayId}
        </span>
    );
};

// 3. Automation Tag
const AutomationTag = ({ type }) => {
    const isSystem = type === 'system';
    return (
        <div className={`
            flex items-center space-x-1.5 px-2 py-1 rounded-md border border-dashed transition-all cursor-pointer hover:shadow-sm
            ${isSystem
                ? 'bg-purple-50 border-purple-200 text-purple-700 hover:bg-purple-100'
                : 'bg-blue-50 border-blue-200 text-blue-700 hover:bg-blue-100'
            }
        `}>
            {isSystem ? <Server className="w-3 h-3" /> : <UserPlus className="w-3 h-3" />}
            <span className="text-xs font-bold uppercase tracking-wider">
                {isSystem ? 'System' : 'Manual'}
            </span>
        </div>
    );
};

// 4. Owner Avatar (Interactive)
const OwnerAvatar = ({ assignee }) => {
    if (!assignee) {
        return (
            <div className="w-7 h-7 rounded-full bg-gray-50 border border-gray-200 border-dashed flex items-center justify-center text-gray-300 hover:border-gray-400 hover:text-gray-500 transition-all cursor-pointer">
                <span className="text-[10px] font-bold">+</span>
            </div>
        );
    }
    return (
        <div
            className="w-7 h-7 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 text-white flex items-center justify-center text-[10px] font-bold shadow-sm cursor-pointer hover:ring-2 hover:ring-offset-1 hover:ring-blue-500 transition-all"
            title={assignee.name}
        >
            {assignee.initials}
        </div>
    );
};

// --- MAIN COMPONENT ---

const UserProcessView = ({ framework, onSelectControl, filters }) => {
    const [processes, setProcesses] = useState([]);
    const [loading, setLoading] = useState(true);
    const [expandedProcesses, setExpandedProcesses] = useState([]);
    const [selectedControls, setSelectedControls] = useState(new Set());

    // ACTION STATE
    const [users, setUsers] = useState([]);
    const [showAssignModal, setShowAssignModal] = useState(false);
    const [selectedOwner, setSelectedOwner] = useState("");
    const [loadingAction, setLoadingAction] = useState(false);

    // Fetch Users
    useEffect(() => {
        fetchUsers();
    }, []);

    const fetchUsers = async () => {
        try {
            const token = localStorage.getItem('token');
            if (!token) return; // Prevent crash if no token
            const res = await axios.get(`${API_URL}/users/`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setUsers(res.data);
        } catch (err) {
            console.error("Failed to load users", err);
        }
    };

    const handleBulkAssign = async () => {
        if (!selectedOwner) return;
        setLoadingAction(true);
        try {
            const token = localStorage.getItem('token');
            await axios.post(`${API_URL}/controls/bulk/owner`, {
                control_ids: Array.from(selectedControls),
                owner_id: selectedOwner
            }, { headers: { Authorization: `Bearer ${token}` } });

            await fetchProcesses();
            setShowAssignModal(false);
            setSelectedControls(new Set());
            setSelectedOwner("");
        } catch (err) {
            alert("Assignment Failed: " + err.message);
        } finally {
            setLoadingAction(false);
        }
    };

    const handleBulkStatus = async (status) => {
        if (!window.confirm(`Mark ${selectedControls.size} controls as ${status === 'implemented' ? 'Complete' : 'In Progress'}?`)) return;
        setLoadingAction(true);
        try {
            const token = localStorage.getItem('token');
            await axios.post(`${API_URL}/controls/bulk/status`, {
                control_ids: Array.from(selectedControls),
                status: status,
                is_applicable: true
            }, { headers: { Authorization: `Bearer ${token}` } });

            await fetchProcesses();
            setSelectedControls(new Set());
        } catch (err) {
            alert("Update Failed");
        } finally {
            setLoadingAction(false);
        }
    };

    // Fetch Data
    useEffect(() => {
        fetchProcesses();
    }, [framework]);

    // Auto-expand
    useEffect(() => {
        if (processes.length > 0) {
            setExpandedProcesses(processes.map(p => p.id));
        }
    }, [processes]);

    const fetchProcesses = async () => {
        if (!framework) return;
        try {
            setLoading(true);
            const token = localStorage.getItem('token');
            if (!token) return;

            let code = framework.code === 'ISO 27001:2022' ? 'ISO27001' : framework.code;
            const res = await axios.get(`${API_URL}/processes/`, {
                headers: { Authorization: `Bearer ${token}` },
                params: { framework_code: code }
            });
            setProcesses(Array.isArray(res.data) ? res.data : []);
            setLoading(false);
        } catch (err) {
            console.error("Failed to fetch processes:", err);
            setLoading(false);
        }
    };

    const getFilteredControls = (subProcess) => {
        if (!subProcess.controls) return [];
        let controls = subProcess.controls.filter(c => c.framework_id == framework.id);

        if (filters?.status && filters.status !== 'All') {
            const filterStatus = filters.status.toLowerCase().replace(' ', '_');
            controls = controls.filter(c => c.status === filterStatus);
        }

        if (filters?.owner && filters.owner !== 'All') {
            if (filters.owner === 'Unassigned') {
                controls = controls.filter(c => !c.assignee);
            } else {
                controls = controls.filter(c => c.assignee?.name === filters.owner);
            }
        }
        return controls;
    };

    const toggleSelection = (controlId) => {
        setSelectedControls(prev => {
            const next = new Set(prev);
            if (next.has(controlId)) next.delete(controlId);
            else next.add(controlId);
            return next;
        });
    };

    const toggleProcess = (pid) => {
        setExpandedProcesses(prev => prev.includes(pid) ? prev.filter(id => id !== pid) : [...prev, pid]);
    };

    if (loading) return <div className="p-12 text-center text-gray-400">Loading...</div>;

    const query = filters?.search || '';

    // --- RENDER ---
    return (
        <div className="space-y-6 pb-20 bg-gray-50 min-h-screen">
            {processes.map(process => {
                const subProcesses = process.sub_processes || [];
                let allProcessControls = subProcesses.flatMap(sp => getFilteredControls(sp));

                // Deduplicate for View
                const uniqueControls = [];
                const seenIds = new Set();
                for (const c of allProcessControls) {
                    if (!seenIds.has(c.control_id)) {
                        seenIds.add(c.control_id);
                        uniqueControls.push(c);
                    }
                }

                // Sort (Clauses First)
                uniqueControls.sort((a, b) => {
                    // Numeric-first custom sort logic
                    const idA = (a.control_id || "").trim();
                    const idB = (b.control_id || "").trim();
                    const isClauseA = /^\d/.test(idA);
                    const isClauseB = /^\d/.test(idB);
                    if (isClauseA && !isClauseB) return -1;
                    if (!isClauseA && isClauseB) return 1;
                    const cleanA = idA.replace(/^[A-Za-z]+\./, '');
                    const cleanB = idB.replace(/^[A-Za-z]+\./, '');
                    const partsA = cleanA.split('.').map(x => parseInt(x, 10));
                    const partsB = cleanB.split('.').map(x => parseInt(x, 10));
                    const len = Math.max(partsA.length, partsB.length);
                    for (let i = 0; i < len; i++) {
                        const valA = partsA[i] !== undefined ? partsA[i] : 0;
                        const valB = partsB[i] !== undefined ? partsB[i] : 0;
                        if (valA !== valB) return valA - valB;
                    }
                    return idA.localeCompare(idB);
                });

                const displayed = query ? uniqueControls.filter(c =>
                    c.title.toLowerCase().includes(query.toLowerCase()) ||
                    c.control_id.toLowerCase().includes(query.toLowerCase()) ||
                    c.actionable_title?.toLowerCase().includes(query.toLowerCase())
                ) : uniqueControls;

                if (displayed.length === 0) return null;

                const isExpanded = expandedProcesses.includes(process.id);

                return (
                    <div key={process.id} className="group">
                        {/* HEADER */}
                        <div
                            className="flex items-center space-x-2 mb-3 cursor-pointer select-none px-2"
                            onClick={() => toggleProcess(process.id)}
                        >
                            <div className={`p-1 rounded text-gray-400 hover:text-gray-900 transition-colors`}>
                                {isExpanded ? <ChevronDown className="w-5 h-5" /> : <ChevronRight className="w-5 h-5" />}
                            </div>
                            <h3 className="text-lg font-bold text-gray-900 tracking-tight">{process.name}</h3>
                            <span className="text-xs font-medium text-gray-500 bg-gray-200 px-2 py-0.5 rounded-full">
                                {displayed.length}
                            </span>
                        </div>

                        {/* LIST */}
                        {isExpanded && (
                            <div className="bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden mb-8 mx-2">
                                {/* LIST HEADER */}
                                <div className="grid grid-cols-12 gap-6 bg-gray-50/50 px-6 py-3 border-b border-gray-100 text-xs font-bold text-gray-400 uppercase tracking-wider">
                                    <div className="col-span-6 pl-12 text-left">CONTROL</div>
                                    <div className="col-span-2 text-left pl-4">EVIDENCE STATUS</div>
                                    <div className="col-span-1 text-center">STANDARD CONTROL</div>
                                    <div className="col-span-1 text-center">OWNER</div>
                                    <div className="col-span-2 text-right pr-4">CATEGORY</div>
                                </div>

                                {displayed.map(control => {
                                    const isSelected = selectedControls.has(control.id);
                                    const evidenceCount = Math.min(control.shared_evidence_count, 4);
                                    const categoryColor = getCategoryColor(control.category || process.name);

                                    return (
                                        <div
                                            key={control.id}
                                            className={`
                                                relative grid grid-cols-12 gap-6 items-center py-4 px-6 border-b border-gray-100 last:border-0 group/row hover:bg-gray-50 transition-colors 
                                                ${isSelected ? 'bg-blue-50/50' : ''}
                                            `}
                                        >
                                            {/* STRIPE (Category) */}
                                            <div className={`absolute left-0 top-0 bottom-0 w-1 ${categoryColor}`} />

                                            {/* CHECKBOX */}
                                            <div className="absolute left-6 top-1/2 -translate-y-1/2">
                                                <input
                                                    type="checkbox"
                                                    checked={isSelected}
                                                    onChange={() => toggleSelection(control.id)}
                                                    className="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
                                                />
                                            </div>

                                            {/* TITLE & SUBTEXT (Col 1-6) */}
                                            <div
                                                className="col-span-6 pl-12 pr-4 cursor-pointer"
                                                onClick={() => onSelectControl(control)}
                                            >
                                                <div className="flex flex-col space-y-1">
                                                    <span
                                                        className="text-xl font-bold text-gray-900 leading-snug group-hover/row:text-blue-700 transition-colors"
                                                        dangerouslySetInnerHTML={{ __html: highlightText(control.title, query) }}
                                                    />
                                                    <div className="flex items-center space-x-2">
                                                        <span className="text-base text-gray-500 font-medium">{control.description}</span>
                                                    </div>
                                                </div>
                                            </div>

                                            {/* EVIDENCE STATUS (Col 7-8) */}
                                            <div className="col-span-2 flex justify-start items-center pl-4">
                                                {evidenceCount === 0 ? (
                                                    <div className="flex items-center space-x-2 opacity-50">
                                                        <div className="flex space-x-1">
                                                            {[1, 2, 3, 4].map(i => <div key={i} className="w-1.5 h-3 bg-gray-300 rounded-full" />)}
                                                        </div>
                                                        <span className="text-xs text-gray-400 font-mono">0/2</span>
                                                    </div>
                                                ) : (
                                                    <div className="flex items-center space-x-2">
                                                        <EvidenceMicroBar count={evidenceCount} total={4} hasSynced={control.has_synced_evidence} />
                                                        <span className="text-xs text-gray-500 font-mono">{evidenceCount}/4</span>
                                                    </div>
                                                )}
                                            </div>

                                            {/* STANDARD CONTROL (Col 9) */}
                                            <div className="col-span-1 flex justify-center items-start pt-1">
                                                <RefBadge id={control.control_id} />
                                            </div>

                                            {/* OWNER (Col 10) */}
                                            <div className="col-span-1 flex justify-center z-10">
                                                <div className="bg-gray-100 text-gray-600 text-xs font-bold px-3 py-1.5 rounded">System</div>
                                            </div>

                                            {/* CATEGORY (Col 11-12) */}
                                            <div className="col-span-2 flex flex-col items-end justify-center pr-4 space-y-1">
                                                <AutomationTag type={control.automation_status} />
                                                <span className="text-[10px] text-gray-400 bg-gray-100 px-2 py-0.5 rounded-full truncate max-w-full">
                                                    {control.category || 'Gov'}
                                                </span>
                                            </div>

                                            {/* HOVER ACTIONS (FLOATING) */}
                                            <div className="absolute right-4 top-1/2 -translate-y-1/2 flex items-center space-x-2 opacity-0 group-hover/row:opacity-100 transition-all translate-x-4 group-hover/row:translate-x-0 bg-white/90 backdrop-blur-sm p-1 rounded-lg border border-gray-100 shadow-lg">
                                                <button
                                                    onClick={() => onSelectControl(control)}
                                                    className="p-1.5 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-md"
                                                    title="View Details"
                                                >
                                                    <FileText className="w-4 h-4" />
                                                </button>
                                                <button
                                                    onClick={() => onSelectControl(control)} // Ideally open distinct tab
                                                    className="p-1.5 text-gray-500 hover:text-emerald-600 hover:bg-emerald-50 rounded-md"
                                                    title="Upload Evidence"
                                                >
                                                    <Upload className="w-4 h-4" />
                                                </button>
                                                <button
                                                    className="p-1.5 text-gray-500 hover:text-purple-600 hover:bg-purple-50 rounded-md"
                                                    title="Run Tests"
                                                >
                                                    <Zap className="w-4 h-4" />
                                                </button>
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        )}
                    </div>
                );
            })}

            {/* FLOATING BULK ACTION BAR (Unchanged) */}
            {selectedControls.size > 0 && (
                <div className="fixed bottom-8 left-1/2 transform -translate-x-1/2 bg-gray-900 text-white px-6 py-3 rounded-xl shadow-2xl flex items-center space-x-6 z-50 animate-in slide-in-from-bottom-5">
                    <div className="font-bold text-white border-r border-gray-700 pr-6">
                        {selectedControls.size} Selected
                    </div>
                    <div className="flex space-x-2">
                        <button
                            onClick={() => setShowAssignModal(true)}
                            className="px-3 py-1.5 hover:bg-gray-700 rounded text-sm font-medium transition flex items-center space-x-2"
                        >
                            <UserPlus className="w-4 h-4 opacity-70" />
                            <span>Assign</span>
                        </button>
                        <button
                            onClick={() => handleBulkStatus('implemented')}
                            className="px-3 py-1.5 hover:bg-gray-700 rounded text-sm font-medium transition flex items-center space-x-2"
                        >
                            <CheckCircle className="w-4 h-4 opacity-70" />
                            <span>Mark Complete</span>
                        </button>
                    </div>
                    <button
                        onClick={() => setSelectedControls(new Set())}
                        className="ml-2 text-gray-400 hover:text-white"
                    >
                        ✕
                    </button>
                </div>
            )}

            {/* ASSIGN MODAL (Unchanged) */}
            {showAssignModal && (
                <div className="fixed inset-0 bg-black/50 z-[100] flex items-center justify-center p-4 animate-in fade-in">
                    <div className="bg-white rounded-xl shadow-2xl max-w-sm w-full p-6 space-y-4">
                        <h3 className="text-lg font-bold text-gray-900">Assign Owner</h3>
                        <p className="text-sm text-gray-500">
                            Assigning <strong>{selectedControls.size}</strong> controls.
                        </p>
                        <div className="space-y-2">
                            <label className="text-xs font-bold text-gray-500 uppercase">Select User</label>
                            <select
                                value={selectedOwner}
                                onChange={(e) => setSelectedOwner(e.target.value)}
                                className="w-full border border-gray-300 rounded-lg p-2.5 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
                            >
                                <option value="">-- Choose User --</option>
                                {users.map(u => (
                                    <option key={u.id} value={u.id}>{u.username} ({u.email})</option>
                                ))}
                            </select>
                        </div>
                        <div className="flex justify-end gap-2 pt-2">
                            <button onClick={() => setShowAssignModal(false)} className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg text-sm font-medium">Cancel</button>
                            <button onClick={handleBulkAssign} disabled={!selectedOwner || loadingAction} className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-bold hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2">
                                {loadingAction && <div className="w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin" />}
                                Confirm Assignment
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default UserProcessView;
