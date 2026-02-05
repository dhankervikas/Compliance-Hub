import React, { useState, useEffect } from 'react';
import axios from '../services/api';
import { X, CheckCircle, AlertTriangle, FileText, Upload, Brain } from 'lucide-react';
import Evidence from './Evidence'; // Reuse Evidence component if possible or just list evidence

const ControlDetailModal = ({ control, onClose, onUpdate }) => {
    const [activeTab, setActiveTab] = useState('overview');
    const [aiAnalysis, setAiAnalysis] = useState(null);
    const [loadingAi, setLoadingAi] = useState(false);

    // Mock AI Analysis fetch if backend endpoint exists
    const fetchAiAnalysis = async () => {
        setLoadingAi(true);
        try {
            // Check if analysis exists, if not trigger it
            // const res = await axios.post(`/assessments/analyze/${control.id}`);
            // setAiAnalysis(res.data);

            // Mocking for now to avoid 404s if endpoint not ready
            setTimeout(() => {
                setAiAnalysis({
                    score: control.status === 'IMPLEMENTED' ? 100 : 45,
                    gaps: control.status === 'IMPLEMENTED' ? [] : ["Evidence is missing", "Policy not reviewed"],
                    recommendations: control.status === 'IMPLEMENTED' ? ["Maintain current state"] : ["Upload evidence", "Approve policy"]
                });
                setLoadingAi(false);
            }, 1000);

        } catch (err) {
            console.error("AI Analysis failed", err);
            setLoadingAi(false);
        }
    };

    return (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex justify-end">
            <div className="w-full max-w-2xl bg-white h-full shadow-2xl flex flex-col animate-slide-in-right">

                {/* Header */}
                <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center bg-gray-50">
                    <div>
                        <div className="flex items-center gap-2 mb-1">
                            <span className="font-mono text-sm font-bold text-gray-600 bg-white border border-gray-200 px-2 py-0.5 rounded">
                                {control.control_id}
                            </span>
                            <span className={`text-xs font-bold px-2 py-0.5 rounded-full border ${control.status === 'IMPLEMENTED' ? 'bg-green-100 text-green-700 border-green-200' : 'bg-blue-100 text-blue-700 border-blue-200'
                                }`}>
                                {control.status}
                            </span>
                        </div>
                        <h2 className="text-lg font-bold text-gray-900 leading-tight">{control.title}</h2>
                    </div>
                    <button onClick={onClose} className="p-2 hover:bg-gray-200 rounded-full transition-colors">
                        <X className="w-5 h-5 text-gray-500" />
                    </button>
                </div>

                {/* Tabs */}
                <div className="flex border-b border-gray-200 px-6">
                    <button
                        onClick={() => setActiveTab('overview')}
                        className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${activeTab === 'overview' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'
                            }`}
                    >
                        Overview
                    </button>
                    <button
                        onClick={() => setActiveTab('evidence')}
                        className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${activeTab === 'evidence' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'
                            }`}
                    >
                        Evidence / Documents
                    </button>
                    <button
                        onClick={() => { setActiveTab('ai'); fetchAiAnalysis(); }}
                        className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors flex items-center gap-2 ${activeTab === 'ai' ? 'border-purple-600 text-purple-600' : 'border-transparent text-gray-500 hover:text-gray-700'
                            }`}
                    >
                        <Brain className="w-4 h-4" /> AI Insight
                    </button>
                </div>

                {/* Content */}
                <div className="flex-1 overflow-y-auto p-6">

                    {activeTab === 'overview' && (
                        <div className="space-y-6">
                            <div>
                                <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wider mb-2">Description</h3>
                                <p className="text-gray-700 leading-relaxed text-sm">{control.description}</p>
                            </div>

                            {/* Remediation */}
                            <div className="bg-blue-50 p-4 rounded-lg border border-blue-100">
                                <h3 className="text-sm font-bold text-blue-900 mb-2 flex items-center gap-2">
                                    <CheckCircle className="w-4 h-4" /> Recommended Action
                                </h3>
                                <p className="text-sm text-blue-800">
                                    Ensure that a formal policy is documented and approved by management.
                                    Upload the signed PDF to the Evidence tab.
                                </p>
                            </div>
                        </div>
                    )}

                    {activeTab === 'evidence' && (
                        <div>
                            <div className="flex justify-between items-center mb-4">
                                <h3 className="font-bold text-gray-900">Linked Evidence</h3>
                                <label className="cursor-pointer bg-white border border-gray-300 text-gray-700 px-3 py-1.5 rounded-lg text-sm font-medium hover:bg-gray-50 shadow-sm flex items-center gap-2">
                                    <Upload className="w-4 h-4" /> Upload New
                                    <input type="file" className="hidden" disabled />
                                </label>
                            </div>

                            <div className="bg-gray-50 rounded-lg border border-gray-200 p-8 text-center text-gray-500 text-sm">
                                <FileText className="w-8 h-8 mx-auto mb-2 text-gray-400" />
                                <p>No evidence linked explicitly to this control yet.</p>
                                <p className="text-xs mt-1">Go to <b>Evidence Library</b> to manage files.</p>
                            </div>
                        </div>
                    )}

                    {activeTab === 'ai' && (
                        <div className="space-y-6">
                            {loadingAi ? (
                                <div className="text-center py-12">
                                    <Brain className="w-12 h-12 text-purple-200 animate-pulse mx-auto mb-4" />
                                    <p className="text-gray-500">Analyzing control effectiveness...</p>
                                </div>
                            ) : aiAnalysis ? (
                                <div className="animate-fade-in">
                                    <div className="flex items-center justify-between mb-6">
                                        <h3 className="text-lg font-bold text-gray-900">AI Assessment</h3>
                                        <span className={`text-xl font-bold ${aiAnalysis.score >= 80 ? 'text-green-600' : 'text-orange-500'}`}>
                                            {aiAnalysis.score}/100
                                        </span>
                                    </div>

                                    <div className="space-y-4">
                                        <div className="bg-red-50 p-4 rounded-lg border border-red-100">
                                            <h4 className="font-bold text-red-800 mb-2 text-sm">Detected Gaps</h4>
                                            <ul className="list-disc pl-4 space-y-1">
                                                {aiAnalysis.gaps.map((gap, i) => (
                                                    <li key={i} className="text-sm text-red-700">{gap}</li>
                                                ))}
                                                {aiAnalysis.gaps.length === 0 && <li className="text-sm text-gray-500 italic">No gaps detected.</li>}
                                            </ul>
                                        </div>

                                        <div className="bg-green-50 p-4 rounded-lg border border-green-100">
                                            <h4 className="font-bold text-green-800 mb-2 text-sm">Recommendations</h4>
                                            <ul className="list-disc pl-4 space-y-1">
                                                {aiAnalysis.recommendations.map((rec, i) => (
                                                    <li key={i} className="text-sm text-green-700">{rec}</li>
                                                ))}
                                            </ul>
                                        </div>
                                    </div>
                                </div>
                            ) : null}
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="bg-gray-50 px-6 py-4 border-t border-gray-200 flex justify-end">
                    <button
                        onClick={onClose}
                        className="px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium hover:bg-gray-50 mr-2"
                    >
                        Close
                    </button>
                    <button className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 shadow-sm">
                        Mark as Reviewed
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ControlDetailModal;
