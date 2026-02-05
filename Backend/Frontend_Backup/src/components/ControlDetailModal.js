import React, { useState, useEffect } from 'react';
import { X, Upload, Brain, FileText, CheckCircle, AlertTriangle, ExternalLink } from 'lucide-react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';

const API_URL = 'http://localhost:8000/api/v1';

const ControlDetailModal = ({ control, isOpen, onClose }) => {
    const [activeTab, setActiveTab] = useState('overview');
    const [evidence, setEvidence] = useState([]);
    const [assessments, setAssessments] = useState([]);
    const [isUploading, setIsUploading] = useState(false);
    const [isAssessing, setIsAssessing] = useState(false);
    const [uploadError, setUploadError] = useState(null);

    useEffect(() => {
        if (isOpen && control) {
            fetchEvidence();
            fetchAssessments();
        }
    }, [isOpen, control]);

    const fetchEvidence = async () => {
        try {
            const res = await axios.get(`${API_URL}/evidence/control/${control.id}`);
            setEvidence(res.data);
        } catch (e) {
            console.error("Failed to fetch evidence", e);
        }
    };

    const fetchAssessments = async () => {
        try {
            const res = await axios.get(`${API_URL}/assessments/control/${control.id}`);
            setAssessments(res.data);
        } catch (e) {
            console.error("Failed to fetch assessments", e);
        }
    };

    const handleFileUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        setIsUploading(true);
        setUploadError(null);

        const formData = new FormData();
        formData.append('file', file);
        formData.append('title', file.name); // Default title to filename

        try {
            await axios.post(`${API_URL}/evidence/upload/${control.id}`, formData);
            fetchEvidence(); // Refresh list
        } catch (error) {
            setUploadError("Failed to upload file.");
            console.error(error);
        } finally {
            setIsUploading(false);
        }
    };

    const runAssessment = async () => {
        setIsAssessing(true);
        try {
            await axios.post(`${API_URL}/assessments/analyze/${control.id}`);
            fetchAssessments(); // Refresh list
            setActiveTab('assessment');
        } catch (error) {
            alert("Assessment failed: " + error.message);
        } finally {
            setIsAssessing(false);
        }
    };

    if (!isOpen || !control) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 overflow-y-auto">
            <div className="bg-white rounded-lg w-full max-w-4xl shadow-xl m-4 flex flex-col max-h-[90vh]">

                {/* Header */}
                <div className="px-6 py-4 border-b flex justify-between items-start bg-gray-50 rounded-t-lg">
                    <div>
                        <div className="flex items-center gap-2 mb-1">
                            <span className="bg-gray-200 text-gray-700 text-xs font-bold px-2 py-0.5 rounded">{control.control_id}</span>
                            <span className={`text-xs font-bold px-2 py-0.5 rounded uppercase ${control.status === 'implemented' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                                }`}>{control.status.replace('_', ' ')}</span>
                        </div>
                        <h2 className="text-xl font-bold text-gray-900">{control.title}</h2>
                    </div>
                    <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
                        <X className="w-6 h-6" />
                    </button>
                </div>

                {/* Tabs */}
                <div className="px-6 pt-4 flex gap-4 border-b">
                    <button
                        onClick={() => setActiveTab('overview')}
                        className={`pb-2 text-sm font-medium ${activeTab === 'overview' ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-500 hover:text-gray-700'}`}
                    >
                        Overview
                    </button>
                    <button
                        onClick={() => setActiveTab('evidence')}
                        className={`pb-2 text-sm font-medium flex items-center gap-2 ${activeTab === 'evidence' ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-500 hover:text-gray-700'}`}
                    >
                        Evidence <span className="bg-gray-100 text-gray-600 px-1.5 rounded-full text-xs">{evidence.length}</span>
                    </button>
                    <button
                        onClick={() => setActiveTab('assessment')}
                        className={`pb-2 text-sm font-medium flex items-center gap-2 ${activeTab === 'assessment' ? 'text-blue-600 border-b-2 border-blue-600' : 'text-gray-500 hover:text-gray-700'}`}
                    >
                        AI Assessment
                    </button>
                </div>

                {/* Content */}
                <div className="p-6 overflow-y-auto flex-1">
                    {activeTab === 'overview' && (
                        <div className="space-y-4">
                            <div>
                                <h3 className="text-sm font-semibold text-gray-900 uppercase">Description</h3>
                                <p className="text-gray-700 mt-1">{control.description || "No description provided."}</p>
                            </div>
                            <div className="grid grid-cols-2 gap-4 mt-4">
                                <div className="bg-gray-50 p-4 rounded border">
                                    <span className="block text-xs text-gray-500 uppercase">Owner</span>
                                    <span className="font-medium text-gray-900">{control.owner || "Unassigned"}</span>
                                </div>
                                <div className="bg-gray-50 p-4 rounded border">
                                    <span className="block text-xs text-gray-500 uppercase">Priority</span>
                                    <span className="font-medium text-gray-900 capitalize">{control.priority || "Medium"}</span>
                                </div>
                            </div>
                        </div>
                    )}

                    {activeTab === 'evidence' && (
                        <div>
                            <div className="flex justify-between items-center mb-4">
                                <h3 className="font-bold text-gray-700">Proof of Implementation</h3>
                                <div className="relative">
                                    <input
                                        type="file"
                                        onChange={handleFileUpload}
                                        className="hidden"
                                        id="file-upload"
                                        disabled={isUploading}
                                    />
                                    <label
                                        htmlFor="file-upload"
                                        className={`flex items-center gap-2 px-4 py-2 border rounded shadow-sm text-sm font-medium cursor-pointer ${isUploading ? 'bg-gray-100 text-gray-400' : 'bg-white text-gray-700 hover:bg-gray-50'
                                            }`}
                                    >
                                        <Upload className="w-4 h-4" />
                                        {isUploading ? "Uploading..." : "Upload Evidence"}
                                    </label>
                                </div>
                            </div>

                            {uploadError && <div className="text-red-500 text-sm mb-4">{uploadError}</div>}

                            {evidence.length === 0 ? (
                                <div className="text-center py-12 border-2 border-dashed rounded-lg bg-gray-50">
                                    <Upload className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                                    <p className="text-gray-500">No evidence uploaded yet.</p>
                                </div>
                            ) : (
                                <table className="min-w-full divide-y divide-gray-200">
                                    <thead className="bg-gray-50">
                                        <tr>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">File Name</th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                                        </tr>
                                    </thead>
                                    <tbody className="bg-white divide-y divide-gray-200">
                                        {evidence.map(item => (
                                            <tr key={item.id}>
                                                <td className="px-6 py-4 whitespace-nowrap flex items-center gap-2">
                                                    <FileText className="w-4 h-4 text-gray-400" />
                                                    <span className="text-sm font-medium text-gray-900">{item.filename}</span>
                                                </td>
                                                <td className="px-6 py-4 whitespace-nowrap">
                                                    <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                                                        {item.status}
                                                    </span>
                                                </td>
                                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                                    {new Date(item.uploaded_at).toLocaleDateString()}
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            )}
                        </div>
                    )}

                    {activeTab === 'assessment' && (
                        <div>
                            <div className="flex justify-between items-center mb-6">
                                <div>
                                    <h3 className="font-bold text-gray-700">AI Compliance Check</h3>
                                    <p className="text-sm text-gray-500">Analyze evidence and policies using Google Gemini.</p>
                                </div>
                                <button
                                    onClick={runAssessment}
                                    disabled={isAssessing}
                                    className={`flex items-center gap-2 px-4 py-2 rounded text-white font-medium ${isAssessing ? 'bg-blue-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'
                                        }`}
                                >
                                    <Brain className="w-4 h-4" />
                                    {isAssessing ? "Analyzing..." : "Run New Assessment"}
                                </button>
                            </div>

                            {assessments && assessments.length > 0 && assessments[0] ? (
                                <div className="space-y-6">
                                    {/* Latest Assessment */}
                                    <div className="bg-white border rounded-lg overflow-hidden shadow-sm">
                                        <div className="p-4 bg-gray-50 border-b flex justify-between items-center">
                                            <span className="font-semibold text-gray-700">Latest Result</span>
                                            <span className="text-xs text-gray-500">
                                                {assessments[0].assessed_at ? new Date(assessments[0].assessed_at).toLocaleString() : 'Just now'}
                                            </span>
                                        </div>
                                        <div className="p-6">
                                            <div className="flex items-center mb-6">
                                                <div className="w-16 h-16 rounded-full flex items-center justify-center text-xl font-bold border-4" style={{
                                                    borderColor: (assessments[0].compliance_score || 0) >= 80 ? '#10B981' : (assessments[0].compliance_score || 0) >= 50 ? '#F59E0B' : '#EF4444',
                                                    color: (assessments[0].compliance_score || 0) >= 80 ? '#10B981' : (assessments[0].compliance_score || 0) >= 50 ? '#F59E0B' : '#EF4444'
                                                }}>
                                                    {assessments[0].compliance_score ?? 0}%
                                                </div>
                                                <div className="ml-4">
                                                    <h4 className="text-lg font-bold">Compliance Score</h4>
                                                    <p className="text-sm text-gray-500">Based on evidence and policy analysis.</p>
                                                </div>
                                            </div>

                                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                                <div className="bg-red-50 p-4 rounded-lg border border-red-100">
                                                    <h5 className="font-bold text-red-800 mb-2 flex items-center">
                                                        <AlertTriangle className="w-4 h-4 mr-2" /> Identified Gaps
                                                    </h5>
                                                    <p className="text-sm text-red-900 whitespace-pre-wrap">{assessments[0].gaps || "No gaps detected or not available."}</p>
                                                </div>
                                                <div className="bg-blue-50 p-4 rounded-lg border border-blue-100">
                                                    <h5 className="font-bold text-blue-800 mb-2 flex items-center">
                                                        <Brain className="w-4 h-4 mr-2" /> AI Recommendations
                                                    </h5>
                                                    <div className="text-sm text-blue-900 prose prose-sm max-w-none">
                                                        <ReactMarkdown>{assessments[0].recommendations || "No recommendations provided."}</ReactMarkdown>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    {/* History (collapsed later, simplified for now) */}
                                </div>
                            ) : (
                                <div className="text-center py-12 text-gray-500">
                                    No assessments run yet. Upload evidence and click "Run New Assessment".
                                </div>
                            )}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default ControlDetailModal;
