import React, { useState, useEffect } from 'react';
import axios from '../services/api';
import assessmentService from '../services/assessmentService';
import {
    CheckCircle,
    AlertTriangle,
    ChevronDown,
    ChevronUp,
    ClipboardCheck,
    FileText,
    Bot,
    Upload,
    Paperclip,
    Check
} from 'lucide-react';

const Controls = () => {
    const [controls, setControls] = useState([]);
    const [loading, setLoading] = useState(true);
    const [expandedRows, setExpandedRows] = useState(new Set());
    const [assessments, setAssessments] = useState({});

    // Mock Evidence State for Manual Upload Demo
    const [uploadedEvidence, setUploadedEvidence] = useState({}); // { controlId: [file1, file2] }

    useEffect(() => {
        const fetchControls = async () => {
            try {
                const res = await axios.get('/controls/');
                setControls(res.data);
                setLoading(false);
            } catch (err) {
                console.error("Failed to fetch controls", err);
                setLoading(false);
            }
        };
        fetchControls();

        // Load some mock assessments for demo
        const loadAssessments = async () => {
            // ...
        }
    }, []);

    const toggleRow = (id) => {
        const newExpanded = new Set(expandedRows);
        if (newExpanded.has(id)) newExpanded.delete(id);
        else newExpanded.add(id);
        setExpandedRows(newExpanded);
    };

    const StatusBadge = ({ status }) => {
        if (status === 'PASS') return (
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                <CheckCircle className="w-3 h-3 mr-1" /> Ready
            </span>
        );
        return (
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                <AlertTriangle className="w-3 h-3 mr-1" /> Not Ready
            </span>
        );
    };

    const getFamily = (id) => id.split('.')[0];

    // Group controls by family
    const groupedControls = controls.reduce((acc, control) => {
        const family = getFamily(control.control_id);
        if (!acc[family]) acc[family] = [];
        acc[family].push(control);
        return acc;
    }, {});

    // Sort families... (Using natural sort logic usually, but here keys are CC1, CC2 etc)
    const sortedFamilies = Object.keys(groupedControls).sort((a, b) => {
        const numA = parseInt(a.replace(/\D/g, ''));
        const numB = parseInt(b.replace(/\D/g, ''));
        return numA - numB;
    });

    const handleMockUpload = (controlId) => {
        const fileName = window.prompt("Simulate File Upload: Enter filename to attach (e.g. 'BoardMinutes.pdf')");
        if (fileName) {
            setUploadedEvidence(prev => ({
                ...prev,
                [controlId]: [...(prev[controlId] || []), { name: fileName, date: new Date().toLocaleDateString() }]
            }));
        }
    }

    if (loading) return <div className="p-8 text-center text-gray-500">Loading controls...</div>;

    return (
        <div className="space-y-6 pb-20">
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">Compliance Controls</h1>
                    <p className="text-sm text-gray-500">
                        View status, verify readiness, and <strong>manually upload</strong> non-technical evidence.
                    </p>
                </div>
            </div>

            {sortedFamilies.map(family => {
                const familyControls = groupedControls[family];
                const passedCount = familyControls.filter(c => c.status === 'PASS').length;
                const progress = Math.round((passedCount / familyControls.length) * 100);

                return (
                    <div key={family} className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden mb-6">
                        {/* Family Header */}
                        <div className="bg-slate-50 px-6 py-4 border-b border-gray-200 flex justify-between items-center">
                            <div>
                                <h3 className="text-lg font-bold text-gray-900">{family} Family</h3>
                                <p className="text-xs text-gray-500">{familyControls.length} Controls</p>
                            </div>
                            <div className="flex items-center gap-4 w-1/3">
                                <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                                    <div className="h-full bg-blue-600 rounded-full transition-all duration-500" style={{ width: `${progress}%` }}></div>
                                </div>
                                <span className="text-sm font-bold text-gray-700">{progress}%</span>
                            </div>
                        </div>

                        {/* Controls List */}
                        <div className="divide-y divide-gray-100">
                            {familyControls.map(control => {
                                const isRowExpanded = expandedRows.has(control.id);
                                const testInfo = control.mapped_test;

                                return (
                                    <div key={control.id} className="group">
                                        <div
                                            onClick={() => toggleRow(control.id)}
                                            className={`px-6 py-4 flex items-center gap-4 cursor-pointer hover:bg-blue-50/50 transition-colors ${isRowExpanded ? 'bg-blue-50/50' : ''}`}
                                        >
                                            <div className="text-gray-400">
                                                {isRowExpanded ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
                                            </div>
                                            <div className="w-24 shrink-0 font-mono text-sm font-medium text-gray-500">{control.control_id}</div>
                                            <div className="flex-1 font-medium text-gray-900">{control.title}</div>

                                            <div className="flex items-center gap-6">
                                                <div className="flex gap-2 text-gray-400">
                                                    {testInfo && (
                                                        <div className="group/icon relative flex">
                                                            <ClipboardCheck className="w-4 h-4 text-purple-500" />
                                                            <span className="absolute bottom-full mb-1 left-1/2 -translate-x-1/2 px-2 py-1 bg-gray-800 text-white text-xs rounded opacity-0 group-hover/icon:opacity-100 whitespace-nowrap pointer-events-none z-10">
                                                                Automated
                                                            </span>
                                                        </div>
                                                    )}
                                                    {(uploadedEvidence[control.id] && uploadedEvidence[control.id].length > 0) && (
                                                        <div className="group/icon relative flex">
                                                            <Paperclip className="w-4 h-4 text-blue-500" />
                                                            <span className="absolute bottom-full mb-1 left-1/2 -translate-x-1/2 px-2 py-1 bg-gray-800 text-white text-xs rounded opacity-0 group-hover/icon:opacity-100 whitespace-nowrap pointer-events-none z-10">
                                                                Manual Evidence
                                                            </span>
                                                        </div>
                                                    )}
                                                </div>
                                                <StatusBadge status={control.status} />
                                            </div>
                                        </div>

                                        {/* Control Expanded Detail */}
                                        {isRowExpanded && (
                                            <div className="px-16 py-6 bg-gray-50 border-t border-gray-100 grid grid-cols-1 lg:grid-cols-2 gap-8 animate-slide-in">

                                                {/* Left: Info & AI */}
                                                <div className="space-y-4">
                                                    <div>
                                                        <h4 className="text-xs font-bold text-gray-500 uppercase mb-2">Description</h4>
                                                        <p className="text-sm text-gray-700 leading-relaxed">{control.description}</p>
                                                    </div>

                                                    <div className="bg-white p-4 rounded-lg border border-purple-100 shadow-sm">
                                                        <div className="flex items-center gap-2 mb-2 text-purple-700 font-semibold text-sm">
                                                            <Bot className="w-4 h-4" /> AI Analysis
                                                        </div>
                                                        {assessments[control.id] ? (
                                                            <div className="text-sm">
                                                                <div className="mb-2">
                                                                    <span className="font-medium text-gray-700">Gaps:</span>
                                                                    <span className="text-gray-600 ml-1">{assessments[control.id][0]?.gaps}</span>
                                                                </div>
                                                            </div>
                                                        ) : (
                                                            <button
                                                                onClick={async (e) => {
                                                                    e.stopPropagation();
                                                                    // Mock assessment
                                                                    setAssessments(prev => ({
                                                                        ...prev,
                                                                        [control.id]: [{ gaps: "No significant gaps detected based on current evidence." }]
                                                                    }));
                                                                }}
                                                                className="text-xs bg-purple-100 text-purple-700 px-3 py-1.5 rounded hover:bg-purple-200"
                                                            >
                                                                Run Automatic Analysis
                                                            </button>
                                                        )}
                                                    </div>
                                                </div>

                                                {/* Right: Technical Evidence & Manual Uploads */}
                                                <div className="space-y-4">

                                                    {/* Automated Moniitoring Section */}
                                                    <div>
                                                        <h4 className="text-xs font-bold text-gray-500 uppercase mb-2">Technical Evidence (Automated)</h4>
                                                        {testInfo ? (
                                                            <div className="bg-white border border-gray-200 rounded p-3 flex justify-between items-center">
                                                                <div className="flex items-center gap-2">
                                                                    <ClipboardCheck className="w-5 h-5 text-gray-400" />
                                                                    <span className="text-sm font-medium text-gray-900">
                                                                        {testInfo.collector_name || "Standard Compliance Check"}
                                                                    </span>
                                                                </div>
                                                                <span className="text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded flex items-center gap-1">
                                                                    <Bot className="w-3 h-3" /> Automated
                                                                </span>
                                                            </div>
                                                        ) : (
                                                            <p className="text-xs text-gray-400 italic">No automated tests mapped.</p>
                                                        )}
                                                    </div>

                                                    {/* Manual Evidence Section */}
                                                    <div>
                                                        <h4 className="text-xs font-bold text-gray-500 uppercase mb-2 flex justify-between items-center">
                                                            <span>Administrative Evidence (Manual)</span>
                                                            <button
                                                                onClick={() => handleMockUpload(control.id)}
                                                                className="text-blue-600 hover:text-blue-700 text-xs font-bold flex items-center gap-1"
                                                            >
                                                                <Upload className="w-3 h-3" /> Upload New
                                                            </button>
                                                        </h4>

                                                        {uploadedEvidence[control.id] && uploadedEvidence[control.id].length > 0 ? (
                                                            <div className="space-y-2">
                                                                {uploadedEvidence[control.id].map((file, idx) => (
                                                                    <div key={idx} className="bg-white border border-gray-200 rounded p-3 flex justify-between items-center">
                                                                        <div className="flex items-center gap-2">
                                                                            <Paperclip className="w-4 h-4 text-blue-500" />
                                                                            <span className="text-sm font-medium text-gray-900">{file.name}</span>
                                                                        </div>
                                                                        <span className="text-xs text-gray-500">{file.date}</span>
                                                                    </div>
                                                                ))}
                                                            </div>
                                                        ) : (
                                                            <div className="bg-gray-50 border border-dashed border-gray-300 rounded p-4 text-center">
                                                                <p className="text-xs text-gray-500 mb-2">No documents uploaded.</p>
                                                            </div>
                                                        )}
                                                    </div>
                                                </div>

                                            </div>
                                        )}
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                );
            })}
        </div>
    );
};

export default Controls;
