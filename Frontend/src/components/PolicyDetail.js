import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from '../services/api';
import PolicyEditor from './PolicyEditor';
import {
    ArrowLeft,
    CheckCircle,
    Clock,
    FileText,
    MoreHorizontal,
    Edit3,
    Send,
    Download,
    History
} from 'lucide-react';

const PolicyDetail = () => {
    const { id, tenantId } = useParams();
    const navigate = useNavigate();
    const [policy, setPolicy] = useState(null);
    const [loading, setLoading] = useState(true);
    const [isEditorOpen, setIsEditorOpen] = useState(false);

    const [masterContent, setMasterContent] = useState(null);
    const baseUrl = tenantId ? `/t/${tenantId}` : '';

    const fetchPolicy = async () => {
        try {
            const res = await axios.get(`/policies/${id}`);
            setPolicy(res.data);

            // If linked to master, fetch master content for sidebar
            if (res.data.master_template_id) {
                try {
                    const masterRes = await axios.get(`/master-templates/${res.data.master_template_id}`);
                    setMasterContent(masterRes.data.content);
                } catch (mastersErr) {
                    console.error("Failed to fetch master template", mastersErr);
                }
            }

        } catch (error) {
            console.error("Failed to fetch policy", error);
            // navigate(`${baseUrl}/policies`); // Fallback
        } finally {
            setLoading(false);
        }
    };

    const handleRestore = async () => {
        if (window.confirm("Are you sure? This will discard your custom changes and revert to the Master Template.")) {
            try {
                await axios.post(`/policies/${id}/restore`);
                fetchPolicy(); // Reload
                alert("Restored to Standard.");
            } catch (err) {
                console.error("Restore failed", err);
                alert("Failed to restore.");
            }
        }
    };

    useEffect(() => {
        fetchPolicy();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [id]);

    const handleApprovalRequest = async () => {
        // Mock Approval Logic
        if (window.confirm(`Request approval for "${policy.name}"? This will notify the Admin.`)) {
            try {
                // In a real app, calling an API. Here just mocking the UI state.
                await axios.post(`/policies/${id}/request_approval`);
                alert("Approval Request Sent to admin@example.com");

                // Optimistically update status for demo
                const updatedPolicy = { ...policy, status: 'Pending Approval' };
                setPolicy(updatedPolicy);

                // Actually save it to backend so it persists
                await axios.put(`/policies/${id}`, { status: 'Pending Approval' });
            } catch (error) {
                console.error("Failed to request approval", error);
            }
        }
    };

    if (loading) return <div className="p-12 text-center text-gray-500">Loading policy...</div>;
    if (!policy) return <div className="p-12 text-center text-red-500">Policy not found</div>;

    const isDraft = policy.status !== 'Approved';

    return (
        <div className="min-h-screen bg-gray-50 pb-12">
            {/* Top Bar */}
            <div className="bg-white border-b border-gray-200 px-8 py-4 flex justify-between items-center sticky top-0 z-10 shadow-sm">
                <div className="flex items-center gap-4">
                    <button onClick={() => navigate(`${baseUrl}/policies`)} className="p-2 hover:bg-gray-100 rounded-full text-gray-500">
                        <ArrowLeft className="w-5 h-5" />
                    </button>
                    <div>
                        <h1 className="text-xl font-bold text-gray-900">{policy.name}</h1>
                        <div className="flex items-center gap-2 text-sm text-gray-500">
                            {policy.linked_frameworks && policy.linked_frameworks.split(',').map(fw => (
                                <span key={fw} className="px-2 py-0.5 bg-gray-100 border border-gray-200 rounded text-xs font-medium">{fw.trim()}</span>
                            ))}
                        </div>
                    </div>
                </div>
                <div className="flex gap-3">
                    {/* Language Selector Mock */}
                    <select className="border-gray-300 rounded-md text-sm text-gray-600 shadow-sm focus:border-indigo-500 focus:ring-indigo-500">
                        <option>English</option>
                    </select>
                    <button
                        onClick={() => window.open(`/print/policy/${policy.id}`, '_blank')}
                        className="px-3 py-1.5 bg-white border border-gray-200 text-gray-700 rounded-md text-sm font-medium hover:bg-gray-50 shadow-sm transition-colors"
                    >
                        <Download className="w-4 h-4 inline mr-1" /> Download PDF
                    </button>
                    <button className="px-3 py-1.5 bg-white border border-gray-200 text-gray-700 rounded-md text-sm font-medium hover:bg-gray-50 shadow-sm">
                        More
                    </button>
                </div>
            </div>

            {/* Content Area - Timeline View */}
            <div className="max-w-4xl mx-auto mt-8 space-y-6 px-4">

                {/* Draft Card (Condition: Status is Draft/Review or Pending) */}
                {isDraft && (
                    <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
                        <div className="p-6 flex justify-between items-start border-b border-gray-100">
                            <div>
                                <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                                    Draft
                                    {policy.status === 'Pending Approval' && (
                                        <span className="px-2 py-0.5 bg-amber-100 text-amber-800 text-xs rounded-full border border-amber-200">Pending Approval</span>
                                    )}
                                </h2>
                                <p className="text-sm text-gray-500 mt-1">
                                    Last edited by {policy.owner} • {new Date(policy.updated_at).toLocaleDateString()}
                                </p>
                                <div className="flex gap-2 mt-3">
                                    <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-gray-100 text-xs font-medium text-gray-600">
                                        <Clock className="w-3 h-3" /> Needs approval
                                    </span>
                                    <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-blue-50 text-xs font-medium text-blue-700">
                                        <Edit3 className="w-3 h-3" /> Created with policy editor
                                    </span>
                                    {policy.master_template_id && (
                                        <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-purple-50 text-xs font-medium text-purple-700">
                                            Based on Gold Standard
                                        </span>
                                    )}
                                </div>
                            </div>
                            <div className="flex gap-2">
                                <button
                                    onClick={handleApprovalRequest}
                                    disabled={policy.status === 'Pending Approval'}
                                    className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 shadow-sm flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    {policy.status === 'Pending Approval' ? (
                                        <>Request Sent</>
                                    ) : (
                                        <>Submit for approval <Send className="w-4 h-4" /></>
                                    )}

                                </button>
                                <button
                                    onClick={() => setIsEditorOpen(true)}
                                    className="px-4 py-2 bg-white border border-gray-200 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-50 shadow-sm"
                                >
                                    Edit
                                </button>
                                <button className="p-2 hover:bg-gray-100 rounded-lg text-gray-500">
                                    <MoreHorizontal className="w-5 h-5" />
                                </button>
                            </div>
                        </div>
                        {/* Preview Snippet */}
                        <div className="p-8 bg-gray-50/50 min-h-[200px] border-t border-gray-100">
                            <div className="bg-white shadow-sm border border-gray-200 p-8 rounded-lg max-w-3xl mx-auto opacity-75 select-none pointer-events-none transform scale-[0.98] origin-top">
                                <div className="h-4 bg-gray-200 rounded w-1/3 mb-6"></div>
                                <div className="space-y-3">
                                    <div className="h-2 bg-gray-200 rounded w-full"></div>
                                    <div className="h-2 bg-gray-200 rounded w-5/6"></div>
                                    <div className="h-2 bg-gray-200 rounded w-4/6"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* Vertical Connector Line */}
                {isDraft && <div className="h-8 border-l-2 border-dashed border-gray-300 mx-auto w-0"></div>}

                {/* Approved Version Card */}
                <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden opacity-90">
                    <div className="p-6 flex justify-between items-start">
                        <div>
                            <h2 className="text-lg font-bold text-gray-900">
                                Version {isDraft ? (parseFloat(policy.version) - 0.1).toFixed(1) : policy.version} (Feb 28 2023)
                            </h2>
                            <p className="text-sm text-gray-500 mt-1">
                                Last edited by {policy.owner} • Approved by Admin
                            </p>
                            <div className="flex gap-2 mt-3">
                                <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-green-100 text-xs font-medium text-green-700">
                                    <CheckCircle className="w-3 h-3" /> Active
                                </span>
                                <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-gray-100 text-xs font-medium text-gray-600">
                                    <FileText className="w-3 h-3" /> Created with policy editor
                                </span>
                            </div>
                        </div>
                        <div className="flex gap-2">
                            <button
                                onClick={() => setIsEditorOpen(true)}
                                className="px-4 py-2 bg-white border border-gray-200 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-50 shadow-sm transition-colors"
                            >
                                View
                            </button>
                        </div>
                    </div>
                    {/* Collapsed Preview Snippet */}
                    <div className="p-6 bg-gray-50/50 border-t border-gray-100 cursor-pointer hover:bg-gray-100 transition-colors" onClick={() => setIsEditorOpen(true)}>
                        <div className="bg-white shadow-sm border border-gray-200 p-6 rounded-lg max-w-3xl mx-auto select-none pointer-events-none">
                            <div className="space-y-2 opacity-50">
                                <div className="h-2 bg-gray-200 rounded w-full"></div>
                                <div className="h-2 bg-gray-200 rounded w-3/4"></div>
                                <div className="h-2 bg-gray-200 rounded w-5/6"></div>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="flex justify-center pt-8 pb-12">
                    <button className="text-sm text-gray-500 hover:text-gray-700 flex items-center gap-2">
                        <History className="w-4 h-4" /> View older versions
                    </button>
                </div>

            </div >

            {/* Full Screen Editor Modal */}
            {
                isEditorOpen && (
                    <PolicyEditor
                        policy={policy}
                        masterContent={masterContent} // Pass master content for Split View
                        onRestore={handleRestore}     // Pass restore handler
                        readOnly={policy.status === 'Approved'}
                        onClose={() => setIsEditorOpen(false)}
                        onSave={() => {
                            setIsEditorOpen(false);
                            fetchPolicy();
                        }}
                    />
                )
            }
        </div >
    );
};

export default PolicyDetail;
