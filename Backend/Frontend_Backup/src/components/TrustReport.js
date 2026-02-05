import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Shield, CheckCircle, AlertTriangle, Lock } from 'lucide-react';

const API_URL = 'http://localhost:8000/api/v1';

const TrustReport = () => {
    const [frameworks, setFrameworks] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const token = localStorage.getItem('access_token');
                const res = await axios.get(`${API_URL}/frameworks/`, { headers: { Authorization: `Bearer ${token}` } });
                // Enriched stats would be better, calling /frameworks/ID/stats for each
                // For MVP, we list them
                setFrameworks(res.data);
                setLoading(false);
            } catch (err) {
                console.error(err);
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    if (loading) return <div className="p-8">Loading Trust Report...</div>;

    return (
        <div className="p-8 bg-gray-50 min-h-screen">
            <div className="max-w-7xl mx-auto space-y-8">
                {/* Header */}
                <div className="bg-white p-8 rounded-2xl shadow-sm border border-gray-200 flex justify-between items-center">
                    <div>
                        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
                            <Lock className="w-8 h-8 text-blue-600" />
                            Live Trust Report
                        </h1>
                        <p className="text-gray-500 mt-2">Real-time security and compliance posture verification.</p>
                    </div>
                    <div className="flex gap-4">
                        <div className="text-right">
                            <div className="text-sm font-bold text-gray-400 uppercase">System Status</div>
                            <div className="text-green-600 font-bold flex items-center gap-1 justify-end">
                                <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                                OPERATIONAL
                            </div>
                        </div>
                    </div>
                </div>

                {/* Framework Cards */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {frameworks.map(fw => (
                        <div key={fw.id} className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 transition hover:shadow-md">
                            <div className="flex justify-between items-start mb-4">
                                <div className="p-2 bg-blue-50 rounded-lg">
                                    <Shield className="w-6 h-6 text-blue-600" />
                                </div>
                                <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs font-bold rounded uppercase">
                                    {fw.code}
                                </span>
                            </div>
                            <h3 className="text-xl font-bold text-gray-900 mb-2">{fw.name}</h3>
                            <p className="text-gray-500 text-sm mb-6 line-clamp-2">{fw.description || "Compliance framework standard."}</p>

                            <div className="flex items-center gap-2 text-sm text-gray-600 mb-4">
                                <AlertTriangle className="w-4 h-4 text-orange-500" />
                                <span>Audit Readiness: <strong>Assessment Required</strong></span>
                            </div>

                            <button className="w-full py-2 bg-gray-50 hover:bg-gray-100 border border-gray-200 rounded-lg text-sm font-medium text-gray-700 transition">
                                View Full Report
                            </button>
                        </div>
                    ))}

                    {/* Add AI Compliance Card manually since it's separate system */}
                    <div className="bg-gradient-to-br from-indigo-600 to-purple-600 p-6 rounded-xl shadow-md text-white">
                        <div className="flex justify-between items-start mb-4">
                            <div className="p-2 bg-white/20 rounded-lg backdrop-blur-sm">
                                <Shield className="w-6 h-6 text-white" />
                            </div>
                            <span className="px-2 py-1 bg-white/20 text-white text-xs font-bold rounded uppercase">
                                BETA
                            </span>
                        </div>
                        <h3 className="text-xl font-bold text-white mb-2">AI Compliance (ISO 42001)</h3>
                        <p className="text-indigo-100 text-sm mb-6">Real-time AI mapping engine status.</p>

                        <a href="/ai-compliance" className="block w-full text-center py-2 bg-white text-indigo-600 rounded-lg text-sm font-bold hover:bg-indigo-50 transition">
                            Open AI Dashboard
                        </a>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default TrustReport;
