import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
    Download, FileText, CheckCircle, XCircle, AlertCircle, Search
} from 'lucide-react';

const API_URL = 'http://localhost:8000/api/v1';

const StatementOfApplicability = () => {
    const [controls, setControls] = useState([]);
    const [loading, setLoading] = useState(true);
    const [stats, setStats] = useState({ total: 0, applicable: 0, excluded: 0 });

    const [selectedFramework, setSelectedFramework] = useState(1); // Default ISO 27001
    const [frameworks, setFrameworks] = useState([]);

    useEffect(() => {
        // Fetch available frameworks for the dropdown
        const fetchFrameworks = async () => {
            try {
                const token = localStorage.getItem('access_token');
                const res = await axios.get(`${API_URL}/frameworks/`, { headers: { Authorization: `Bearer ${token}` } });
                setFrameworks(res.data);
            } catch (e) { console.error("Error fetching frameworks", e); }
        };
        fetchFrameworks();
    }, []);

    useEffect(() => {
        fetchSoAData();
    }, [selectedFramework]);

    const fetchSoAData = async () => {
        try {
            setLoading(true);
            const token = localStorage.getItem('access_token');
            const headers = { Authorization: `Bearer ${token}` };

            const res = await axios.get(`${API_URL}/controls/?framework_id=${selectedFramework}`, { headers });

            const allControls = res.data;
            setControls(allControls);

            setStats({
                total: allControls.length,
                applicable: allControls.filter(c => c.is_applicable !== false).length,
                excluded: allControls.filter(c => c.is_applicable === false).length
            });

            setLoading(false);
        } catch (error) {
            console.error("Failed to fetch SoA data", error);
            setLoading(false);
        }
    };

    if (loading) return <div className="p-12 text-center text-gray-500">Loading SoA...</div>;

    return (
        <div className="p-8 bg-gray-50 min-h-screen">
            <div className="max-w-7xl mx-auto space-y-6">

                {/* HEADER */}
                <div className="flex justify-between items-start">
                    <div>
                        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                            <ShieldIcon /> Statement of Applicability
                        </h1>
                        <div className="flex items-center gap-2 mt-1">
                            <span className="text-gray-500">Framework:</span>
                            <select
                                value={selectedFramework}
                                onChange={(e) => setSelectedFramework(e.target.value)}
                                className="bg-white border border-gray-300 rounded px-2 py-1 text-sm focus:outline-none focus:border-blue-500"
                            >
                                {frameworks.map(fw => (
                                    <option key={fw.id} value={fw.id}>{fw.name} ({fw.code})</option>
                                ))}
                            </select>
                        </div>
                    </div>
                    <div className="flex gap-3">
                        <button className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 font-medium text-sm">
                            <FileText className="w-4 h-4" /> Executive Summary (PDF)
                        </button>
                        <button className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium text-sm">
                            <Download className="w-4 h-4" /> Download SoA (.xlsx)
                        </button>
                    </div>
                </div>

                {/* TABS */}
                <div className="border-b border-gray-200">
                    <div className="flex gap-8">
                        <button className="pb-4 border-b-2 border-blue-600 text-blue-600 font-medium text-sm">
                            SoA Preview (Live)
                        </button>
                        <button className="pb-4 border-b-2 border-transparent text-gray-500 hover:text-gray-700 font-medium text-sm">
                            Configuration & Scoping
                        </button>
                    </div>
                </div>

                {/* STATS CARDS */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <StatCard title="TOTAL CONTROLS" value={stats.total} sub="ISO 27001:2022 Annex A" />
                    <StatCard title="APPLICABLE" value={stats.applicable} sub="In Scope for Audit" color="text-green-600" />
                    <StatCard title="EXCLUDED" value={stats.excluded} sub="Justification Required" color="text-red-600" />
                </div>

                {/* TABLE CARD */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                    <div className="p-4 border-b border-gray-200 bg-gray-50 flex justify-between items-center">
                        <h3 className="font-bold text-gray-900">Preview: Annex A Applicability Matrix</h3>
                        <div className="px-2 py-1 bg-blue-100 text-blue-700 text-xs font-bold rounded uppercase">
                            Live Preview
                        </div>
                    </div>

                    <div className="overflow-x-auto">
                        <table className="w-full text-sm text-left">
                            <thead className="text-xs text-gray-500 uppercase bg-gray-50 border-b border-gray-200">
                                <tr>
                                    <th className="px-6 py-3 font-medium">ID</th>
                                    <th className="px-6 py-3 font-medium w-1/3">Control Name</th>
                                    <th className="px-6 py-3 font-medium">Applicability</th>
                                    <th className="px-6 py-3 font-medium">Justification Category & Detail</th>
                                    <th className="px-6 py-3 font-medium">Method</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-100">
                                {controls.map(control => (
                                    <tr key={control.id} className="hover:bg-gray-50">
                                        <td className="px-6 py-4 font-medium text-gray-900 whitespace-nowrap">
                                            {control.control_id}
                                        </td>
                                        <td className="px-6 py-4 text-gray-900">
                                            {control.title}
                                        </td>
                                        <td className="px-6 py-4">
                                            {control.is_applicable !== false ? (
                                                <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                                    <CheckCircle className="w-3 h-3" /> YES
                                                </span>
                                            ) : (
                                                <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                                                    <XCircle className="w-3 h-3" /> NO
                                                </span>
                                            )}
                                        </td>
                                        <td className="px-6 py-4">
                                            <div className="flex flex-col">
                                                <span className="font-bold text-xs text-gray-700 uppercase mb-1">
                                                    {control.justification || 'RISK TREATMENT'}
                                                </span>
                                                <span className="text-gray-500 text-xs italic">
                                                    {control.justification_reason || 'Standard requirement included in scope.'}
                                                </span>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 text-gray-500">
                                            {control.implementation_method || 'N/A'}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>

            </div>
        </div>
    );
};

const StatCard = ({ title, value, sub, color = "text-gray-900" }) => (
    <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
        <h4 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">{title}</h4>
        <div className={`text-4xl font-extrabold mb-1 ${color}`}>{value}</div>
        <div className="text-sm text-gray-400">{sub}</div>
    </div>
);

const ShieldIcon = () => (
    <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
    </svg>
);

export default StatementOfApplicability;
