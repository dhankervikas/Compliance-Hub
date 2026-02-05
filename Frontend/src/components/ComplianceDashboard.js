import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { CheckCircle, XCircle, AlertCircle, ChevronDown, ChevronUp, Lock, Filter, Shield } from 'lucide-react';

const ComplianceDashboard = () => {
    const { user } = useAuth();
    const [summary, setSummary] = useState([]);
    const [loading, setLoading] = useState(true);
    const [stats, setStats] = useState({ total: 0, pass: 0, fail: 0 });

    // Framework Filtering
    const [frameworks, setFrameworks] = useState([]);
    const [selectedFramework, setSelectedFramework] = useState(null); // null = All

    // Domain Expansion State
    const [expandedDomain, setExpandedDomain] = useState(null);
    const [domainDetails, setDomainDetails] = useState({}); // Cache details by domain
    const [loadingDetails, setLoadingDetails] = useState(false);

    useEffect(() => {
        if (user) {
            fetchFrameworks();
        }
    }, [user]);

    useEffect(() => {
        if (user) {
            fetchSummary();
        }
    }, [user, selectedFramework]);

    const fetchFrameworks = async () => {
        try {
            const res = await api.get('/frameworks');
            setFrameworks(res.data);
        } catch (err) {
            console.error("Failed to load frameworks");
        }
    };

    const fetchSummary = async () => {
        setLoading(true);
        try {
            let url = '/compliance/summary';
            if (selectedFramework) {
                url += `?framework_id=${selectedFramework}`;
            }

            const response = await api.get(url);

            const data = response.data.summary;
            setSummary(data);

            // Calculate Global Stats
            let total = 0;
            let pass = 0;
            let fail = 0;

            data.forEach(d => {
                total += d.stats.total;
                pass += d.stats.pass;
                fail += d.stats.fail;
            });

            setStats({ total, pass, fail });
            setLoading(false);
        } catch (error) {
            console.error("Error fetching compliance summary:", error);
            setLoading(false);
        }
    };

    const toggleDomain = async (domain) => {
        if (expandedDomain === domain) {
            setExpandedDomain(null);
            return;
        }

        setExpandedDomain(domain);

        // Fetch details if not cached
        if (!domainDetails[domain]) {
            setLoadingDetails(true);
            try {
                const response = await api.get(`/compliance/domain/${encodeURIComponent(domain)}/details`);
                setDomainDetails(prev => ({ ...prev, [domain]: response.data.controls }));
            } catch (error) {
                console.error("Error fetching details:", error);
            } finally {
                setLoadingDetails(false);
            }
        }
    };

    if (loading) return <div className="p-8 text-center text-gray-500">Loading Compliance Dashboard...</div>;

    return (
        <div className="p-8 max-w-7xl mx-auto">
            <header className="mb-8">
                <h1 className="text-3xl font-bold text-gray-900 mb-2">Compliance Overview</h1>
                <div className="flex items-center gap-3">
                    <div className="relative">
                        <Filter size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                        <select
                            className="pl-9 pr-4 py-2 bg-white border border-gray-200 rounded-lg text-sm font-medium text-gray-700 outline-none focus:ring-2 focus:ring-blue-500 appearance-none cursor-pointer hover:border-blue-400 transition-colors"
                            value={selectedFramework || ""}
                            onChange={(e) => setSelectedFramework(e.target.value || null)}
                        >
                            <option value="">All Frameworks (Trust Score)</option>
                            {frameworks.map(fw => (
                                <option key={fw.id} value={fw.id}>{fw.name}</option>
                            ))}
                        </select>
                    </div>
                    <span className="text-gray-300">|</span>
                    <span className="text-sm text-gray-500">Tenant: <strong className="text-gray-700">{user?.tenant_id || 'Unknown'}</strong></span>
                </div>
            </header>

            {/* Summary Cards */}
            <div className={`grid grid-cols-1 md:grid-cols-2 ${!selectedFramework ? 'lg:grid-cols-4' : 'lg:grid-cols-3'} gap-6 mb-10`}>
                {!selectedFramework && (
                    <div className="bg-gradient-to-br from-blue-600 to-indigo-700 p-6 rounded-xl shadow-lg border border-blue-500 text-white animate-fade-in-up">
                        <div className="text-blue-100 text-xs font-bold uppercase tracking-wider mb-2">Platform Trust Score</div>
                        <div className="text-5xl font-extrabold flex items-center gap-3">
                            {stats.total > 0 ? Math.round((stats.pass / stats.total) * 100) : 0}%
                            <Shield size={32} className="text-blue-300/50" />
                        </div>
                    </div>
                )}

                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                    <div className="text-gray-500 text-sm font-medium uppercase tracking-wide mb-1">Total Controls</div>
                    <div className="text-4xl font-bold text-gray-900">{stats.total}</div>
                </div>
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                    <div className="text-gray-500 text-sm font-medium uppercase tracking-wide mb-1">Passing</div>
                    <div className="text-4xl font-bold text-green-600 flex items-center gap-2">
                        {stats.pass}
                        <CheckCircle size={24} className="text-green-500" />
                    </div>
                </div>
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                    <div className="text-gray-500 text-sm font-medium uppercase tracking-wide mb-1">Failing</div>
                    <div className="text-4xl font-bold text-red-600 flex items-center gap-2">
                        {stats.fail}
                        <XCircle size={24} className="text-red-500" />
                    </div>
                </div>
            </div>

            {/* Domain List */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                <div className="px-6 py-4 border-b border-gray-100 bg-gray-50">
                    <h2 className="font-semibold text-gray-800">Domain Breakdown</h2>
                </div>

                <div className="divide-y divide-gray-100">
                    {summary.map((item) => (
                        <div key={item.domain} className="group">
                            {/* Row Header */}
                            <div
                                onClick={() => toggleDomain(item.domain)}
                                className="px-6 py-5 cursor-pointer hover:bg-gray-50 transition-colors flex flex-col md:flex-row md:items-center gap-4"
                            >
                                <div className="flex-1">
                                    <div className="flex justify-between items-center mb-2">
                                        <h3 className="font-medium text-gray-900">{item.domain}</h3>
                                        <span className={`text-sm font-bold ${item.percentage === 100 ? 'text-green-600' : item.percentage > 0 ? 'text-orange-500' : 'text-gray-400'}`}>
                                            {item.percentage}% Passing
                                        </span>
                                    </div>

                                    {/* Progress Bar */}
                                    <div className="h-2 w-full bg-gray-100 rounded-full overflow-hidden">
                                        <div
                                            className={`h-full rounded-full transition-all duration-500 ${item.percentage === 100 ? 'bg-green-500' :
                                                item.percentage > 50 ? 'bg-orange-400' : 'bg-red-500'
                                                }`}
                                            style={{ width: `${item.percentage}%` }}
                                        />
                                    </div>
                                </div>
                                <div className="ml-4 text-gray-400">
                                    {expandedDomain === item.domain ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
                                </div>
                            </div>

                            {/* Details Expansion */}
                            {expandedDomain === item.domain && (
                                <div className="px-6 pb-6 bg-gray-50/50 border-t border-gray-100 animate-fade-in-down">
                                    <div className="pt-4 space-y-4">
                                        {loadingDetails && !domainDetails[item.domain] ? (
                                            <div className="text-center py-4 text-gray-500 text-sm">Loading Controls...</div>
                                        ) : (
                                            domainDetails[item.domain]?.map(control => (
                                                <div key={control.control_id} className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm">
                                                    <div className="flex justify-between items-start mb-2">
                                                        <div>
                                                            <div className="flex items-center gap-2">
                                                                <span className="font-mono text-sm font-bold text-gray-600 bg-gray-100 px-1.5 py-0.5 rounded">
                                                                    {control.control_id}
                                                                </span>
                                                                <h4 className="font-semibold text-gray-800">{control.title}</h4>
                                                            </div>
                                                            <p className="text-sm text-gray-500 mt-1">{control.description || "No description available."}</p>
                                                        </div>
                                                        <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${control.status === 'PASS' ? 'bg-green-100 text-green-800' :
                                                            control.status === 'FAIL' ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-800'
                                                            }`}>
                                                            {control.status}
                                                        </span>
                                                    </div>

                                                    {/* Evidence Section */}
                                                    <div className="mt-3 bg-slate-50 border border-slate-100 rounded p-3">
                                                        <div className="flex items-center gap-2 text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">
                                                            <Lock size={12} /> Decrypted Evidence
                                                            <span className="ml-auto font-normal normal-case text-slate-400">
                                                                Scanned: {new Date(control.last_scanned).toLocaleString()}
                                                            </span>
                                                        </div>
                                                        {control.evidence && Object.keys(control.evidence).length > 0 ? (
                                                            <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs">
                                                                {Object.entries(control.evidence).map(([key, value]) => (
                                                                    <div key={key} className="flex justify-between border-b border-slate-200 pb-1 last:border-0 last:pb-0">
                                                                        <span className="text-slate-500 font-medium">{key}:</span>
                                                                        <span className="text-slate-700 font-mono text-right truncate ml-4" title={String(value)}>
                                                                            {String(value)}
                                                                        </span>
                                                                    </div>
                                                                ))}
                                                            </div>
                                                        ) : (
                                                            <div className="text-sm text-gray-400 italic">No evidence data found.</div>
                                                        )}
                                                    </div>
                                                </div>
                                            ))
                                        )}
                                        {domainDetails[item.domain]?.length === 0 && (
                                            <div className="text-center text-sm text-gray-500">No controls mapped to this domain.</div>
                                        )}
                                    </div>
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default ComplianceDashboard;
