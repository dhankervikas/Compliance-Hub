import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from '../services/api';
import {
    ChevronLeft, Save, Globe, CheckCircle, Clock,
    Shield, FileText, History, Share2, Printer
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

const PolicyDetail = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const { user } = useAuth();

    const [policy, setPolicy] = useState(null);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState('editor'); // editor, preview, history

    // Mock Version History
    const versions = [
        { version: '1.2', date: '2025-02-10', author: 'Jane Doe', status: 'Draft' },
        { version: '1.1', date: '2024-12-15', author: 'John Smith', status: 'Approved' },
        { version: '1.0', date: '2024-11-01', author: 'System', status: 'Archived' },
    ];

    useEffect(() => {
        fetchPolicy();
    }, [id]);

    const fetchPolicy = async () => {
        try {
            const res = await axios.get(`/policies/${id}`);
            setPolicy(res.data);
        } catch (err) {
            console.error("Failed to fetch policy", err);
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <div className="p-8 text-center text-gray-500">Loading policy...</div>;
    if (!policy) return <div className="p-8 text-center text-red-500">Policy not found</div>;

    return (
        <div className="min-h-screen bg-gray-50 flex flex-col">
            {/* Header */}
            <div className="bg-white border-b border-gray-200 px-6 py-4 flex justify-between items-center sticky top-0 z-10">
                <div className="flex items-center gap-4">
                    <button onClick={() => navigate(-1)} className="text-gray-500 hover:text-gray-800">
                        <ChevronLeft className="w-5 h-5" />
                    </button>
                    <div>
                        <div className="flex items-center gap-3">
                            <h1 className="text-xl font-bold text-gray-900">{policy.name}</h1>
                            <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${policy.status === 'Approved' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                                }`}>
                                {policy.status}
                            </span>
                        </div>
                        <p className="text-xs text-gray-500 mt-0.5">Last updated {new Date(policy.updated_at).toLocaleDateString()} by {policy.owner}</p>
                    </div>
                </div>

                <div className="flex items-center gap-3">
                    <button className="px-3 py-1.5 text-gray-600 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 flex items-center gap-2 text-sm">
                        <Printer className="w-4 h-4" /> Print
                    </button>
                    <button className="px-3 py-1.5 text-gray-600 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 flex items-center gap-2 text-sm" onClick={() => alert("Attestation request sent to all employees.")}>
                        <Share2 className="w-4 h-4" /> Send for Acceptance
                    </button>
                    <button className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 flex items-center gap-2 text-sm font-medium">
                        <Save className="w-4 h-4" /> Save Changes
                    </button>
                </div>
            </div>

            <div className="flex flex-1 overflow-hidden">
                {/* Left Sidebar: Context & Metadata */}
                <div className="w-72 bg-white border-r border-gray-200 overflow-y-auto hidden lg:block">
                    <div className="p-5 space-y-8">
                        {/* Standards Mapping */}
                        <div>
                            <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-4 flex items-center gap-2">
                                <Shield className="w-4 h-4" /> Mapped Standards
                            </h3>
                            <div className="space-y-3">
                                <div className="p-3 bg-blue-50 border border-blue-100 rounded-lg">
                                    <div className="flex justify-between items-start mb-1">
                                        <span className="font-semibold text-sm text-blue-900">ISO 27001:2022</span>
                                    </div>
                                    <p className="text-xs text-blue-700">A.5.15 Access Control</p>
                                    <p className="text-xs text-blue-700">A.8.2 Privileged Access</p>
                                </div>
                                <div className="p-3 bg-gray-50 border border-gray-100 rounded-lg">
                                    <div className="flex justify-between items-start mb-1">
                                        <span className="font-semibold text-sm text-gray-900">SOC 2 Type II</span>
                                    </div>
                                    <p className="text-xs text-gray-600">CC6.1 Logical Access</p>
                                </div>
                            </div>
                        </div>

                        {/* Recent Activity / Version History Preview */}
                        <div>
                            <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-4 flex items-center gap-2">
                                <History className="w-4 h-4" /> Version History
                            </h3>
                            <div className="space-y-4 relative before:absolute before:left-1.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-gray-100">
                                {versions.map((ver, idx) => (
                                    <div key={idx} className="relative pl-6">
                                        <div className={`absolute left-0 top-1.5 w-3.5 h-3.5 rounded-full border-2 ${ver.status === 'Approved' ? 'bg-green-500 border-white' :
                                            idx === 0 ? 'bg-indigo-500 border-white' : 'bg-gray-300 border-white'
                                            }`}></div>
                                        <div className="flex justify-between items-center mb-0.5">
                                            <span className="text-sm font-medium text-gray-900">v{ver.version}</span>
                                            <span className="text-[10px] text-gray-500">{ver.date}</span>
                                        </div>
                                        <p className="text-xs text-gray-500">{ver.author}</p>
                                        <span className={`text-[10px] px-1.5 py-0.5 rounded ${ver.status === 'Approved' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'
                                            }`}>{ver.status}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>

                {/* Main Content: Editor */}
                <div className="flex-1 overflow-y-auto bg-gray-50 p-6">
                    <div className="max-w-4xl mx-auto bg-white rounded-xl shadow-sm border border-gray-200 min-h-[800px] p-12">
                        {/* Placeholder for Rich Text Editor */}
                        <div className="prose prose-indigo max-w-none">
                            {/* In a real app, use Tiptap or Quill here */}
                            <h2 className="text-3xl font-bold text-gray-900 mb-8">{policy.name}</h2>
                            <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg mb-8 text-sm text-yellow-800">
                                <strong>Draft Mode:</strong> You are editing version {policy.version}. Changes are auto-saved.
                            </div>

                            <div className="whitespace-pre-wrap text-gray-700 leading-relaxed space-y-4">
                                {policy.content || "Start writing your policy..."}
                            </div>
                        </div>
                    </div>
                </div>

                {/* Right Sidebar: Review & Approval (Optional, keeping simple for now) */}
            </div>
        </div>
    );
};

export default PolicyDetail;
