
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
    CheckCircle, TrendingUp, AlertTriangle,
    Activity, Clock, RefreshCw
} from 'lucide-react';

import LogDetailModal from './LogDetailModal';

import config from '../config';
const API_URL = config.API_BASE_URL;



const SystemEffectiveness = () => {
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const [lastScan, setLastScan] = useState(new Date().toLocaleTimeString());
    const [selectedLog, setSelectedLog] = useState(null);
    const [activeFilter, setActiveFilter] = useState('ALL'); // 'ALL', 'FAIL', 'PASS'

    const fetchStats = async () => {
        try {
            const token = localStorage.getItem('token');
            const res = await axios.get(`${API_URL}/analytics/system-stats`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setStats(res.data);
            setLoading(false);
        } catch (err) {
            console.error("Failed to fetch system stats", err);
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchStats();
    }, []);

    const handleRunScan = () => {
        // Trigger re-scan animation or API call
        setLoading(true);
        setTimeout(() => {
            fetchStats();
            setLastScan(new Date().toLocaleTimeString());
        }, 1500); // Mock scan delay
    };

    if (loading && !stats) return <div className="p-12 text-center text-gray-400">Loading Automation Engine...</div>;

    const allLogs = stats?.scan_stats?.findings || [];
    const logs = allLogs.filter(log => {
        if (activeFilter === 'ALL') return true;
        return log.status === activeFilter;
    });

    // Sort logs by status (FAIL first) then date if available
    logs.sort((a, b) => a.status === 'FAIL' ? -1 : 1);

    return (
        <div className="min-h-screen bg-gray-50 pb-20 animate-fade-in">
            {/* HEADER */}
            <div className="bg-white border-b border-gray-200 sticky top-0 z-20 shadow-sm">
                <div className="max-w-7xl mx-auto px-6 py-6">
                    <div className="flex justify-between items-center">
                        <div>
                            <div className="text-xs font-bold text-gray-500 mb-1 uppercase tracking-wider">Analytics Engine</div>
                            <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                                System Effectiveness
                                <span className="text-xs font-bold text-green-600 bg-green-50 px-2 py-0.5 rounded-full border border-green-100">LIVE</span>
                            </h1>
                        </div>
                        <div className="flex items-center gap-4">
                            <div className="text-right">
                                <span className="block text-xs font-bold text-gray-400">LAST SCAN</span>
                                <span className="text-sm font-medium text-gray-700">{lastScan}</span>
                            </div>
                            <button
                                onClick={handleRunScan}
                                className="bg-gray-900 text-white px-4 py-2 rounded-lg text-sm font-bold hover:bg-gray-800 transition-colors flex items-center gap-2 shadow-lg"
                            >
                                <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                                Run Poller
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            {/* METRICS GRID */}
            <div className="max-w-7xl mx-auto px-6 py-8">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">

                    {/* CARD 1: VELOCITY (Filter: PASS) */}
                    <div
                        onClick={() => setActiveFilter('PASS')}
                        className={`bg-white p-6 rounded-xl border shadow-sm hover:shadow-md transition-all relative overflow-hidden group cursor-pointer ${activeFilter === 'PASS' ? 'border-blue-500 ring-2 ring-blue-100' : 'border-gray-200'}`}
                    >
                        <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                            <Activity size={80} className="text-blue-600" />
                        </div>
                        <div className="flex items-center gap-2 mb-2">
                            <div className="p-2 bg-blue-50 rounded-lg text-blue-600">
                                <Activity size={20} />
                            </div>
                            <span className="text-sm font-bold text-gray-500">COMPLIANCE VELOCITY</span>
                        </div>
                        <div className="mt-4">
                            <span className="text-4xl font-bold text-gray-900">{stats?.compliance_velocity?.value}%</span>
                            <div className="flex items-center gap-2 mt-2 text-sm font-medium text-green-600">
                                <TrendingUp size={16} />
                                {stats?.compliance_velocity?.trend} this month
                            </div>
                        </div>
                        <div className="mt-4 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                            <div className="h-full bg-blue-500 rounded-full" style={{ width: `${stats?.compliance_velocity?.value}%` }}></div>
                        </div>
                    </div>

                    {/* CARD 2: FRESHNESS (Filter: ALL) */}
                    <div
                        onClick={() => setActiveFilter('ALL')}
                        className={`bg-white p-6 rounded-xl border shadow-sm hover:shadow-md transition-all relative overflow-hidden group cursor-pointer ${activeFilter === 'ALL' ? 'border-purple-500 ring-2 ring-purple-100' : 'border-gray-200'}`}
                    >
                        <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                            <Clock size={80} className="text-purple-600" />
                        </div>
                        <div className="flex items-center gap-2 mb-2">
                            <div className="p-2 bg-purple-50 rounded-lg text-purple-600">
                                <Clock size={20} />
                            </div>
                            <span className="text-sm font-bold text-gray-500">EVIDENCE FRESHNESS</span>
                        </div>
                        <div className="mt-4">
                            <span className="text-4xl font-bold text-gray-900">{stats?.evidence_freshness?.value}%</span>
                            <div className="flex items-center gap-2 mt-2 text-sm font-medium text-gray-500">
                                Avg Expiry: <span className="text-gray-900">{stats?.evidence_freshness?.days_to_expiry} days</span>
                            </div>
                        </div>
                        <div className="mt-4 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                            <div className="h-full bg-purple-500 rounded-full" style={{ width: `${stats?.evidence_freshness?.value}%` }}></div>
                        </div>
                    </div>

                    {/* CARD 3: COVERAGE GAP (Filter: FAIL) */}
                    <div
                        onClick={() => setActiveFilter('FAIL')}
                        className={`bg-white p-6 rounded-xl border shadow-sm hover:shadow-md transition-all relative overflow-hidden group cursor-pointer ${activeFilter === 'FAIL' ? 'border-red-500 ring-2 ring-red-100' : 'border-gray-200'}`}
                    >
                        <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                            <AlertTriangle size={80} className="text-amber-600" />
                        </div>
                        <div className="flex items-center gap-2 mb-2">
                            <div className="p-2 bg-amber-50 rounded-lg text-amber-600">
                                <AlertTriangle size={20} />
                            </div>
                            <span className="text-sm font-bold text-gray-500">COVERAGE GAP</span>
                        </div>
                        <div className="mt-4">
                            <span className="text-4xl font-bold text-gray-900">{stats?.coverage_gap?.value}%</span>
                            <div className={`flex items-center gap-2 mt-2 text-sm font-medium ${stats?.scan_stats?.failures > 0 ? 'text-red-600' : 'text-amber-600'}`}>
                                {stats?.scan_stats?.failures > 0
                                    ? <><AlertTriangle size={16} /> {stats.scan_stats.failures} Active Scan Failures</>
                                    : (stats?.coverage_gap?.value > 0 ? 'Action Required' : 'Fully Covered')
                                }
                            </div>
                        </div>
                        <div className="mt-4 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                            {/* Invert color: Gap is bad */}
                            <div className={`h-full rounded-full ${stats?.scan_stats?.failures > 0 ? 'bg-red-600' : 'bg-amber-500'}`} style={{ width: `${stats?.coverage_gap?.value}%` }}></div>
                        </div>
                    </div>
                </div>

                {/* AUTOMATION LOGS - DYNAMIC */}
                <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
                    <div className="px-6 py-4 border-b border-gray-100 flex justify-between items-center bg-gray-50/50">
                        <h3 className="font-bold text-gray-900">Recent Automation Logs</h3>
                        <span className="text-xs font-bold text-gray-500">LIVE STREAM</span>
                    </div>
                    <div className="divide-y divide-gray-100">
                        {logs.length > 0 ? logs.map((log, idx) => (
                            <div
                                key={idx}
                                onClick={() => setSelectedLog(log)}
                                className="px-6 py-3 flex items-center justify-between hover:bg-blue-50 transition-colors cursor-pointer group"
                            >
                                <div className="flex items-center gap-3">
                                    {log.status === 'PASS'
                                        ? <CheckCircle className="w-5 h-5 text-green-500" />
                                        : <AlertTriangle className="w-5 h-5 text-red-500 group-hover:scale-110 transition-transform" />
                                    }
                                    <div>
                                        <p className="text-sm font-bold text-gray-900 group-hover:text-blue-600">
                                            {log.title || log.details}
                                        </p>
                                        <p className="text-xs text-gray-500 flex items-center gap-2">
                                            Mapped to {log.control}
                                            {log.execution_id && <span className="font-mono bg-gray-100 px-1 rounded">{log.execution_id}</span>}
                                        </p>
                                    </div>
                                </div>
                                <span className="text-xs font-mono text-gray-400">
                                    {log.timestamp ? new Date(log.timestamp).toLocaleTimeString() : 'Just now'}
                                </span>
                            </div>
                        )) : (
                            <div className="p-6 text-center text-gray-400 text-sm">No automation logs available.</div>
                        )}
                    </div>
                </div>
            </div>

            {/* DETAIL MODAL */}
            {selectedLog && (
                <LogDetailModal
                    log={selectedLog}
                    onClose={() => setSelectedLog(null)}
                />
            )}
        </div>
    );
};

export default SystemEffectiveness;
