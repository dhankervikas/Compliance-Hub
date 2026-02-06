import React, { useState, useEffect } from 'react';
import { Shield, CheckCircle, AlertTriangle, ArrowRight, X, Info } from 'lucide-react';
import { auditService } from '../../services/auditService';
import api from '../../services/api';

// const API_URL = config.API_BASE_URL; // api service handles base URL

const FrameworkSetupWizard = ({ onComplete, onCancel }) => {
    const [step, setStep] = useState(1);
    const [loading, setLoading] = useState(false);

    // State for Selection
    const [selectedPrinciples, setSelectedPrinciples] = useState(['Security']);
    const [justifications, setJustifications] = useState({});

    // Load existing settings on mount
    useEffect(() => {
        const fetchSettings = async () => {
            try {
                // api.get automatically attaches token
                const res = await api.get(`/settings/scope`);
                const content = res.data.content || {};

                if (content.soc2_selected_principles && Array.isArray(content.soc2_selected_principles)) {
                    setSelectedPrinciples(content.soc2_selected_principles);
                }
                if (content.soc2_exclusions) {
                    setJustifications(content.soc2_exclusions);
                }
            } catch (err) {
                console.warn("Failed to load existing SOC 2 settings", err);
            }
        };
        fetchSettings();
    }, []);

    // Definition of TSC Principles
    const PRINCIPLES = [
        {
            id: 'Security',
            name: 'Security (Common Criteria)',
            desc: 'Protection against unauthorized access. Mandatory for all SOC 2 reports.',
            locked: true
        },
        {
            id: 'Availability',
            name: 'Availability',
            desc: 'System availability for operation and use as committed or agreed. Critical for hosting/SaaS.',
            locked: false
        },
        {
            id: 'Confidentiality',
            name: 'Confidentiality',
            desc: 'Information designated as confidential is protected. Important for IP/Sensitive Data.',
            locked: false
        },
        {
            id: 'Processing Integrity',
            name: 'Processing Integrity',
            desc: 'System processing is complete, valid, accurate, timely, and authorized. For Fintech/Transaction systems.',
            locked: false
        },
        {
            id: 'Privacy',
            name: 'Privacy',
            desc: 'Personal information is collected, used, retained, disclosed, and disposed of appropriately. For PII handlers.',
            locked: false
        }
    ];

    const togglePrinciple = (id) => {
        if (id === 'Security') return; // Locked

        setSelectedPrinciples(prev => {
            if (prev.includes(id)) {
                return prev.filter(p => p !== id);
            } else {
                return [...prev, id];
            }
        });
    };

    const handleJustificationChange = (id, text) => {
        setJustifications(prev => ({
            ...prev,
            [id]: text
        }));
    };

    const handleSave = async () => {
        setLoading(true);
        try {
            // 1. Save Framework Activation (Legacy/Mock)
            // We still might want to save the selected principles list to legacy settings 
            // if other parts of the app use it (e.g., policy generation).
            // For now, we will do BOTH: Save legacy principles + New Strict Justifications.

            // A. Legacy Save (for Principles List)
            let currentContent = {};
            try {
                const res = await api.get(`/settings/scope`);
                currentContent = res.data.content || {};
            } catch (e) { console.log("No settings, creating new..."); }

            const payload = {
                section: "scope",
                content: {
                    ...currentContent,
                    soc2_selected_principles: selectedPrinciples
                    // soc2_exclusions is DEPRECATED in favor of new table
                }
            };
            await api.put(`/settings/scope`, payload);

            // B. Strict Scope API Save (For Exclusions)
            const promises = Object.entries(justifications).map(([criteriaId, reason]) => {
                return auditService.saveScopeJustification({
                    standard_type: 'SOC2',
                    criteria_id: criteriaId,
                    reason_code: 'NOT_APPLICABLE',
                    justification_text: reason
                });
            });
            await Promise.all(promises);

            // Success
            if (onComplete) onComplete();

        } catch (err) {
            console.error("Failed to save SOC 2 Scope", err);
            const msg = err.response?.data?.detail || err.message || "Unknown error";
            alert(`Failed to save settings: ${msg}`);
        } finally {
            setLoading(false);
        }
    };

    // --- RENDER STEPS ---

    // STEP 1: SELECTION
    if (step === 1) {
        return (
            <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4 backdrop-blur-sm animate-fade-in">
                <div className="bg-white rounded-2xl shadow-2xl max-w-3xl w-full flex flex-col max-h-[90vh] overflow-hidden">
                    <div className="p-8 border-b border-gray-100 bg-gradient-to-r from-blue-50 to-white">
                        <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-3">
                            <Shield className="w-8 h-8 text-blue-600" />
                            SOC 2 Scope Configuration
                        </h2>
                        <p className="text-gray-600 mt-2">Which Trust Services Criteria (TSC) apply to your organization?</p>
                    </div>

                    <div className="p-8 flex-1 overflow-y-auto">
                        <div className="space-y-4">
                            {PRINCIPLES.map(p => {
                                const isSelected = selectedPrinciples.includes(p.id);
                                return (
                                    <div
                                        key={p.id}
                                        className={`p-4 rounded-xl border-2 transition-all cursor-pointer flex items-start gap-4 ${isSelected ? 'border-blue-500 bg-blue-50/30' : 'border-gray-200 hover:border-blue-200'}`}
                                        onClick={() => togglePrinciple(p.id)}
                                    >
                                        <div className={`w-6 h-6 rounded border flex items-center justify-center flex-shrink-0 mt-0.5 ${isSelected ? 'bg-blue-500 border-blue-500' : 'bg-white border-gray-300'}`}>
                                            {isSelected && <CheckCircle className="w-4 h-4 text-white" />}
                                        </div>
                                        <div>
                                            <div className="flex items-center gap-2">
                                                <h3 className="font-bold text-gray-900">{p.name}</h3>
                                                {p.locked && <span className="text-[10px] bg-gray-200 text-gray-600 px-1.5 py-0.5 rounded font-bold uppercase">Mandatory</span>}
                                            </div>
                                            <p className="text-sm text-gray-500 mt-1">{p.desc}</p>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    </div>

                    <div className="p-6 border-t border-gray-100 bg-gray-50 flex justify-between items-center">
                        <button onClick={onCancel} className="text-gray-500 font-medium hover:text-gray-800">Cancel</button>
                        <button
                            onClick={() => setStep(2)}
                            className="bg-blue-600 text-white px-6 py-3 rounded-xl font-bold hover:bg-blue-700 flex items-center gap-2 shadow-lg shadow-blue-200"
                        >
                            Next: Justify Exclusions <ArrowRight className="w-4 h-4" />
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    // STEP 2: JUSTIFICATION
    const excludedPrinciples = PRINCIPLES.filter(p => !selectedPrinciples.includes(p.id));

    if (step === 2) {
        return (
            <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4 backdrop-blur-sm animate-fade-in">
                <div className="bg-white rounded-2xl shadow-2xl max-w-3xl w-full flex flex-col max-h-[90vh] overflow-hidden">
                    <div className="p-8 border-b border-gray-100 bg-gradient-to-r from-orange-50 to-white">
                        <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-3">
                            <AlertTriangle className="w-8 h-8 text-orange-500" />
                            Non-Applicability Justification
                        </h2>
                        <p className="text-gray-600 mt-2">Auditors require a valid reason for excluding trust principles. These notes will appear in your final report.</p>
                    </div>

                    <div className="p-8 flex-1 overflow-y-auto">
                        {excludedPrinciples.length === 0 ? (
                            <div className="text-center py-12">
                                <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
                                <h3 className="text-xl font-bold text-gray-900">Full Scope Selected!</h3>
                                <p className="text-gray-500 mt-2">You have selected all Trust Services Criteria. No justification needed.</p>
                            </div>
                        ) : (
                            <div className="space-y-6">
                                {excludedPrinciples.map(p => (
                                    <div key={p.id} className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
                                        <h3 className="font-bold text-gray-900 mb-2 flex items-center gap-2">
                                            <X className="w-4 h-4 text-red-500" />
                                            Why exclude {p.name}?
                                        </h3>
                                        <textarea
                                            placeholder={`e.g., We do not process ${p.id === 'Privacy' ? 'PII' : 'financial transactions'}...`}
                                            className="w-full border border-gray-300 rounded-lg p-3 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 min-h-[80px]"
                                            value={justifications[p.id] || ''}
                                            onChange={(e) => handleJustificationChange(p.id, e.target.value)}
                                        />
                                        <p className="text-xs text-gray-400 mt-2 flex items-center gap-1">
                                            <Info className="w-3 h-3" />
                                            This will be saved to your compliance profile.
                                        </p>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>

                    <div className="p-6 border-t border-gray-100 bg-gray-50 flex justify-between items-center">
                        <button onClick={() => setStep(1)} className="text-gray-500 font-medium hover:text-gray-800">Back</button>
                        <button
                            onClick={handleSave}
                            disabled={loading}
                            className="bg-green-600 text-white px-8 py-3 rounded-xl font-bold hover:bg-green-700 flex items-center gap-2 shadow-lg shadow-green-200 disabled:opacity-50"
                        >
                            {loading ? 'Saving...' : 'Finalize Configuration'} <CheckCircle className="w-4 h-4" />
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    return null;
};

export default FrameworkSetupWizard;
