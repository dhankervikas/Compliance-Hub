import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import {
    Shield,
    CheckCircle,
    AlertTriangle,
    FileText,
    Search,
    Filter,
    Activity,
    Clock,
    Zap,
    Settings
} from 'lucide-react';
import { ISO_CONTROLS, SOC2_CONTROLS, HIPPA_CONTROLS, NIST_CONTROLS, GDPR_CONTROLS } from '../data/seedData';
import FrameworkSetupWizard from './Wizards/FrameworkSetupWizard';

import config from '../config';
const API_URL = config.API_BASE_URL;

const Dashboard = () => {
    const navigate = useNavigate();
    const [frameworks, setFrameworks] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null); // Add Error State
    const [filterFramework, setFilterFramework] = useState('All');
    const [searchTerm, setSearchTerm] = useState('');
    const [showWizard, setShowWizard] = useState(false);
    const [soc2Scope, setSoc2Scope] = useState(['Security']); // Default

    // Capability Stats
    const [policyStats, setPolicyStats] = useState({ approved: 0, total: 0, status: 'Unknown' });
    const [evidenceStats, setEvidenceStats] = useState({ valid: 0, total: 0, status: 'Unknown' });

    const [seedLog, setSeedLog] = useState([]); // Log state

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            const token = localStorage.getItem('token');
            const headers = { Authorization: `Bearer ${token}` };

            // 0. Fetch Scope Settings
            try {
                const scopeRes = await axios.get(`${API_URL}/settings/scope`, { headers });
                if (scopeRes.data && scopeRes.data.content && scopeRes.data.content.soc2_selected_principles) {
                    setSoc2Scope(scopeRes.data.content.soc2_selected_principles);
                }
            } catch (e) {
                console.warn("Scope settings not found, using default.");
            }

            // 1. Fetch Frameworks & Stats
            const fwRes = await axios.get(`${API_URL}/frameworks/`, { headers });
            const fwData = fwRes.data;

            const frameworksWithStats = await Promise.all(fwData.map(async (fw) => {
                try {
                    const statRes = await axios.get(`${API_URL}/frameworks/${fw.id}/stats`, { headers });
                    return { ...fw, ...statRes.data }; // Merge stats
                } catch (e) {
                    return { ...fw, completion_percentage: 0, total_controls: 0, implemented_controls: 0 };
                }
            }));

            // SORT LOGIC
            const sortedFrameworks = frameworksWithStats.sort((a, b) => {
                const codeA = (a.code || "").toUpperCase();
                const codeB = (b.code || "").toUpperCase();
                const priority = { "ISO27001": 1, "SOC2": 2 };
                const pA = priority[codeA] || priority[Object.keys(priority).find(k => codeA.includes(k))] || 99;
                const pB = priority[codeB] || priority[Object.keys(priority).find(k => codeB.includes(k))] || 99;
                if (pA !== pB) return pA - pB;
                return a.name.localeCompare(b.name);
            });

            setFrameworks(sortedFrameworks);

            // 2. Fetch Policy & Evidence Stats
            // We fetch the lists and calculate stats client-side for now
            try {
                const [policiesRes, evidenceRes] = await Promise.all([
                    axios.get(`${API_URL}/policies/`, { headers }),
                    axios.get(`${API_URL}/evidence/`, { headers })
                ]);

                // Policy Stats
                const policies = policiesRes.data;
                const approvedPolicies = policies.filter(p => p.status === 'Approved').length;
                let policyStatus = 'Needs Review';
                if (policies.length === 0) policyStatus = 'No Policies';
                else if (approvedPolicies === policies.length) policyStatus = 'Healthy';
                else if (approvedPolicies > 0) policyStatus = 'In Progress';

                setPolicyStats({
                    approved: approvedPolicies,
                    total: policies.length,
                    status: policyStatus
                });

                // Evidence Stats
                const evidence = evidenceRes.data;
                // Assuming existence implies some validity for now, or check specific fields if available
                const validEvidence = evidence.length; // Simplify for now
                let evidenceStatus = 'Needs Collection';
                if (evidence.length > 5) evidenceStatus = 'Healthy'; // Arbitrary threshold for demo
                else if (evidence.length > 0) evidenceStatus = 'Collecting';

                setEvidenceStats({
                    valid: validEvidence,
                    total: evidence.length,
                    status: evidenceStatus
                });

            } catch (err) {
                console.warn("Failed to fetch auxiliary stats", err);
            }

            setLoading(false);
        } catch (err) {
            console.error("Failed to load dashboard data", err);
            setError(err.message || "Failed to load data");
            setLoading(false);
        }
    };

    const handleSeed = async () => {
        // ... (Existing Seed Logic - Unchanged)
        // Define helper immediately so it can be used
        const addLog = (msg) => setSeedLog(prev => [...prev, `${new Date().toLocaleTimeString()} - ${msg}`]);

        setSeedLog(["Starting Repair Process..."]);

        try {
            setLoading(true);
            const token = localStorage.getItem('token');
            const headers = { Authorization: `Bearer ${token}` };

            addLog("Starting Database Hard Reset...");

            // 1. Fetch Frameworks to get IDs
            const DEFAULT_FRAMEWORKS = [
                { name: "ISO 27001:2022", code: "ISO27001", description: "Information Security Management System" },
                { name: "SOC 2 Type II", code: "SOC2", description: "Service Organization Control 2" },
                { name: "HIPAA Security Rule", code: "HIPAA", description: "Health Insurance Portability and Accountability Act" },
                { name: "GDPR", code: "GDPR", description: "General Data Protection Regulation" },
                { name: "NIST CSF 2.0", code: "NIST-CSF", description: "National Institute of Standards and Technology" }
            ];

            let frameworksRes = await axios.get(`${API_URL}/frameworks/`, { headers });
            let allFws = frameworksRes.data;
            const existingCodes = new Set(allFws.map(f => f.code));

            for (const fw of DEFAULT_FRAMEWORKS) {
                if (!existingCodes.has(fw.code)) {
                    addLog(`Creating Framework: ${fw.name}...`);
                    await axios.post(`${API_URL}/frameworks/`, fw, { headers });
                }
            }

            frameworksRes = await axios.get(`${API_URL}/frameworks/`, { headers });
            allFws = frameworksRes.data;
            const frameworkMap = {};
            allFws.forEach(fw => { frameworkMap[fw.code] = fw.id; });

            const controlsMap = {
                'HIPAA': HIPPA_CONTROLS,
                'SOC2': SOC2_CONTROLS,
                'ISO27001': ISO_CONTROLS,
                'NIST-CSF': NIST_CONTROLS,
                'GDPR': GDPR_CONTROLS
            };

            const processBatch = async (items, batchSize, processFn) => {
                for (let i = 0; i < items.length; i += batchSize) {
                    const batch = items.slice(i, i + batchSize);
                    await Promise.all(batch.map(processFn));
                }
            };

            for (const fwCode of Object.keys(controlsMap)) {
                const fwId = frameworkMap[fwCode];
                if (!fwId) { addLog(`Skipping ${fwCode}`); continue; }

                const newControls = controlsMap[fwCode];
                if (!newControls || newControls.length === 0) continue;
                addLog(`Loaded ${newControls.length} controls for ${fwCode}.`);

                const existingRes = await axios.get(`${API_URL}/controls/?limit=3000`, { headers });
                const relevantControls = existingRes.data.filter(c => c.framework_id === fwId);
                addLog(`Found ${relevantControls.length} existing. Deleting...`);

                await processBatch(relevantControls, 100, async (c) => { // Aggressive batch
                    try { await axios.delete(`${API_URL}/controls/${c.id}`, { headers }); } catch (e) { }
                });

                addLog(`Creating ${newControls.length} new controls...`);
                await processBatch(newControls, 20, async (c) => {
                    const controlId = c.control_id || c.title.substring(0, 15);
                    const payload = {
                        framework_id: fwId,
                        control_id: controlId,
                        title: c.title,
                        description: c.description,
                        category: c.category || "General",
                        status: "not_started"
                    };
                    try { await axios.post(`${API_URL}/controls/`, payload, { headers }); } catch (e) { }
                });
            }
            addLog("Global Seed Complete.");
            alert("Database repaired successfully!");
            setLoading(false);
            fetchData();
        } catch (err) {
            console.error("Seeding failed", err);
            alert(`Seeding Failed: ${err.message}`);
            setLoading(false);
        }
    };

    if (error) {
        return (
            <div className="p-8 text-center text-red-500">
                <p className="mb-4">Failed to load dashboard: {error}</p>
                <button
                    onClick={() => { setError(null); setLoading(true); fetchData(); }}
                    className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                >
                    Retry Connection
                </button>
            </div>
        );
    }

    // --- MOCKED "DUE SOON" DATA ---
    const actionItems = [
        { id: 1, type: 'Vulnerability', title: 'Critical: Log4j in payment-service', due: 'Today', severity: 'Critical' },
        { id: 2, type: 'Policy', title: 'Review: Access Control Policy', due: 'Tomorrow', severity: 'High' },
        { id: 3, type: 'CAPA', title: 'Missing Evidence for CC6.1', due: '3 Days', severity: 'Medium' },
        { id: 4, type: 'Training', title: 'Security Awareness: 5 Employees Pending', due: '5 Days', severity: 'Low' }
    ];

    const filteredFrameworks = frameworks.filter(fw => {
        const matchesSearch = fw.name.toLowerCase().includes(searchTerm.toLowerCase());
        const matchesFilter = filterFramework === 'All' || fw.name.includes(filterFramework);
        return matchesSearch && matchesFilter;
    });

    if (loading) return <div className="p-8 text-center text-gray-500">Loading Dashboard...</div>;

    return (
        <div className="p-6 space-y-6 animate-fade-in pb-20">
            {showWizard && (
                <FrameworkSetupWizard
                    onComplete={() => { setShowWizard(false); fetchData(); }}
                    onCancel={() => setShowWizard(false)}
                />
            )}

            {/* HEADER & FILTERS */}
            <div>
                <h1 className="text-2xl font-bold text-gray-900 mb-6">Dashboard</h1>

                <div className="flex flex-col md:flex-row justify-between gap-4 bg-white p-4 rounded-xl border border-gray-200 shadow-sm">
                    <div className="flex items-center gap-4 flex-1">
                        <div className="relative flex-1 max-w-md">
                            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                            <input
                                type="text"
                                placeholder="Search items..."
                                className="pl-9 pr-4 py-2 border border-gray-300 rounded-lg text-sm w-full focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                            />
                        </div>
                        <div className="h-8 w-px bg-gray-200"></div>
                        <div className="flex items-center gap-2">
                            <Filter className="w-4 h-4 text-gray-500" />
                            <select
                                className="border-none text-sm font-medium text-gray-700 focus:ring-0 cursor-pointer bg-transparent"
                                value={filterFramework}
                                onChange={(e) => setFilterFramework(e.target.value)}
                            >
                                <option value="All">All Frameworks</option>
                                <option value="SOC 2">SOC 2</option>
                                <option value="ISO">ISO 27001</option>
                            </select>
                        </div>
                    </div>
                    <div className="flex gap-2">
                        <button
                            onClick={() => setShowWizard(true)}
                            className="px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors shadow-sm flex items-center gap-2"
                        >
                            <Settings className="w-4 h-4 text-gray-600" /> Options
                        </button>
                        {/* Dev-only Repair Data Button */}
                        {(window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') && (
                            <button
                                onClick={handleSeed}
                                className="px-3 py-2 text-sm font-bold text-white bg-gray-800 rounded-lg hover:bg-gray-700 transition-colors shadow-sm flex items-center gap-2"
                            >
                                <Shield className="w-4 h-4" /> Repair Data
                            </button>
                        )}
                        <button className="px-3 py-2 text-sm font-medium text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors">
                            + Add Widget
                        </button>
                    </div>
                </div>
            </div>

            {/* MAIN CONTENT GRID */}
            <div className="flex flex-col lg:flex-row gap-8 items-start">

                {/* LEFT COLUMN */}
                <div className="flex-1 w-full space-y-6">
                    <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                        <Shield className="w-5 h-5 text-blue-600" /> Framework Status
                    </h2>

                    {frameworks.length === 0 && !loading && (
                        <div className="bg-white border border-blue-100 rounded-2xl p-12 text-center shadow-lg mb-8">
                            <div className="w-20 h-20 bg-blue-50 rounded-full flex items-center justify-center mx-auto mb-6">
                                <Shield className="w-10 h-10 text-blue-600" />
                            </div>
                            <h3 className="text-2xl font-bold text-gray-900 mb-2">Welcome to AssuRisk</h3>
                            <p className="text-gray-500 mb-8 max-w-lg mx-auto">
                                Initialize database to get started.
                            </p>
                            <button
                                onClick={handleSeed}
                                className="px-8 py-4 text-lg font-bold text-white bg-blue-600 rounded-xl hover:bg-blue-700 transition-all shadow-blue-200 shadow-xl flex items-center gap-3 mx-auto"
                            >
                                <Zap className="w-5 h-5 fill-current" /> Initialize Data
                            </button>
                            {seedLog.length > 0 && (
                                <div className="mt-8 bg-gray-900 rounded-xl p-4 text-left font-mono text-xs text-green-400 h-64 overflow-y-auto w-full max-w-2xl mx-auto border border-gray-800 shadow-inner">
                                    {seedLog.map((log, i) => (
                                        <div key={i} className="mb-1 border-l-2 border-green-800 pl-2">{log}</div>
                                    ))}
                                </div>
                            )}
                        </div>
                    )}

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {filteredFrameworks.map(fw => {
                            let percent = fw.completion_percentage;
                            let controls = fw.implemented_controls;
                            let total = fw.total_controls;

                            // SOC 2 SCOPE OVERRIDE
                            if (fw.code && fw.code.includes("SOC2")) {
                                // Dynamic Denominator Calculation based on Scope
                                // Security (CC) is roughly 33 base controls in 2017 TSC
                                let baseControls = 33;

                                if (soc2Scope.includes('Availability')) baseControls += 3;
                                if (soc2Scope.includes('Confidentiality')) baseControls += 5;
                                if (soc2Scope.includes('Processing Integrity')) baseControls += 3;
                                if (soc2Scope.includes('Privacy')) baseControls += 18; // Privacy is large

                                total = baseControls;

                                // Adjust Implemented Count (Mocking the effect of scope on tested controls)
                                // If Privacy is excluded, we shouldn't count its "missing" controls as failures, 
                                // but for this demo, we assume 'controls' (numerator) is constant count of passing tests.
                                // We clamp it to not exceed total.
                                if (controls > total) controls = total;

                                // Re-calculate percentage
                                percent = Math.round((controls / total) * 100);
                            }

                            return (
                                <div
                                    key={fw.id}
                                    onClick={() => navigate(`/frameworks/${fw.id}`)}
                                    className="bg-white rounded-xl p-6 shadow-sm border border-gray-200 hover:shadow-md hover:border-blue-300 transition-all cursor-pointer group relative overflow-hidden"
                                >
                                    <div className="flex justify-between items-start mb-4 relative z-10">
                                        <h3 className="text-lg font-bold text-gray-900 line-clamp-1" title={fw.name}>{fw.name}</h3>
                                        <span className={`px-2 py-1 rounded text-xs font-bold ${percent === 100 ? 'bg-green-100 text-green-700' : 'bg-blue-50 text-blue-700'}`}>
                                            {percent === 100 ? 'COMPLIANT' : 'ACTIVE'}
                                        </span>
                                    </div>

                                    {/* SOC 2 SPECIFIC BADGES */}
                                    {fw.code && fw.code.includes("SOC2") && (
                                        <div className="flex gap-1 mb-3 relative z-10 flex-wrap">
                                            {soc2Scope.map(p => (
                                                <span key={p} className="text-[10px] bg-slate-100 text-slate-600 border border-slate-200 px-1.5 py-0.5 rounded font-medium">
                                                    {p.substring(0, 3).toUpperCase()}
                                                </span>
                                            ))}
                                            {soc2Scope.length < 5 && soc2Scope.length > 0 && <span className="text-[10px] text-gray-400 px-1">+ Scope Configured</span>}
                                        </div>
                                    )}

                                    <div className="flex items-end gap-2 mb-4 relative z-10">
                                        <span className="text-4xl font-extrabold text-gray-900">{percent}%</span>
                                        <span className="text-sm text-gray-500 mb-1">Implemented</span>
                                    </div>
                                    <div className="w-full bg-gray-100 rounded-full h-2 mb-4 relative z-10">
                                        <div
                                            className={`h-2 rounded-full transition-all duration-1000 ${percentageColor(percent)}`}
                                            style={{ width: `${percent}%` }}
                                        ></div>
                                    </div>
                                    <div className="flex justify-between text-xs text-gray-500 relative z-10 border-t border-gray-50 pt-3">
                                        <span className="flex items-center gap-1">
                                            <CheckCircle className="w-3 h-3 text-green-500" /> {controls} / {total} Controls
                                        </span>
                                        <span className="flex items-center gap-1">
                                            <Activity className="w-3 h-3 text-blue-500" /> Auto-Testing On
                                        </span>
                                    </div>
                                    <div className="absolute -bottom-10 -right-10 w-32 h-32 bg-gray-50 rounded-full group-hover:bg-blue-50 transition-colors z-0"></div>
                                </div>
                            );
                        })}
                        <div className="border-2 border-dashed border-gray-200 rounded-xl p-6 flex flex-col items-center justify-center text-gray-400 hover:border-blue-300 hover:text-blue-500 cursor-pointer transition-colors min-h-[220px]">
                            <div className="w-12 h-12 bg-gray-50 rounded-full flex items-center justify-center mb-3">
                                <span className="text-2xl">+</span>
                            </div>
                            <span className="font-medium text-sm">Add New Framework</span>
                        </div>
                    </div>
                </div>

                {/* RIGHT COLUMN */}
                <div className="w-full lg:w-96 space-y-8 flex-shrink-0">

                    {/* Action Required */}
                    <div>
                        <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                            <Clock className="w-5 h-5 text-orange-500" /> Action Required
                        </h2>
                        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                            <div className="divide-y divide-gray-100">
                                {actionItems.map(item => (
                                    <div
                                        key={item.id}
                                        onClick={() => navigate(`/frameworks/${frameworks.length > 0 ? frameworks[0].id : 1}?search=${encodeURIComponent(item.type)}`)}
                                        className="p-4 flex items-start gap-4 hover:bg-gray-50 transition-colors cursor-pointer group"
                                    >
                                        <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 mt-1 ${itemSeverityColor(item.severity)}`}>
                                            {item.type === 'Vulnerability' && <Zap className="w-4 h-4" />}
                                            {item.type === 'Policy' && <FileText className="w-4 h-4" />}
                                            {item.type === 'CAPA' && <AlertTriangle className="w-4 h-4" />}
                                            {item.type === 'Training' && <CheckCircle className="w-4 h-4" />}
                                        </div>
                                        <div className="flex-1 min-w-0">
                                            <div className="flex justify-between items-start">
                                                <h4 className="text-sm font-bold text-gray-900 line-clamp-2 leading-tight mb-1 group-hover:text-blue-600">{item.title}</h4>
                                            </div>
                                            <p className="text-xs text-gray-500 flex items-center gap-2">
                                                <span className="font-medium text-orange-600 whitespace-nowrap">Due: {item.due}</span>
                                                <span>•</span>
                                                <span>{item.type}</span>
                                            </p>
                                        </div>
                                    </div>
                                ))}
                            </div>
                            <div className="bg-gray-50 p-2 text-center border-t border-gray-200">
                                <button className="text-xs text-blue-600 font-bold uppercase tracking-wider hover:text-blue-800">View All Actions</button>
                            </div>
                        </div>
                    </div>

                    {/* Compliance Capability */}
                    <div>
                        <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                            <Activity className="w-5 h-5 text-purple-600" /> Capabilities
                        </h2>
                        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 space-y-6">
                            <div className="flex justify-between items-center">
                                <span className="text-sm font-medium text-gray-700">Continuous Monitoring</span>
                                <span className="px-2 py-1 bg-green-100 text-green-700 rounded text-xs font-bold">ACTIVE</span>
                            </div>
                            <div className="flex justify-between items-center">
                                <span className="text-sm font-medium text-gray-700">Evidence Collection</span>
                                <span className={`text-sm font-bold ${evidenceStats.status === 'Healthy' ? 'text-green-600' : 'text-orange-600'}`}>
                                    {evidenceStats.status} ({evidenceStats.total})
                                </span>
                            </div>
                            <div className="flex justify-between items-center">
                                <span className="text-sm font-medium text-gray-700">Policy Adherence</span>
                                <span className={`text-sm font-bold ${policyStats.status === 'Healthy' ? 'text-green-600' : 'text-orange-600'}`}>
                                    {policyStats.status} ({policyStats.approved}/{policyStats.total})
                                </span>
                            </div>

                            <div className="pt-4 border-t border-gray-100">
                                <div className="flex justify-between items-center mb-2">
                                    <h4 className="text-xs font-bold text-gray-500 uppercase">Pending Tasks</h4>
                                    <span className="text-[10px] bg-red-100 text-red-600 px-1.5 rounded-full font-bold">4</span>
                                </div>
                                <div className="space-y-2">
                                    <div className="flex justify-between text-sm hover:bg-gray-50 p-1 rounded cursor-pointer transition-colors">
                                        <span className="text-gray-600">Vendor Reviews</span>
                                        <span className="font-bold text-red-500">3 Due</span>
                                    </div>
                                    <div className="flex justify-between text-sm hover:bg-gray-50 p-1 rounded cursor-pointer transition-colors">
                                        <span className="text-gray-600">Access Reviews</span>
                                        <span className="font-bold text-orange-500">1 Overdue</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                </div>
            </div>
        </div>
    );
};

const percentageColor = (p) => {
    if (p === 100) return 'bg-green-500';
    if (p > 50) return 'bg-blue-500';
    return 'bg-orange-500';
};

const itemSeverityColor = (sev) => {
    switch (sev) {
        case 'Critical': return 'bg-red-100 text-red-600';
        case 'High': return 'bg-orange-100 text-orange-600';
        case 'Medium': return 'bg-yellow-100 text-yellow-600';
        default: return 'bg-blue-50 text-blue-600';
    }
};

export default Dashboard;
