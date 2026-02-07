import React, { useState, useEffect } from 'react';
import axios from '../services/api';
import { X, CheckCircle, AlertTriangle, FileText, Upload, Brain } from 'lucide-react';
import Evidence from './Evidence'; // Reuse Evidence component if possible or just list evidence

const ControlDetailModal = ({ control, onClose, onUpdate }) => {
    const [activeTab, setActiveTab] = useState('overview');
    const [aiAnalysis, setAiAnalysis] = useState(null);
    const [loadingAi, setLoadingAi] = useState(false);

    // Mock Genie Analysis fetch if backend endpoint exists
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
            console.error("Genie Analysis failed", err);
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
                        <Brain className="w-4 h-4" /> Genie Insight
                    </button>
                </div>

                {/* Content */}
                <div className="flex-1 overflow-y-auto p-6">

                    {/* UNIFIED IMPLEMENTATION VIEW */}
                    <div className="space-y-8">

                        {/* 1. BUSINESS GOAL (Explanation) */}
                        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-6 rounded-xl border border-blue-100">
                            <h3 className="text-xs font-bold text-blue-800 uppercase tracking-widest mb-2 flex items-center gap-2">
                                <Brain className="w-4 h-4" /> Business Goal
                            </h3>
                            <p className="text-lg font-medium text-blue-900 leading-relaxed">
                                {aiAnalysis?.explanation || control.ai_explanation || control.description}
                            </p>
                        </div>

                        {/* 2. IMPLEMENTATION CHECKLIST (Requirements) */}
                        <div>
                            <div className="flex items-center justify-between mb-4">
                                <h3 className="text-sm font-bold text-gray-900 uppercase tracking-widest flex items-center gap-2">
                                    <CheckCircle className="w-4 h-4 text-emerald-500" /> Implementation Tasks
                                </h3>
                                <span className="text-xs font-medium bg-gray-100 text-gray-600 px-2 py-1 rounded-full">
                                    {aiAnalysis?.requirements?.length || 0} Steps
                                </span>
                            </div>

                            <div className="space-y-3">
                                {(aiAnalysis?.requirements || JSON.parse(control.ai_requirements_json || '[]')).map((req, i) => (
                                    <div key={i} className="group flex items-start gap-4 p-4 rounded-xl border border-gray-200 hover:border-blue-300 hover:bg-blue-50/30 transition-all bg-white shadow-sm">
                                        <div className="mt-1">
                                            <input
                                                type="checkbox"
                                                className="w-5 h-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
                                            />
                                        </div>
                                        <div className="flex-1">
                                            <div className="flex items-center gap-2 mb-1">
                                                <h4 className="font-bold text-gray-900 text-base">{req.Requirement_Name || req.name}</h4>
                                                {req.Automation_Potential && (
                                                    <span className="text-[10px] font-bold bg-purple-100 text-purple-700 px-1.5 py-0.5 rounded border border-purple-200">
                                                        AUTO
                                                    </span>
                                                )}
                                                <span className="text-[10px] font-bold bg-gray-100 text-gray-600 px-1.5 py-0.5 rounded border border-gray-200 uppercase">
                                                    {req.Source || 'MANUAL'}
                                                </span>
                                            </div>
                                            <p className="text-sm text-gray-600 leading-relaxed">{req.Description || req.desc}</p>

                                            {/* GUIDANCE HOVER */}
                                            {(req.Auditor_Guidance || req.audit_guidance) && (
                                                <div className="mt-3 text-xs bg-gray-50 p-2 rounded border border-gray-100 text-gray-500 italic pb-1">
                                                    <strong className="text-gray-700 not-italic">Auditor Note: </strong>
                                                    {req.Auditor_Guidance || req.audit_guidance}
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                ))}

                                {(!control.ai_requirements_json && !aiAnalysis) && (
                                    <div className="text-center py-8 text-gray-400 italic">
                                        No implementation tasks defined. Run Genie Analysis to generate.
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
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
