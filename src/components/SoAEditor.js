
import React, { useState, useEffect, useMemo } from 'react';
import axios from 'axios';
import {
    Save, Search, Wand2,
    Edit3, CheckSquare, XSquare
} from 'lucide-react';
import config from '../config';

const API_URL = config.API_BASE_URL;

const REASONS_FOR_INCLUSION = [
    "Legal/Regulatory Requirement",
    "Risk Treatment",
    "Contractual Obligation",
    "Business Requirement"
];

const SoAEditor = () => {
    const [controls, setControls] = useState([]);
    const [loading, setLoading] = useState(false);
    const [saving, setSaving] = useState(false);
    const [aiThinking, setAiThinking] = useState(null);
    const [isEditing, setIsEditing] = useState(false);
    const [searchText, setSearchText] = useState("");

    useEffect(() => {
        fetchControls();
    }, []);

    const fetchControls = async () => {
        setLoading(true);
        try {
            // Mock or Real API
            // For now we assume we fetch the full list of controls for the framework
            const res = await axios.get(`${API_URL}/controls?framework_id=1`);
            // Filter strict Annex A
            const annexControls = res.data.filter(c => c.control_id.startsWith('A.'));

            // Deduplicate
            const uniqueControls = Array.from(new Map(annexControls.map(item => [item.control_id, item])).values());

            // Natural Sort
            uniqueControls.sort((a, b) =>
                a.control_id.localeCompare(b.control_id, undefined, { numeric: true, sensitivity: 'base' })
            );

            setControls(uniqueControls);
        } catch (err) {
            console.error("Failed to load controls", err);
        } finally {
            setLoading(false);
        }
    };

    const handleChange = (id, field, value) => {
        setControls(prev => prev.map(c =>
            c.control_id === id ? { ...c, [field]: value } : c
        ));
    };

    const handleReasonChange = (id, reason, checked) => {
        setControls(prev => prev.map(c => {
            if (c.control_id !== id) return c;

            let currentReasons = c.justification_reason ? c.justification_reason.split(', ').filter(r => r) : [];

            if (checked) {
                if (!currentReasons.includes(reason)) currentReasons.push(reason);
            } else {
                currentReasons = currentReasons.filter(r => r !== reason);
            }
            return { ...c, justification_reason: currentReasons.join(', ') };
        }));
    };

    const handleToggle = (id, currentVal) => {
        if (!isEditing) return;
        const newVal = !currentVal;
        setControls(prev => prev.map(c => {
            if (c.control_id !== id) return c;
            return {
                ...c,
                is_applicable: newVal,
            };
        }));
    };

    const handleBulkApplicability = (isApplicable) => {
        // eslint-disable-next-line no-restricted-globals
        if (!window.confirm(`Are you sure you want to mark ALL filtered controls as ${isApplicable ? 'Applicable' : 'Excluded'}?`)) return;

        const filteredIds = new Set(filteredControls.map(c => c.control_id));

        setControls(prev => prev.map(c =>
            filteredIds.has(c.control_id) ? { ...c, is_applicable: isApplicable } : c
        ));
    };

    const handleAiSuggest = async (control) => {
        setAiThinking(control.control_id);
        try {
            const token = localStorage.getItem('token');
            const res = await axios.post(`${API_URL}/ai/suggest-justification`, {
                control_id: control.control_id,
                title: control.title,
                category: control.is_applicable ? "Inclusion" : "Exclusion",
                scope_description: "Standard ISO 27001 Scope"
            }, {
                headers: { Authorization: `Bearer ${token}` }
            });

            handleChange(control.control_id, 'justification', res.data.justification);
        } catch (err) {
            alert("AI Generation Failed");
        } finally {
            setAiThinking(null);
        }
    };

    const handleSave = async () => {
        setSaving(true);
        try {
            const token = localStorage.getItem('token');
            const updates = controls.map(c => ({
                control_id: c.control_id,
                is_applicable: c.is_applicable,
                justification: c.justification,
                justification_reason: c.is_applicable ? c.justification_reason : "Not Applicable",
                implementation_method: c.implementation_method
            }));

            await axios.post(`${API_URL}/controls/soa-update`, updates, {
                headers: { Authorization: `Bearer ${token}` }
            });
            alert("SoA Configuration Saved Successfully!");
            setIsEditing(false);
        } catch (err) {
            console.error(err);
            alert("Failed to save configuration");
        } finally {
            setSaving(false);
        }
    };

    const filteredControls = useMemo(() => {
        if (!searchText) return controls;
        const lowerSearch = searchText.toLowerCase();
        return controls.filter(c =>
            c.control_id.toLowerCase().includes(lowerSearch) ||
            c.title.toLowerCase().includes(lowerSearch)
        );
    }, [controls, searchText]);

    const groupedControls = useMemo(() => {
        return filteredControls.reduce((acc, ctrl) => {
            const theme = ctrl.control_id.split('.')[1] || 'General';
            const key = `A.${theme}`;
            if (!acc[key]) acc[key] = [];
            acc[key].push(ctrl);
            return acc;
        }, {});
    }, [filteredControls]);

    return (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 flex flex-col h-full">
            {/* Header Toolbar */}
            <div className="p-4 border-b border-gray-200 bg-gray-50 flex flex-col md:flex-row justify-between items-center gap-4 sticky top-0 z-10">
                <div className="flex items-center gap-4 w-full md:w-auto">
                    <div>
                        <h2 className="text-lg font-bold text-gray-900">SoA Configuration</h2>
                        <span className="text-xs text-gray-500">
                            {filteredControls.length} Controls Visible
                        </span>
                    </div>
                </div>

                <div className="flex items-center gap-3 w-full md:w-auto">
                    {/* Search */}
                    <div className="relative flex-1 md:w-64">
                        <Search className="absolute left-3 top-2.5 text-gray-400" size={16} />
                        <input
                            type="text"
                            placeholder="Search controls..."
                            className="w-full pl-9 pr-4 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                            value={searchText}
                            onChange={(e) => setSearchText(e.target.value)}
                        />
                    </div>

                    {/* Edit Mode Toggle */}
                    {!isEditing ? (
                        <button
                            onClick={() => setIsEditing(true)}
                            className="bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-lg font-bold flex items-center gap-2 hover:bg-gray-50"
                        >
                            <Edit3 size={16} /> Edit
                        </button>
                    ) : (
                        <>
                            <div className="flex bg-white rounded-lg border border-gray-300 overflow-hidden">
                                <button
                                    onClick={() => handleBulkApplicability(true)}
                                    className="px-3 py-2 border-r border-gray-300 hover:bg-gray-50 text-green-600"
                                    title="Mark All Visible as Applicable"
                                >
                                    <CheckSquare size={16} />
                                </button>
                                <button
                                    onClick={() => handleBulkApplicability(false)}
                                    className="px-3 py-2 hover:bg-gray-50 text-red-500"
                                    title="Mark All Visible as Excluded"
                                >
                                    <XSquare size={16} />
                                </button>
                            </div>

                            <button
                                onClick={handleSave}
                                disabled={saving}
                                className="bg-blue-600 text-white px-6 py-2 rounded-lg font-bold flex items-center gap-2 hover:bg-blue-700 disabled:opacity-50"
                            >
                                <Save size={16} />
                                {saving ? "Saving..." : "Save"}
                            </button>
                        </>
                    )}
                </div>
            </div>

            {/* Content */}
            {loading ? <div className="p-10 text-center text-gray-500">Loading Controls...</div> : (
                <div className="p-6 space-y-8 overflow-y-auto max-h-[calc(100vh-250px)]">
                    {Object.entries(groupedControls).sort().map(([theme, items]) => (
                        <div key={theme} className="border border-gray-200 rounded-lg overflow-hidden">
                            <div className="bg-gray-100 px-4 py-2 font-bold text-gray-700 uppercase text-xs tracking-wider flex justify-between items-center">
                                <span>Annex {theme}</span>
                                <span className="bg-white px-2 py-0.5 rounded text-gray-500 border border-gray-200">{items.length}</span>
                            </div>
                            <div className="divide-y divide-gray-100">
                                {items.map(ctrl => {
                                    const isExcluded = ctrl.is_applicable === false;
                                    const currentReasons = ctrl.justification_reason ? ctrl.justification_reason.split(', ') : [];

                                    return (
                                        <div key={ctrl.id} className={`p-6 transition-colors ${isExcluded ? 'bg-red-50/30' : 'bg-white'}`}>

                                            {/* Top Row: ID, Title, Applicability */}
                                            <div className="flex justify-between items-start mb-4">
                                                <div className="flex gap-4 items-center">
                                                    <span className="font-mono font-bold text-blue-900 bg-blue-50 px-2 py-1 rounded text-sm min-w-[3.5rem] text-center">
                                                        {ctrl.control_id}
                                                    </span>
                                                    <div>
                                                        <h3 className="font-medium text-gray-900">{ctrl.title}</h3>
                                                        <p className="text-sm text-gray-500 mt-1 line-clamp-1">{ctrl.description}</p>
                                                    </div>
                                                </div>
                                                <div className="flex items-center gap-3 shrink-0">
                                                    <span className={`text-xs font-bold uppercase tracking-wider ${!isExcluded ? 'text-green-600' : 'text-red-500'}`}>
                                                        {!isExcluded ? 'Applicable' : 'Excluded'}
                                                    </span>
                                                    {isEditing ? (
                                                        <button
                                                            onClick={() => handleToggle(ctrl.control_id, ctrl.is_applicable)}
                                                            className={`w-12 h-6 rounded-full p-1 transition-colors focus:outline-none focus:ring-2 focus:ring-offset-1 focus:ring-blue-500 ${!isExcluded ? 'bg-green-500' : 'bg-gray-300'}`}
                                                        >
                                                            <div className={`w-4 h-4 bg-white rounded-full shadow-sm transform transition-transform ${!isExcluded ? 'translate-x-6' : ''}`} />
                                                        </button>
                                                    ) : (
                                                        <div className={`w-3 h-3 rounded-full ${!isExcluded ? 'bg-green-500' : 'bg-red-500'}`} />
                                                    )}
                                                </div>
                                            </div>

                                            {/* Logic Section */}
                                            {(!isExcluded) ? (
                                                /* APPLICABLE LAYOUT */
                                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-4 pl-16">
                                                    {/* Reasons Checkboxes */}
                                                    <div className="space-y-2">
                                                        <label className="block text-xs font-bold text-gray-500 uppercase">
                                                            Reason for Inclusion
                                                        </label>
                                                        <div className="grid grid-cols-2 gap-2">
                                                            {REASONS_FOR_INCLUSION.map(reason => {
                                                                const isChecked = currentReasons.includes(reason);
                                                                return (
                                                                    <label key={reason} className={`flex items-center space-x-2 p-2 rounded border text-sm cursor-pointer transition-all ${isChecked ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:bg-gray-50'}`}>
                                                                        <input
                                                                            type="checkbox"
                                                                            disabled={!isEditing}
                                                                            checked={isChecked}
                                                                            onChange={(e) => handleReasonChange(ctrl.control_id, reason, e.target.checked)}
                                                                            className="rounded text-blue-600 focus:ring-blue-500"
                                                                        />
                                                                        <span className={isChecked ? 'text-blue-900 font-medium' : 'text-gray-600'}>{reason}</span>
                                                                    </label>
                                                                );
                                                            })}
                                                        </div>
                                                    </div>

                                                    {/* Implementation Method */}
                                                    <div>
                                                        <label className="block text-xs font-bold text-gray-500 uppercase mb-2">
                                                            Implementation Method
                                                        </label>
                                                        {isEditing ? (
                                                            <textarea
                                                                className="w-full border border-gray-300 rounded-lg p-2.5 text-sm focus:ring-2 focus:ring-blue-500 h-24 resize-none"
                                                                placeholder="Describe policy, procedure, or technology..."
                                                                value={ctrl.implementation_method || ''}
                                                                onChange={(e) => handleChange(ctrl.control_id, 'implementation_method', e.target.value)}
                                                            />
                                                        ) : (
                                                            <div className="bg-gray-50 p-3 rounded-lg text-sm text-gray-700 min-h-[6rem] border border-gray-100">
                                                                {ctrl.implementation_method || <span className="text-gray-400 italic">No implementation method defined.</span>}
                                                            </div>
                                                        )}
                                                    </div>
                                                </div>
                                            ) : (
                                                /* EXCLUDED LAYOUT */
                                                <div className="mt-4 pl-16">
                                                    <label className="block text-xs font-bold text-gray-500 uppercase mb-2 flex justify-between items-center">
                                                        <span>Justification for Exclusion</span>
                                                        {isEditing && (
                                                            <button
                                                                onClick={() => handleAiSuggest(ctrl)}
                                                                className="text-purple-600 hover:text-purple-700 flex items-center gap-1 text-[10px] uppercase font-bold bg-purple-50 px-2 py-1 rounded-full"
                                                            >
                                                                {aiThinking === ctrl.control_id ? "Thinking..." : <><Wand2 size={12} /> Auto-Draft with AI</>}
                                                            </button>
                                                        )}
                                                    </label>
                                                    {isEditing ? (
                                                        <textarea
                                                            className="w-full border border-red-200 rounded-lg p-3 text-sm focus:ring-2 focus:ring-red-500 h-20 resize-none bg-red-50/20"
                                                            placeholder="Why is this control not applicable? (e.g. No physical offices)"
                                                            value={ctrl.justification || ''}
                                                            onChange={(e) => handleChange(ctrl.control_id, 'justification', e.target.value)}
                                                        />
                                                    ) : (
                                                        <div className="bg-red-50 p-3 rounded-lg text-sm text-red-800 border border-red-100">
                                                            {ctrl.justification || <span className="opacity-50 italic">No justification provided.</span>}
                                                        </div>
                                                    )}
                                                </div>
                                            )}

                                        </div>
                                    );
                                })}
                            </div>
                        </div>
                    ))}

                    {filteredControls.length === 0 && (
                        <div className="text-center py-20 text-gray-400">
                            <Search size={48} className="mx-auto mb-4 opacity-20" />
                            <p>No controls found matching "{searchText}"</p>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default SoAEditor;
