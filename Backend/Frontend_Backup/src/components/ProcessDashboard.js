import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';
import { AlertTriangle, CheckCircle, Brain, ArrowRight } from 'lucide-react';
import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1';

const ProcessDashboard = () => {
    // Hardcoded list of domains for now (matching seed script)
    const domains = [
        "Information Security Policies",
        "Asset Management",
        "Access Management", // Might be empty if seed didn't catch it
        "Organization of Information Security"
    ];

    const [processData, setProcessData] = useState([]);
    const [selectedDomain, setSelectedDomain] = useState(null);
    const [analytics, setAnalytics] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchAllDomains();
    }, []);

    const fetchAllDomains = async () => {
        setLoading(true);
        const results = [];
        for (const domain of domains) {
            try {
                const res = await axios.get(`${API_URL}/analytics/domain/${encodeURIComponent(domain)}`);
                if (res.data.total_controls > 0) {
                    results.push(res.data);
                }
            } catch (error) {
                console.error(`Failed to fetch ${domain}`, error);
            }
        }
        setProcessData(results);
        if (results.length > 0) setSelectedDomain(results[0].domain);
        setLoading(false);
    };

    useEffect(() => {
        if (selectedDomain) {
            const data = processData.find(d => d.domain === selectedDomain);
            setAnalytics(data);
        }
    }, [selectedDomain, processData]);

    if (loading) return <div className="p-8">Loading Analytics...</div>;

    return (
        <div className="flex bg-gray-50 h-full">
            {/* Sidebar List */}
            <div className="w-1/3 border-r bg-white p-6 overflow-y-auto">
                <h2 className="text-xl font-bold mb-6">Process Domains</h2>
                <div className="space-y-4">
                    {processData.map((proc) => (
                        <div
                            key={proc.domain}
                            onClick={() => setSelectedDomain(proc.domain)}
                            className={`p-4 rounded-lg cursor-pointer border transition-all ${selectedDomain === proc.domain ? 'border-blue-500 bg-blue-50 shadow-md' : 'border-gray-200 hover:bg-gray-50'
                                }`}
                        >
                            <div className="flex justify-between items-center mb-2">
                                <span className="font-semibold text-gray-700">{proc.domain}</span>
                                <span className={`px-2 py-1 rounded text-xs font-bold ${proc.compliance_score >= 80 ? 'bg-green-100 text-green-800' :
                                    proc.compliance_score >= 50 ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'
                                    }`}>
                                    {proc.compliance_score}%
                                </span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2">
                                <div
                                    className={`h-2 rounded-full ${proc.compliance_score >= 80 ? 'bg-green-500' :
                                        proc.compliance_score >= 50 ? 'bg-yellow-500' : 'bg-red-500'
                                        }`}
                                    style={{ width: `${proc.compliance_score}%` }}
                                ></div>
                            </div>
                            <div className="text-xs text-gray-500 mt-2">
                                {proc.implemented} / {proc.total_controls} Controls Implemented
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Main Content */}
            <div className="w-2/3 p-8 overflow-y-auto">
                {analytics && (
                    <div>
                        <h1 className="text-2xl font-bold mb-2">{analytics.domain}</h1>
                        <p className="text-gray-600 mb-8">Process-level compliance breakdown and gap analysis.</p>

                        {/* Chart Section */}
                        <div className="bg-white p-6 rounded-lg shadow-sm mb-8 border border-gray-100">
                            <h3 className="font-semibold mb-4">Compliance Overview</h3>
                            <div className="h-64">
                                <ResponsiveContainer width="100%" height="100%">
                                    <BarChart data={[analytics]} layout="vertical">
                                        <CartesianGrid strokeDasharray="3 3" />
                                        <XAxis type="number" domain={[0, 100]} />
                                        <YAxis dataKey="domain" type="category" width={150} hide />
                                        <Tooltip />
                                        <Legend />
                                        <Bar dataKey="compliance_score" name="Compliance %" fill="#3B82F6" radius={[0, 4, 4, 0]}>
                                            <Cell fill={analytics.compliance_score >= 80 ? '#10B981' : analytics.compliance_score > 50 ? '#F59E0B' : '#EF4444'} />
                                        </Bar>
                                    </BarChart>
                                </ResponsiveContainer>
                            </div>
                        </div>

                        {/* Gap Analysis */}
                        <div className="mb-8">
                            <h3 className="text-lg font-bold mb-4 flex items-center">
                                <AlertTriangle className="w-5 h-5 text-orange-500 mr-2" />
                                Gap Analysis (The Missing {100 - analytics.compliance_score}%)
                            </h3>

                            {analytics.gaps.length === 0 ? (
                                <div className="p-4 bg-green-50 text-green-700 rounded-lg flex items-center">
                                    <CheckCircle className="w-5 h-5 mr-2" />
                                    No gaps detected! This process is fully compliant.
                                </div>
                            ) : (
                                <div className="bg-white border rounded-lg shadow-sm">
                                    <div className="px-6 py-4 border-b bg-gray-50 flex justify-between">
                                        <span className="font-semibold text-gray-600">Missing Controls</span>
                                        <span className="text-sm text-gray-500">{analytics.gaps.length} Gaps Found</span>
                                    </div>
                                    <div className="divide-y">
                                        {analytics.gaps.map(gap => (
                                            <div key={gap.id} className="p-6">
                                                <div className="flex justify-between items-start mb-2">
                                                    <div>
                                                        <span className="text-xs font-mono bg-gray-100 px-2 py-1 rounded text-gray-600 mr-2">{gap.id}</span>
                                                        <span className="font-medium text-gray-900">{gap.title}</span>
                                                    </div>
                                                    <span className="text-xs uppercase font-bold tracking-wider text-red-600 bg-red-50 px-2 py-1 rounded">
                                                        {gap.status.replace('_', ' ')}
                                                    </span>
                                                </div>

                                                {/* AI Insight Stub */}
                                                <div className="mt-4 bg-blue-50 p-4 rounded-md border border-blue-100">
                                                    <div className="flex items-center text-blue-800 mb-2">
                                                        <Brain className="w-4 h-4 mr-2" />
                                                        <span className="text-xs font-bold uppercase">AI Remediation Plan</span>
                                                    </div>
                                                    <p className="text-sm text-blue-900 leading-relaxed">
                                                        This control is currently <strong>{gap.status}</strong>.
                                                        To close this gap, assign an owner and upload evidence of implementation.
                                                        Recommended action: Define and document the procedure for {gap.title.toLowerCase()}.
                                                        <br />
                                                        <a href="#" className="font-medium hover:underline mt-2 inline-block">View Implementation Guide &rarr;</a>
                                                    </p>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ProcessDashboard;
