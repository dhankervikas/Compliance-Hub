import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FileText, Folder, CheckCircle, Clock, AlertCircle, Plus, Search, ChevronRight } from 'lucide-react';
import axios from '../services/api';

const PoliciesDashboard = () => {
    const navigate = useNavigate();
    const [policies, setPolicies] = useState([]);
    const [loading, setLoading] = useState(true);
    const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'list'

    // Mock Folders (since we don't have a structured backend for folders yet, we group by 'folder' string)
    const folders = [
        { id: 'governance', name: '01_Governance', label: 'Governance & Strategy', color: 'bg-blue-50 text-blue-700' },
        { id: 'people', name: '02_People', label: 'People & HR', color: 'bg-purple-50 text-purple-700' },
        { id: 'physical', name: '03_Physical', label: 'Physical Security', color: 'bg-green-50 text-green-700' },
        { id: 'technology', name: '04_Technology', label: 'Technology & Operations', color: 'bg-indigo-50 text-indigo-700' },
        { id: 'compliance', name: '05_Compliance', label: 'Legal & Compliance', color: 'bg-orange-50 text-orange-700' },
    ];

    useEffect(() => {
        fetchPolicies();
    }, []);

    const fetchPolicies = async () => {
        try {
            const res = await axios.get('/policies');
            setPolicies(res.data);
        } catch (err) {
            console.error("Failed to fetch policies", err);
        } finally {
            setLoading(false);
        }
    };

    // Helper to group policies
    const getPoliciesInFolder = (folderName) => {
        return policies.filter(p => p.folder && p.folder.toLowerCase().includes(folderName.split('_')[1].toLowerCase()));
    };

    const calculateProgress = (folderParams) => {
        const folderPolicies = getPoliciesInFolder(folderParams.name);
        if (!folderPolicies.length) return 0;
        const approved = folderPolicies.filter(p => p.status === 'Approved').length;
        return Math.round((approved / folderPolicies.length) * 100);
    };

    return (
        <div className="min-h-screen bg-gray-50/50 p-6">
            <div className="flex justify-between items-center mb-8">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">Policy Library</h1>
                    <p className="text-sm text-gray-500 mt-1">Manage, approve, and attestation for ISMS policies.</p>
                </div>
                <div className="flex gap-3">
                    <button className="px-4 py-2 bg-white border border-gray-200 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-50 flex items-center gap-2">
                        <Clock className="w-4 h-4" /> Audit Log
                    </button>
                    <button className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 flex items-center gap-2">
                        <Plus className="w-4 h-4" /> New Policy
                    </button>
                </div>
            </div>

            {/* Folder Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-10">
                {folders.map(folder => {
                    const progress = calculateProgress(folder);
                    const count = getPoliciesInFolder(folder.name).length;

                    return (
                        <div key={folder.id} className="bg-white border border-gray-200 rounded-xl p-5 hover:shadow-md transition-shadow cursor-pointer" onClick={() => console.log("Filter by folder")}>
                            <div className="flex justify-between items-start mb-4">
                                <div className={`p-3 rounded-lg ${folder.color}`}>
                                    <Folder className="w-6 h-6" />
                                </div>
                                <span className="text-xs font-semibold bg-gray-100 text-gray-600 px-2 py-1 rounded-full">
                                    {count} Files
                                </span>
                            </div>
                            <h3 className="text-lg font-bold text-gray-900 mb-1">{folder.label}</h3>
                            <p className="text-xs text-gray-500 mb-4 font-mono">{folder.name}</p>

                            {/* Progress Bar */}
                            <div className="w-full bg-gray-100 rounded-full h-2 mb-2">
                                <div className="bg-green-500 h-2 rounded-full transition-all duration-500" style={{ width: `${progress}%` }}></div>
                            </div>
                            <div className="flex justify-between text-xs text-gray-500">
                                <span>{progress}% Complete</span>
                                <span>{count > 0 ? `${Math.round((progress / 100) * count)} Approved` : '0 Approved'}</span>
                            </div>
                        </div>
                    );
                })}
            </div>

            {/* Recent Policies List */}
            <div className="bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden">
                <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center bg-gray-50">
                    <h3 className="font-bold text-gray-700">All Policies</h3>
                    <div className="relative">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                        <input type="text" placeholder="Search policies..." className="pl-9 pr-4 py-1.5 text-sm border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500" />
                    </div>
                </div>

                <table className="w-full text-left">
                    <thead className="bg-gray-50 text-xs text-gray-500 uppercase font-semibold">
                        <tr>
                            <th className="px-6 py-3">Policy Name</th>
                            <th className="px-6 py-3">Status</th>
                            <th className="px-6 py-3">Folder</th>
                            <th className="px-6 py-3">Last Updated</th>
                            <th className="px-6 py-3 text-right">Action</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                        {loading ? (
                            <tr><td colSpan="5" className="p-6 text-center text-gray-500">Loading policies...</td></tr>
                        ) : policies.length === 0 ? (
                            <tr><td colSpan="5" className="p-6 text-center text-gray-500">No policies found. Create your first policy.</td></tr>
                        ) : (
                            policies.map(policy => (
                                <tr key={policy.id} className="hover:bg-gray-50 transition-colors group">
                                    <td className="px-6 py-4">
                                        <div className="flex items-center gap-3">
                                            <div className="p-2 bg-indigo-50 text-indigo-600 rounded-lg">
                                                <FileText className="w-5 h-5" />
                                            </div>
                                            <div>
                                                <div className="font-medium text-gray-900 group-hover:text-indigo-600 transition-colors cursor-pointer" onClick={() => navigate(`/policies/${policy.id}`)}>
                                                    {policy.name}
                                                </div>
                                                <div className="text-xs text-gray-500">v{policy.version} • {policy.owner}</div>
                                            </div>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4">
                                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${policy.status === 'Approved' ? 'bg-green-100 text-green-800' :
                                                policy.status === 'Review' ? 'bg-yellow-100 text-yellow-800' :
                                                    'bg-gray-100 text-gray-800'
                                            }`}>
                                            {policy.status}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 text-sm text-gray-500">
                                        {policy.folder || 'Uncategorized'}
                                    </td>
                                    <td className="px-6 py-4 text-sm text-gray-500">
                                        {new Date(policy.updated_at || Date.now()).toLocaleDateString()}
                                    </td>
                                    <td className="px-6 py-4 text-right">
                                        <button onClick={() => navigate(`/policies/${policy.id}`)} className="text-gray-400 hover:text-indigo-600">
                                            <ChevronRight className="w-5 h-5" />
                                        </button>
                                    </td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default PoliciesDashboard;
