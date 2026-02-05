import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Download, Activity, RefreshCw } from 'lucide-react';

const API_URL = "http://localhost:8000/api/v1";

const ComplianceHealth = () => {
    const [stats, setStats] = useState([]);
    const [loading, setLoading] = useState(true);
    const [scanning, setScanning] = useState(false);
    const [selectedModule, setSelectedModule] = useState('All');
    const [selectedDomain, setSelectedDomain] = useState('All');

    useEffect(() => {
        fetchStats();
    }, []);

    const fetchStats = async () => {
        try {
            const token = localStorage.getItem('access_token');
            const res = await axios.get(`${API_URL}/compliance/stats`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setStats(res.data);
            setLoading(false);
        } catch (error) {
            console.error("Error fetching stats:", error);
            setLoading(false);
        }
    };

    const triggerScan = async () => {
        setScanning(true);
        try {
            const token = localStorage.getItem('access_token');
            await axios.post(`${API_URL}/compliance/scan`, {}, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setTimeout(() => {
                fetchStats();
                setScanning(false);
            }, 3000);
        } catch (error) {
            console.error("Error triggering scan:", error);
            setScanning(false);
        }
    };

    const downloadReport = async () => {
        try {
            const token = localStorage.getItem('access_token');
            const response = await axios.get(`${API_URL}/compliance/report/pdf`, {
                headers: { Authorization: `Bearer ${token}` },
                responseType: 'blob',
            });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', 'AI_Compliance_Report.pdf');
            document.body.appendChild(link);
            link.click();
        } catch (error) {
            console.error("Error downloading report:", error);
        }
    };

    if (loading) return <div className="p-8"><p>Loading Compliance Data...</p></div>;

    // Flatten data for grid
    // Assuming stats structure contains details, otherwise we might need a separate /compliance/details endpoint
    // For MVP, we can mock the detail list or fetch it if available.
    // The previous implementation of `ingest_ai_modules.py` created RequirementMaster data.
    // We'll create a new endpoint call or just visualize what we have for now.
    // Since the user wants "Module -> Domain" filtering, we really need the raw requirement data.

    // For now, let's assume we can fetch detailed requirements. I'll add a fetch for it.

    return (
        <div className="p-8 space-y-8 bg-gray-50 min-h-screen">
            {/* Header */}
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-bold flex items-center gap-2 text-gray-900">
                        <Activity className="w-8 h-8 text-indigo-600" />
                        AI Compliance Mapping Report
                    </h1>
                    <p className="text-gray-500">ISO 42001 & AI Framework Analysis</p>
                </div>
                <div className="flex gap-3">
                    <button
                        onClick={triggerScan}
                        disabled={scanning}
                        className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 flex items-center gap-2 disabled:opacity-50"
                    >
                        <RefreshCw className={`w-4 h-4 ${scanning ? 'animate-spin' : ''}`} />
                        {scanning ? "Scanning..." : "Update Mappings"}
                    </button>
                    <button
                        onClick={downloadReport}
                        className="px-4 py-2 border border-gray-300 bg-white rounded hover:bg-gray-50 flex items-center gap-2 text-gray-700"
                    >
                        <Download className="w-4 h-4" />
                        Export to Excel
                    </button>
                </div>
            </div>

            {/* High Level Stats */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {stats.map((mod) => (
                    <div key={mod.module} className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                        <h3 className="font-semibold text-gray-700 mb-2">{mod.module}</h3>
                        <div className="flex items-end gap-2 mb-2">
                            <span className="text-3xl font-bold text-gray-900">{mod.score}%</span>
                            <span className="text-sm text-gray-500 mb-1">compliant</span>
                        </div>
                        <div className="w-full bg-gray-100 rounded-full h-2 mb-3">
                            <div
                                className={`h-2 rounded-full ${mod.score >= 80 ? 'bg-green-500' : mod.score >= 50 ? 'bg-yellow-500' : 'bg-red-500'}`}
                                style={{ width: `${mod.score}%` }}
                            ></div>
                        </div>
                        <div className="text-xs text-gray-500">
                            {mod.met} / {mod.total} Requirements Met
                        </div>
                    </div>
                ))}
            </div>

            {/* Detailed Filterable Report */}
            <div className="bg-white border border-gray-200 rounded-xl shadow-sm p-6">
                <div className="flex justify-between items-center mb-6">
                    <h3 className="font-bold text-lg text-gray-900">Detailed Mapping Analysis</h3>
                    <div className="flex gap-3">
                        <select
                            className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-indigo-500 focus:border-indigo-500 block p-2.5"
                            value={selectedModule}
                            onChange={(e) => setSelectedModule(e.target.value)}
                        >
                            <option value="All">All Modules</option>
                            {stats.map(s => <option key={s.module} value={s.module}>{s.module}</option>)}
                        </select>
                        <select
                            className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-indigo-500 focus:border-indigo-500 block p-2.5"
                            value={selectedDomain}
                            onChange={(e) => setSelectedDomain(e.target.value)}
                        >
                            <option value="All">All Domains</option>
                            {/* Ideally populate domains dynamically based on selected module */}
                            <option value="Governance">Governance</option>
                            <option value="Risk Management">Risk Management</option>
                        </select>
                    </div>
                </div>

                {/* Data Grid Placeholder (Needs backend endpoint for detailed list) */}
                <div className="overflow-x-auto">
                    <table className="w-full text-sm text-left text-gray-500">
                        <thead className="text-xs text-gray-700 uppercase bg-gray-50">
                            <tr>
                                <th className="px-6 py-3">ID</th>
                                <th className="px-6 py-3">Requirement</th>
                                <th className="px-6 py-3">Status</th>
                                <th className="px-6 py-3">Mapped Policies/Controls</th>
                                <th className="px-6 py-3">Gap Analysis</th>
                            </tr>
                        </thead>
                        <tbody>
                            {/* 
                                TODO: We need to fetch the actual requirements list here.
                                For now, I will show a placeholder row or fetch if possible.
                                To fix this properly, I'll update the component to fetch from a new endpoint /compliance/details
                             */}
                            <tr className="bg-white border-b hover:bg-gray-50">
                                <td className="px-6 py-4 font-medium text-gray-900">AI-01</td>
                                <td className="px-6 py-4">Define AI Roles and Responsibilities</td>
                                <td className="px-6 py-4"><span className="bg-green-100 text-green-800 text-xs font-medium px-2.5 py-0.5 rounded">MET</span></td>
                                <td className="px-6 py-4">Information Security Policy</td>
                                <td className="px-6 py-4">-</td>
                            </tr>
                        </tbody>
                    </table>
                    <div className="p-4 text-center text-gray-500 text-sm italic">
                        (Displaying sample data - Detailed grid requires new API endpoint)
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ComplianceHealth;
