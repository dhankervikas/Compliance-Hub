
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Layers, Users, Globe, Plus, Edit2 } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

const ContextPage = () => {
    const [activeTab, setActiveTab] = useState('issues'); // issues, parties, scope
    const [issues, setIssues] = useState([]);
    const [parties, setParties] = useState([]);
    const [scope, setScope] = useState(null);
    const [loading, setLoading] = useState(true);


    // Fetch Data
    useEffect(() => {
        fetchData();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const fetchData = async () => {
        setLoading(true);
        try {
            if (activeTab === 'issues') {
                const res = await axios.get(`${API_BASE_URL} /api/v1 / context / issues`);
                setIssues(res.data);
            } else if (activeTab === 'parties') {
                const res = await axios.get(`${API_BASE_URL} /api/v1 / context / interested - parties`);
                setParties(res.data);
            } else if (activeTab === 'scope') {
                const res = await axios.get(`${API_BASE_URL} /api/v1 / context / scope`);
                setScope(res.data);
            }
        } catch (err) {
            console.error("Failed to fetch context data", err);
        } finally {
            setLoading(false);
        }
    };

    // Render Issues Table
    const renderIssues = () => (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <div className="p-4 border-b border-gray-100 flex justify-between items-center bg-gray-50">
                <h3 className="font-semibold text-gray-800">4.1 Internal & External Issues (PESTLE)</h3>
                <button className="flex items-center gap-2 px-3 py-1.5 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">
                    <Plus size={16} /> Add Issue
                </button>
            </div>
            <table className="w-full text-sm text-left">
                <thead className="text-xs text-gray-500 uppercase bg-gray-50 border-b">
                    <tr>
                        <th className="px-6 py-3">Issue</th>
                        <th className="px-6 py-3">Category</th>
                        <th className="px-6 py-3">PESTLE</th>
                        <th className="px-6 py-3">Impact</th>
                        <th className="px-6 py-3">Treatment / Control</th>
                    </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                    {issues.map((issue) => (
                        <tr key={issue.id} className="hover:bg-gray-50">
                            <td className="px-6 py-4 font-medium text-gray-900">
                                {issue.name}
                                <div className="text-xs text-gray-500 font-normal">{issue.description}</div>
                            </td>
                            <td className="px-6 py-4">
                                <span className={`px - 2 py - 1 rounded - full text - xs font - medium ${issue.category === 'External' ? 'bg-purple-100 text-purple-700' : 'bg-blue-100 text-blue-700'
                                    } `}>
                                    {issue.category}
                                </span>
                            </td>
                            <td className="px-6 py-4 text-gray-600">{issue.pestle_category}</td>
                            <td className="px-6 py-4">
                                <span className={`px - 2 py - 1 rounded - full text - xs font - medium ${issue.impact === 'High' ? 'bg-red-100 text-red-700' :
                                    issue.impact === 'Medium' ? 'bg-orange-100 text-orange-700' : 'bg-green-100 text-green-700'
                                    } `}>
                                    {issue.impact}
                                </span>
                            </td>
                            <td className="px-6 py-4 text-gray-600 max-w-xs truncate" title={issue.treatment}>
                                {issue.treatment}
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );

    // Render Parties Table
    const renderParties = () => (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <div className="p-4 border-b border-gray-100 flex justify-between items-center bg-gray-50">
                <h3 className="font-semibold text-gray-800">4.2 Interested Parties Register</h3>
                <button className="flex items-center gap-2 px-3 py-1.5 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">
                    <Plus size={16} /> Add Party
                </button>
            </div>
            <table className="w-full text-sm text-left">
                <thead className="text-xs text-gray-500 uppercase bg-gray-50 border-b">
                    <tr>
                        <th className="px-6 py-3">Stakeholder</th>
                        <th className="px-6 py-3">Needs & Expectations</th>
                        <th className="px-6 py-3">Requirements</th>
                        <th className="px-6 py-3">Compliance Mapping</th>
                    </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                    {parties.map((party) => (
                        <tr key={party.id} className="hover:bg-gray-50">
                            <td className="px-6 py-4 font-medium text-gray-900">{party.stakeholder}</td>
                            <td className="px-6 py-4 text-gray-600">{party.needs}</td>
                            <td className="px-6 py-4 text-gray-600">{party.requirements}</td>
                            <td className="px-6 py-4">
                                <span className="px-2 py-1 bg-gray-100 text-gray-600 rounded text-xs font-mono">
                                    {party.compliance_mapping}
                                </span>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );

    // Render Scope Document
    const renderScope = () => {
        if (!scope) return <div>Loading Scope...</div>;
        return (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2 space-y-6">
                    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                        <div className="flex justify-between items-start mb-4">
                            <h3 className="text-lg font-bold text-gray-900">4.3 ISMS Scope Document</h3>
                            <button className="text-blue-600 hover:text-blue-800"><Edit2 size={16} /></button>
                        </div>
                        <div className="prose prose-sm max-w-none text-gray-600">
                            <ReactMarkdown>{scope.content}</ReactMarkdown>
                        </div>
                    </div>
                </div>

                <div className="space-y-6">
                    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                        <h4 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                            <Globe size={16} className="text-blue-500" /> Boundaries
                        </h4>
                        <div className="space-y-4">
                            <div>
                                <label className="text-xs font-bold text-gray-500 uppercase">Physical Scope</label>
                                <p className="text-sm text-gray-700 mt-1">{scope.boundaries_physical}</p>
                            </div>
                            <div>
                                <label className="text-xs font-bold text-gray-500 uppercase">Logical / Cloud Scope</label>
                                <p className="text-sm text-gray-700 mt-1">{scope.boundaries_logical}</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    };

    return (
        <div className="p-8 max-w-7xl mx-auto space-y-6 animate-fade-in">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">Organization Context</h1>
                    <p className="text-gray-500 text-sm mt-1">ISO 27001 Clause 4: Define the internal and external context of the ISMS.</p>
                </div>
            </div>

            {/* Tabs */}
            <div className="flex gap-2 border-b border-gray-200 overflow-x-auto">
                <button
                    onClick={() => setActiveTab('issues')}
                    className={`px - 4 py - 2 text - sm font - medium border - b - 2 transition - colors flex items - center gap - 2 whitespace - nowrap ${activeTab === 'issues' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'
                        } `}
                >
                    <Layers size={16} /> 4.1 Context & Issues
                </button>
                <button
                    onClick={() => setActiveTab('parties')}
                    className={`px - 4 py - 2 text - sm font - medium border - b - 2 transition - colors flex items - center gap - 2 whitespace - nowrap ${activeTab === 'parties' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'
                        } `}
                >
                    <Users size={16} /> 4.2 Interested Parties
                </button>
                <button
                    onClick={() => setActiveTab('scope')}
                    className={`px - 4 py - 2 text - sm font - medium border - b - 2 transition - colors flex items - center gap - 2 whitespace - nowrap ${activeTab === 'scope' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'
                        } `}
                >
                    <Globe size={16} /> 4.3 ISMS Scope
                </button>
            </div>

            {/* Content */}
            <div className="min-h-[400px]">
                {loading ? (
                    <div className="flex justify-center py-12 text-gray-400">Loading context data...</div>
                ) : (
                    <>
                        {activeTab === 'issues' && renderIssues()}
                        {activeTab === 'parties' && renderParties()}
                        {activeTab === 'scope' && renderScope()}
                    </>
                )}
            </div>
        </div>
    );
};

export default ContextPage;
