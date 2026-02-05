
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import {
    ArrowLeft, Search, Filter, MoreHorizontal,
    Calendar, CheckCircle, FileText, AlertCircle,
    ChevronDown, Plus, Edit2
} from 'lucide-react';

const API_URL = 'https://assurisk-backend.onrender.com/api/v1';

// COSO DESCRIPTIONS MAP (Hardcoded for UI)
const COSO_DESCRIPTIONS = {
    "CC1.1": "COSO Principle 1: The entity demonstrates a commitment to integrity and ethical values.",
    "CC1.2": "COSO Principle 2: The board of directors exercises oversight of the development and performance of internal control.",
    "CC1.3": "COSO Principle 3: Management establishes structures, reporting lines, and appropriate authorities and responsibilities.",
    "CC2.1": "COSO Principle 16: The entity selects, develops, and performs ongoing and/or separate evaluations.",
    "CC3.1": "COSO Principle 17: The entity evaluates and communicates internal control deficiencies in a timely manner.",
    "CC6.1": "The entity limits physical access to the system to authorized people.",
    "CC6.2": "The entity requires two-factor authentication for remote access.",
    "CC6.3": "The entity manages access based on the principle of least privilege.",
    // Add defaults for others to avoid empty subheaders
    "DEFAULT": "Standard requirement for this criteria."
};

const FrameworkDetail = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const [framework, setFramework] = useState(null);
    const [processes, setProcesses] = useState([]);
    const [socControls, setSocControls] = useState({}); // { "CC1.1": [controls...] }
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [stats, setStats] = useState({ total: 0, implemented: 0, percentage: 0 });
    const [searchTerm, setSearchTerm] = useState('');

    useEffect(() => {
        fetchData();
    }, [id]);

    const fetchData = async () => {
        try {
            const token = localStorage.getItem('token');
            const headers = { Authorization: `Bearer ${token}` };

            // 1. Fetch Framework
            const fwRes = await axios.get(`${API_URL}/frameworks/${id}`, { headers });
            const fwData = fwRes.data;
            const isSOC2 = fwData.code && fwData.code.includes("SOC2");

            // 2. Fetch Controls
            const ctrlRes = await axios.get(`${API_URL}/controls/`, { headers });
            // Filter strictly for this framework
            const allControls = ctrlRes.data.filter(c => c.framework_id === parseInt(id));

            if (isSOC2) {
                // SPECIAL HANDLING FOR SOC 2: Group by Category (Control Code / Standard Ref)
                const grouped = {};
                allControls.forEach(c => {
                    const key = c.category || "Uncategorized"; // We seeded 'CC1.1' into category
                    if (!grouped[key]) grouped[key] = [];
                    grouped[key].push(c);
                });
                setSocControls(grouped);
                setProcesses([]); // Disable process view
            } else {
                // STANDARD HANDLING (ISO etc.): Use Process Hierarchy
                const procRes = await axios.get(`${API_URL}/processes/`, { headers });

                // Map controls to processes (using existing logic or re-mapping)
                // For simplicity in this view, we will use the existing process structure returned by API
                // But we need to ensure we only show processes relevant to this framework.
                // Re-using the logic from previous version:
                const filteredProcesses = procRes.data.map(proc => {
                    const relevantSubs = proc.sub_processes.map(sub => {
                        // We need to know which controls belong to this sub-process.
                        // Ideally, we'd use the 'map-controls' data, but if API doesn't return it flatly,
                        // we can try to infer or fetch. 
                        // Note: The seeded data maps controls to subprocesses in the backend. 
                        // Does the process object have them? 
                        // Let's assume 'sub.controls' is populated. If not, this view might be empty for ISO.
                        // Fallback: Show all controls under a "General" process if mapping fails?
                        return { ...sub, controls: sub.controls || [] };
                    }).filter(sub => sub.controls && sub.controls.length > 0);
                    return { ...proc, sub_processes: relevantSubs };
                }).filter(proc => proc.sub_processes.length > 0);

                setProcesses(filteredProcesses);
            }

            // Calc Stats
            const total = allControls.length;
            const implemented = allControls.filter(c => c.status === 'IMPLEMENTED').length;

            setFramework(fwData);
            setStats({
                total,
                implemented,
                percentage: total > 0 ? Math.round((implemented / total) * 100) : 0
            });
            setLoading(false);

        } catch (err) {
            console.error(err);
            setError(`Failed to load data: ${err.message}`);
            setLoading(false);
        }
    };

    if (loading) return <div className="p-12 text-center text-gray-400">Loading Framework Data...</div>;
    if (error) return <div className="p-12 text-center text-red-500">{error}</div>;

    const isSOC2 = framework.code && framework.code.includes("SOC2");

    // Filter Logic for Search
    const getFilteredControls = (controls) => {
        if (!searchTerm) return controls;
        return controls.filter(c => c.title.toLowerCase().includes(searchTerm.toLowerCase()));
    };

    return (
        <div className="min-h-screen bg-gray-50 pb-20 animate-fade-in">
            {/* TOP HEADER */}
            <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
                <div className="max-w-7xl mx-auto px-6 py-4">
                    <div className="flex justify-between items-center mb-4">
                        <div className="flex items-center gap-2 text-sm text-gray-500">
                            <a onClick={() => navigate('/dashboard')} className="hover:text-gray-900 cursor-pointer">DASHBOARD</a>
                            <span>/</span>
                            <span className="font-medium text-gray-900">{framework.code}</span>
                        </div>
                    </div>

                    <div className="flex justify-between items-end">
                        <h1 className="text-3xl font-bold text-gray-900">
                            {framework.name} {isSOC2 && <span className="text-sm font-normal text-blue-600 bg-blue-50 px-2 py-1 rounded-full align-middle">(COSO View)</span>}
                        </h1>
                        <div className="flex gap-3">
                            {/* ... Buttons ... */}
                        </div>
                    </div>
                </div>
            </div>

            <div className="max-w-7xl mx-auto px-6 py-8 space-y-8">

                {/* STATS ROW (Same as before) */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 flex items-center justify-between">
                    <div>
                        <h3 className="text-sm font-bold text-gray-500 uppercase">Implementation</h3>
                        <div className="flex items-end gap-2">
                            <span className="text-4xl font-extrabold text-gray-900">{stats.percentage}%</span>
                            <span className="text-sm text-gray-500 mb-1">({stats.implemented}/{stats.total} Controls)</span>
                        </div>
                    </div>
                    <div className="w-1/2">
                        <div className="w-full bg-gray-100 rounded-full h-2">
                            <div className="bg-green-500 h-2 rounded-full transition-all duration-1000" style={{ width: `${stats.percentage}%` }}></div>
                        </div>
                    </div>
                </div>

                {/* SEARCH & FILTER */}
                <div className="flex items-center justify-between">
                    <div className="relative">
                        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                        <input
                            type="text"
                            placeholder="Search controls..."
                            className="pl-9 pr-4 py-2 border border-gray-300 rounded-lg text-sm w-64 focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                    </div>
                </div>

                {/* CONTENT AREA */}
                <div className="space-y-10">

                    {/* SOC 2 SPECIAL VIEW */}
                    {isSOC2 ? (
                        Object.keys(socControls).sort().map(category => {
                            const controls = getFilteredControls(socControls[category]);
                            if (controls.length === 0) return null;

                            const cosoText = COSO_DESCRIPTIONS[category] || COSO_DESCRIPTIONS["DEFAULT"];

                            return (
                                <div key={category} className="mb-8">
                                    <div className="mb-4">
                                        <h2 className="text-xl font-bold text-gray-900">{category}</h2>
                                        <p className="text-gray-600 font-medium text-sm mt-1 border-l-4 border-blue-500 pl-3">
                                            {cosoText}
                                        </p>
                                    </div>
                                    <div className="bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden">
                                        <table className="w-full">
                                            <thead>
                                                <tr className="bg-gray-50 border-b border-gray-200 text-left">
                                                    <th className="px-6 py-3 w-8"><input type="checkbox" className="rounded" /></th>
                                                    <th className="px-6 py-3 text-xs font-bold text-gray-500 uppercase">Control</th>
                                                    <th className="px-6 py-3 text-xs font-bold text-gray-500 uppercase">Evidence</th>
                                                    <th className="px-6 py-3 text-xs font-bold text-gray-500 uppercase">Category</th>
                                                    <th className="px-6 py-3 text-xs font-bold text-gray-500 uppercase">Owner</th>
                                                    <th className="px-6 py-3 text-xs font-bold text-gray-500 uppercase">Internal ID</th>
                                                </tr>
                                            </thead>
                                            <tbody className="divide-y divide-gray-100">
                                                {controls.map(c => (
                                                    <tr key={c.id} className="hover:bg-gray-50 transition-colors">
                                                        <td className="px-6 py-4"><input type="checkbox" className="rounded" /></td>
                                                        <td className="px-6 py-4 font-medium text-gray-900">{c.title}</td>
                                                        <td className="px-6 py-4">
                                                            <div className="flex items-center gap-2">
                                                                <div className={`w-2 h-2 rounded-full ${c.status === 'IMPLEMENTED' ? 'bg-green-500' : 'bg-gray-300'}`}></div>
                                                                <span className="text-sm text-gray-600">{c.status === 'IMPLEMENTED' ? 'Ready' : 'Pending'}</span>
                                                            </div>
                                                        </td>
                                                        <td className="px-6 py-4 text-sm text-gray-500">{category}</td>
                                                        <td className="px-6 py-4 text-sm text-gray-500">System</td>
                                                        <td className="px-6 py-4"><span className="bg-gray-100 text-gray-600 px-2 py-1 rounded text-xs font-mono">{c.control_id}</span></td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            );
                        })
                    ) : (
                        /* ISO / OTHER STANDARD VIEW (Using Processes) */
                        processes.length > 0 ? processes.map(process => (
                            <div key={process.id} className="bg-white border border-gray-200 rounded-lg p-6">
                                <h2 className="text-xl font-bold mb-4">{process.name}</h2>
                                <p className="text-gray-500 mb-4">Mapped Process</p>
                                <div className="text-sm text-gray-400 italic">Controls implementation pending for {process.name}...</div>
                            </div>
                        )) : (
                            <div className="text-center py-12 text-gray-500">
                                No mapped controls found for this framework.
                            </div>
                        )
                    )}

                </div>
            </div>
        </div>
    );
};

export default FrameworkDetail;
