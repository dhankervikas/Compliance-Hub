
import React, { useState, useEffect } from 'react';
import { useEntitlements } from '../contexts/EntitlementContext';
import axios from 'axios';
import {
    LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
    PieChart, Pie, Cell
} from 'recharts';
import { CheckCircle, Shield, FileSpreadsheet, Lock, GitBranch, TrendingUp } from 'lucide-react';
import { generateSoA } from '../utils/soaGenerator';

import config from '../config';
const API_URL = config.API_BASE_URL;

const ReportHeader = ({ confidence, framework }) => (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 mb-8 flex justify-between items-center">
        <div>
            <div className="flex items-center gap-2 mb-1">
                <Shield className="text-blue-600 w-5 h-5" />
                <span className="text-xs font-bold text-gray-500 uppercase tracking-widest">Compliance Report</span>
            </div>
            <h1 className="text-2xl font-bold text-gray-900">{framework} Applicability & Status</h1>
            <p className="text-sm text-gray-500 mt-1">Generated: {new Date().toLocaleDateString()}</p>
        </div>
        <div className="text-right">
            <div className="text-sm text-gray-500 mb-1">Data Confidence Score</div>
            <div className="text-3xl font-bold text-green-600 flex items-center justify-end gap-2">
                {confidence}%
                <CheckCircle className="w-5 h-5" />
            </div>
        </div>
    </div>
);

// NEW EXPORT: ENCRYPTION MATRIX
const EncryptionMatrix = ({ data }) => (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 col-span-1 md:col-span-2">
        <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
            <Lock className="text-blue-500 w-5 h-5" />
            Control A.8.24: Cryptography Matrix
        </h3>
        <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
                <thead className="text-xs text-gray-500 uppercase bg-gray-50">
                    <tr>
                        <th className="px-4 py-3">Resource Type</th>
                        <th className="px-4 py-3">Volume ID</th>
                        <th className="px-4 py-3">Status</th>
                        <th className="px-4 py-3">Algorithm</th>
                        <th className="px-4 py-3">Metadata</th>
                    </tr>
                </thead>
                <tbody>
                    {data.map((item, i) => (
                        <tr key={i} className="border-b border-gray-100 hover:bg-gray-50">
                            <td className="px-4 py-3 font-medium">{item.resource_type}</td>
                            <td className="px-4 py-3 font-mono text-xs">{item.volume_id}</td>
                            <td className="px-4 py-3">
                                <span className={`px-2 py-1 rounded text-xs font-bold ${item.encryption_status === 'ENCRYPTED' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                                    }`}>
                                    {item.encryption_status}
                                </span>
                            </td>
                            <td className="px-4 py-3">{item.algorithm}</td>
                            <td className="px-4 py-3 text-gray-400 text-xs">Verified by AWS Config</td>
                        </tr>
                    ))}
                </tbody>
            </table>
            {data.length === 0 && <p className="text-center text-gray-400 py-4">No encryption data available.</p>}
        </div>
    </div>
);

// NEW EXPORT: GITHUB METRICS
const GitHubMetrics = ({ data }) => (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
        <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
            <GitBranch className="text-purple-500 w-5 h-5" />
            Control A.8.28: Secure SDLC
        </h3>
        <div className="space-y-4">
            {data.map((repo, i) => (
                <div key={i} className="flex justify-between items-center p-3 border rounded-lg hover:bg-gray-50">
                    <div>
                        <div className="font-bold text-gray-900 flex items-center gap-2">
                            {repo.repository}
                            {repo.branch_protection === 'ENABLED' && <CheckCircle size={14} className="text-green-500" />}
                        </div>
                        <div className="text-xs text-gray-500">PR Reviews Required: {repo.pr_reviews_required}</div>
                    </div>
                    <div className="text-right">
                        <span className={`px-2 py-1 rounded text-xs font-bold ${repo.branch_protection === 'ENABLED' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                            }`}>
                            {repo.branch_protection}
                        </span>
                    </div>
                </div>
            ))}
            {data.length === 0 && <p className="text-center text-gray-400 py-4">No repository data available.</p>}
        </div>
    </div>
);

const ReportsDashboard = () => {
    const { entitlements } = useEntitlements();
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [generatingPack, setGeneratingPack] = useState(false);

    const [mappingData, setMappingData] = useState([]);

    useEffect(() => {
        fetchData();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const fetchData = async () => {
        try {
            const token = localStorage.getItem('token');
            const headers = { Authorization: `Bearer ${token}` };

            const res = await axios.get(`${API_URL}/reports/dashboard`, { headers });
            let reportData = res.data;

            // STRICT FILTERING: Hide inactive frameworks from Coverage Chart
            if (reportData.framework_coverage && entitlements && entitlements.frameworks) {
                const activeCodes = new Set(entitlements.frameworks.filter(f => f.is_active).map(f => f.name));
                // Note: Chart uses 'name' e.g. "ISO 27001:2022". Logic must match.
                // If chart data uses codes, we'd map codes.
                // Assuming Name matching for now based on screenshot.
                reportData.framework_coverage = reportData.framework_coverage.filter(item =>
                    activeCodes.has(item.name) || entitlements.frameworks.some(f => f.is_active && f.name === item.name)
                );
            }

            setData(reportData);

            // Fetch Mapping Data
            const mapRes = await axios.get(`${API_URL}/reports/ai-mapping`, { headers });
            if (mapRes.data?.data) {
                setMappingData(mapRes.data.data);
            }

            setLoading(false);
        } catch (err) {
            console.error("Failed to fetch reports", err);
            setError(err.message || "Failed to load report data");
            setLoading(false);
        }
    };

    // MAPPING TABLE COMPONENT
    const MappingTable = ({ data }) => {
        const [searchTerm, setSearchTerm] = useState('');
        const [selectedModule, setSelectedModule] = useState('All');
        const [selectedDomain, setSelectedDomain] = useState('All');

        if (!data || data.length === 0) return null;

        // Extract unique values for filters
        const modules = ['All', ...new Set(data.map(d => d['AI Category']).filter(Boolean))];
        const domains = ['All', ...new Set(data.map(d => d['AI Domain']).filter(Boolean))];

        const filtered = data.filter(row => {
            const matchesSearch =
                row["Genie Control Title"]?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                row["Mapped ISO 42001 ID"]?.toLowerCase().includes(searchTerm.toLowerCase());

            const matchesModule = selectedModule === 'All' || row["AI Category"] === selectedModule;
            const matchesDomain = selectedDomain === 'All' || row["AI Domain"] === selectedDomain;

            return matchesSearch && matchesModule && matchesDomain;
        });

        return (
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 col-span-1 md:col-span-2 mt-8">
                <div className="flex flex-col md:flex-row justify-between items-center mb-6 gap-4">
                    <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                        <TrendingUp className="text-indigo-500 w-5 h-5" />
                        Genie Framework to ISO 42001 Mapping
                    </h3>

                    <div className="flex flex-wrap gap-2">
                        {/* Module Filter */}
                        <select
                            className="border border-gray-300 rounded px-3 py-1 text-sm bg-white"
                            value={selectedModule}
                            onChange={(e) => setSelectedModule(e.target.value)}
                        >
                            {modules.map(m => <option key={m} value={m}>Module: {m}</option>)}
                        </select>

                        {/* Domain Filter */}
                        <select
                            className="border border-gray-300 rounded px-3 py-1 text-sm bg-white"
                            value={selectedDomain}
                            onChange={(e) => setSelectedDomain(e.target.value)}
                        >
                            {domains.map(d => <option key={d} value={d}>Domain: {d}</option>)}
                        </select>

                        <input
                            type="text"
                            placeholder="Search controls..."
                            className="border border-gray-300 rounded px-3 py-1 text-sm"
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                    </div>
                </div>

                <div className="overflow-x-auto max-h-[600px] overflow-y-auto">
                    <table className="w-full text-sm text-left">
                        <thead className="text-xs text-gray-500 uppercase bg-gray-50 sticky top-0 z-10 shadow-sm">
                            <tr>
                                <th className="px-4 py-3 bg-gray-50">Genie ID & Domain</th>
                                <th className="px-4 py-3 bg-gray-50">Control Details</th>
                                <th className="px-4 py-3 bg-gray-50">Requirements</th>
                                <th className="px-4 py-3 bg-gray-50">ISO 42001 Match</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-100">
                            {filtered.map((row, i) => (
                                <tr key={i} className="hover:bg-gray-50 align-top">
                                    {/* ID & Domain */}
                                    <td className="px-4 py-3 whitespace-nowrap">
                                        <div className="font-bold text-gray-900">{row["AI Control ID"]}</div>
                                        <div className="text-xs inline-block bg-blue-100 text-blue-800 px-2 py-0.5 rounded mt-1">
                                            {row["AI Domain"]}
                                        </div>
                                        <div className="text-xs text-gray-400 mt-1">{row["AI Category"]}</div>
                                    </td>

                                    {/* Description (Title) */}
                                    <td className="px-4 py-3 min-w-[200px]">
                                        <div className="font-medium text-gray-800">{row["Genie Control Title"]}</div>
                                    </td>

                                    {/* Requirements */}
                                    <td className="px-4 py-3 min-w-[300px]">
                                        <div className="text-xs text-gray-600 whitespace-pre-wrap">
                                            {row["Requirements"] || "-"}
                                        </div>
                                    </td>

                                    {/* ISO Match */}
                                    <td className="px-4 py-3 whitespace-nowrap">
                                        <span className="bg-indigo-50 text-indigo-700 px-2 py-1 rounded text-xs font-bold font-mono">
                                            {row["Mapped ISO 42001 ID"]}
                                        </span>
                                        <div className="text-xs text-gray-500 mt-1 w-48 truncate" title={row["Mapped ISO 42001 Title"]}>
                                            {row["Mapped ISO 42001 Title"]}
                                        </div>
                                        <div className="text-[10px] text-gray-400 mt-1 italic">
                                            {row["Mapping Rationale"]}
                                        </div>
                                    </td>
                                </tr>
                            ))}
                            {filtered.length === 0 && (
                                <tr><td colSpan="4" className="text-center py-8 text-gray-500">No matches found for the selected filters</td></tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        );
    };

    const handleDownloadSoA = async () => {
        if (!data) return;
        setGeneratingPack(true);
        try {
            const token = localStorage.getItem('token');
            const controlsRes = await axios.get(`${API_URL}/frameworks/ISO27001_2022/controls`, {
                headers: { Authorization: `Bearer ${token}` }
            });

            // We need evidence list too (from dashboard data or separate call)
            // Using mock empty list for now if not available in dashboard response
            const evidenceList = data.evidence_summary || [];

            const buffer = await generateSoA("ISO 27001:2022", controlsRes.data, evidenceList);

            const blob = new Blob([buffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `SoA_ISO27001_${new Date().toISOString().split('T')[0]}.xlsx`);
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (err) {
            console.error(err);
            alert("Failed to generate SoA Excel");
        } finally {
            setGeneratingPack(false);
        }
    };

    if (loading) return <div className="p-12 text-center text-gray-400">Loading Reporting Engine...</div>;
    if (error) return <div className="p-12 text-center text-red-500">{error}</div>;

    const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

    return (
        <div className="min-h-screen bg-gray-50 pb-20 p-8 animate-fade-in">
            <div className="max-w-7xl mx-auto">
                <div className="flex justify-between items-center mb-6">
                    <h2 className="text-xl font-bold text-gray-800">Elite Compliance Reports</h2>
                    <div className="flex gap-2">
                        <button
                            onClick={handleDownloadSoA}
                            disabled={generatingPack}
                            className="bg-green-600 text-white px-4 py-2 rounded-lg font-bold flex items-center gap-2 hover:bg-green-700 transition-colors shadow-lg disabled:opacity-70"
                        >
                            <FileSpreadsheet className="w-4 h-4" />
                            {generatingPack ? "Generating Excel..." : "Download SoA (.xlsx)"}
                        </button>
                        <a
                            href={`${API_URL.replace('/api/v1', '')}/static/reports/AI_ISO_42001_Mapping_Report.xlsx?t=${new Date().getTime()}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="bg-indigo-600 text-white px-4 py-2 rounded-lg font-bold flex items-center gap-2 hover:bg-indigo-700 transition-colors shadow-lg"
                        >
                            <TrendingUp className="w-4 h-4" />
                            Genie Standards Mapping (.xlsx)
                        </a>
                    </div>
                </div>

                <ReportHeader confidence={data.meta.confidence_score} framework="ISO 27001:2022" />

                <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
                    {/* CHART 1: DRIFT TREND (Historical Data) */}
                    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                        <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                            <TrendingUp className="text-blue-500 w-5 h-5" />
                            Compliance Trend (Year-over-Year)
                        </h3>
                        <div className="h-64">
                            <ResponsiveContainer width="100%" height="100%">
                                <LineChart data={data.drift_trend}>
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis dataKey="date" />
                                    <YAxis />
                                    <Tooltip />
                                    <Legend />
                                    <Line type="monotone" dataKey="passing" stroke="#22c55e" name="Compliance Score" strokeWidth={3} />
                                </LineChart>
                            </ResponsiveContainer>
                        </div>
                    </div>

                    {/* WIDGET: SECURE SDLC */}
                    <GitHubMetrics data={data.github_metrics || []} />

                    {/* WIDGET: ENCRYPTION MATRIX */}
                    <EncryptionMatrix data={data.encryption_matrix || []} />

                    {/* CHART 3: FRAMEWORK COVERAGE */}
                    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                        <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                            <Shield className="text-purple-500 w-5 h-5" />
                            Framework Coverage
                        </h3>
                        <div className="h-64 flex justify-center">
                            <ResponsiveContainer width="100%" height="100%">
                                <PieChart>
                                    <Pie
                                        data={data.framework_coverage}
                                        cx="50%"
                                        cy="50%"
                                        innerRadius={60}
                                        outerRadius={80}
                                        fill="#8884d8"
                                        paddingAngle={5}
                                        dataKey="coverage"
                                        nameKey="name"
                                        label={({ name, coverage }) => `${name}: ${coverage}%`}
                                    >
                                        {data.framework_coverage.map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                        ))}
                                    </Pie>
                                    <Tooltip />
                                </PieChart>
                            </ResponsiveContainer>
                        </div>
                    </div>

                    {/* NEW: AI MAPPING TABLE - Conditional Rendering */}
                    <div className="col-span-1 md:col-span-2">
                        {entitlements?.frameworks?.some(f => f.is_active && (f.code.includes("ISO42001") || f.code.includes("AI"))) && (
                            <MappingTable data={mappingData} />
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ReportsDashboard;
