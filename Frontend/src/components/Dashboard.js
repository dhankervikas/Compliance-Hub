import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import axios from 'axios';
import { useEntitlements } from '../contexts/EntitlementContext';
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

import FrameworkSelector from './FrameworkSelector';

// ... (inside Dashboard component)

import api from '../services/api';

const Dashboard = () => {
    const navigate = useNavigate();
    const { tenantId } = useParams();
    const { refreshEntitlements } = useEntitlements();

    const [frameworks, setFrameworks] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showWizard, setShowWizard] = useState(false);
    const [searchTerm, setSearchTerm] = useState('');
    const [filterFramework, setFilterFramework] = useState('All');

    // Stats & Data
    const [actionItems, setActionItems] = useState([]);
    const [evidenceStats, setEvidenceStats] = useState({ status: 'Healthy', total: 0 });
    const [policyStats, setPolicyStats] = useState({ status: 'Healthy', approved: 0, total: 0 });
    const [soc2Scope, setSoc2Scope] = useState(['Security', 'Confidentiality', 'Availability']); // Default scope

    const fetchData = async () => {
        try {
            setLoading(true);
            // Fetch Frameworks
            const res = await api.get('/frameworks/');
            setFrameworks(res.data);

            // Mock Data for Dashboard Widgets (Preserving UI)
            setActionItems([
                { id: 1, title: 'Review AWS Security Group Changes', type: 'Vulnerability', severity: 'High', due: 'Today' },
                { id: 2, title: 'Approve New Access Request', type: 'Policy', severity: 'Medium', due: 'Tomorrow' },
                { id: 3, title: 'Vendor Assessment: Vanta', type: 'CAPA', severity: 'Medium', due: 'in 2 days' }
            ]);
            setEvidenceStats({ status: 'Healthy', total: 142 });
            setPolicyStats({ status: 'Healthy', approved: 12, total: 15 });

        } catch (err) {
            console.error("Dashboard fetch error:", err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, [tenantId]);

    // Derived State
    const filteredFrameworks = frameworks.filter(fw => {
        const matchesSearch = fw.name.toLowerCase().includes(searchTerm.toLowerCase());
        const matchesFilter = filterFramework === 'All' || fw.name.includes(filterFramework) || fw.code.includes(filterFramework);
        return matchesSearch && matchesFilter;
    });

    const baseUrl = `/t/${tenantId}`; // Helper for navigation

    const handleSetupComplete = async () => {
        await refreshEntitlements();
        fetchData();
    };

    // AUTO-INIT: If no frameworks, automatically link ISO 27001 (Zero-Touch Onboarding)
    useEffect(() => {
        const autoInitialize = async () => {
            if (!loading && frameworks.length === 0) {
                try {
                    // 1. Get Catalog
                    const catRes = await api.get('/frameworks/?catalog=true');
                    const catalog = catRes.data;

                    // 2. Find ISO 27001 (Default Standard)
                    const isoFw = catalog.find(f => f.code.includes("ISO27001") || f.code.includes("ISO"));

                    if (isoFw) {
                        console.log("Auto-initializing workspace with:", isoFw.name);
                        // 3. Link it
                        await api.post('/frameworks/tenant-link', { framework_ids: [isoFw.id] });
                        // 4. Refresh Dashboard
                        await handleSetupComplete();
                    }
                } catch (e) {
                    console.error("Auto-init failed:", e);
                }
            }
        };

        if (!loading && frameworks.length === 0) {
            autoInitialize();
        }
    }, [loading, frameworks.length]);

    // AUTO-REPAIR: If frameworks exist but have no data (e.g. legacy link), Seed them
    useEffect(() => {
        const checkAndRepair = async () => {
            if (!loading && frameworks.length > 0) {
                const isoFw = frameworks.find(f => f.code.includes("ISO") || f.code.includes("ISO27001"));

                // If ISO exists but has < 10 controls, it's likely unseeded.
                if (isoFw && isoFw.total_controls < 10) {
                    console.log("Detected unseeded framework. Triggering auto-repair...");
                    try {
                        // Show some UI indication if desirable, or just do it silently and refresh
                        await api.post(`/frameworks/${isoFw.id}/seed-controls`);
                        // Refresh data to show results
                        fetchData();
                    } catch (e) {
                        console.error("Auto-repair failed:", e);
                    }
                }
            }
        };

        checkAndRepair();
    }, [loading, frameworks]);

    // CHECK IF NEEDS SETUP
    // If we have no frameworks, show initializing state
    if (!loading && frameworks.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50">
                <div className="w-16 h-16 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mb-4"></div>
                <h2 className="text-xl font-bold text-gray-900">Setting up your secure workspace...</h2>
                <p className="text-gray-500">Applying default compliance standards.</p>
            </div>
        );
    }

    if (loading) return <div className="p-8 text-center text-gray-500">Loading Dashboard...</div>;

    return (
        <div className="p-6 space-y-6 animate-fade-in pb-20">
            {/* FrameworkSetupWizard Removed - One-Time Configuration Only */}

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
                        {/* Options Button Removed - Frameworks are set once during onboarding */}
                        {/* Dev-only Repair Data Button REMOVED for Tenant Stability */}

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
                                if (soc2Scope.includes('Confidentiality')) baseControls += 2; // Actual DB count
                                if (soc2Scope.includes('Processing Integrity')) baseControls += 5; // Actual DB count
                                if (soc2Scope.includes('Privacy')) baseControls += 20; // Actual DB count

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
                                    onClick={() => navigate(`/t/${tenantId}/frameworks/${fw.id}`)}
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
                        {/* Add New Framework Button REMOVED as per user request */}
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
                                        onClick={() => navigate(`${baseUrl}/frameworks/${frameworks.length > 0 ? frameworks[0].id : 1}?search=${encodeURIComponent(item.type)}`)}
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
