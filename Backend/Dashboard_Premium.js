
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import {
    Activity, Shield, CheckCircle, AlertTriangle,
    Filter, Search, Clock, FileText, Zap, ChevronDown
} from 'lucide-react';

const API_URL = 'https://assurisk-backend.onrender.com/api/v1';

const Dashboard = () => {
    const navigate = useNavigate();
    const [frameworks, setFrameworks] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filterFramework, setFilterFramework] = useState('All');
    const [searchTerm, setSearchTerm] = useState('');

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            const token = localStorage.getItem('token');
            const headers = { Authorization: `Bearer ${token}` };

            // Fetch Frameworks
            const fwRes = await axios.get(`${API_URL}/frameworks/`, { headers });
            const fwData = fwRes.data;

            // Fetch Stats for each
            const frameworksWithStats = await Promise.all(fwData.map(async (fw) => {
                try {
                    const statRes = await axios.get(`${API_URL}/frameworks/${fw.id}/stats`, { headers });
                    return statRes.data;
                } catch (e) {
                    return { ...fw, completion_percentage: 0, total_controls: 0, implemented_controls: 0 };
                }
            }));

            setFrameworks(frameworksWithStats);
            setLoading(false);
        } catch (err) {
            console.error("Failed to load dashboard data", err);
            setLoading(false);
        }
    };

    // --- MOCKED "DUE SOON" DATA ---
    const actionItems = [
        { id: 1, type: 'Vulnerability', title: 'Critical: Log4j in payment-service', due: 'Today', severity: 'Critical' },
        { id: 2, type: 'Policy', title: 'Review: Access Control Policy', due: 'Tomorrow', severity: 'High' },
        { id: 3, type: 'CAPA', title: 'Missing Evidence for CC6.1', due: '3 Days', severity: 'Medium' },
        { id: 4, type: 'Training', title: 'Security Awareness: 5 Employees Pending', due: '5 Days', severity: 'Low' }
    ];

    // Filter Logic
    const filteredFrameworks = frameworks.filter(fw => {
        const matchesSearch = fw.name.toLowerCase().includes(searchTerm.toLowerCase());
        const matchesFilter = filterFramework === 'All' || fw.name.includes(filterFramework);
        return matchesSearch && matchesFilter;
    });

    if (loading) return <div className="p-8 text-center text-gray-500">Loading Dashboard...</div>;

    return (
        <div className="p-6 space-y-6 animate-fade-in pb-20">
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
                        <button className="px-3 py-2 text-sm font-medium text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors">
                            + Add Widget
                        </button>
                    </div>
                </div>
            </div>

            {/* MAIN CONTENT GRID (2 COLUMNS) */}
            <div className="flex flex-col lg:flex-row gap-8 items-start">

                {/* LEFT COLUMN: FRAMEWORKS (Expands to fill) */}
                <div className="flex-1 w-full space-y-6">
                    <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                        <Shield className="w-5 h-5 text-blue-600" /> Framework Status
                    </h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {filteredFrameworks.map(fw => (
                            <div
                                key={fw.id}
                                onClick={() => navigate(`/frameworks/${fw.id}`)}
                                className="bg-white rounded-xl p-6 shadow-sm border border-gray-200 hover:shadow-md hover:border-blue-300 transition-all cursor-pointer group relative overflow-hidden"
                            >
                                <div className="flex justify-between items-start mb-4 relative z-10">
                                    <h3 className="text-lg font-bold text-gray-900 line-clamp-1" title={fw.name}>{fw.name}</h3>
                                    <span className={`px-2 py-1 rounded text-xs font-bold ${fw.completion_percentage === 100 ? 'bg-green-100 text-green-700' : 'bg-blue-50 text-blue-700'}`}>
                                        {fw.completion_percentage === 100 ? 'COMPLIANT' : 'ACTIVE'}
                                    </span>
                                </div>

                                <div className="flex items-end gap-2 mb-4 relative z-10">
                                    <span className="text-4xl font-extrabold text-gray-900">{fw.completion_percentage}%</span>
                                    <span className="text-sm text-gray-500 mb-1">Implemented</span>
                                </div>

                                {/* Progress Bar */}
                                <div className="w-full bg-gray-100 rounded-full h-2 mb-4 relative z-10">
                                    <div
                                        className={`h-2 rounded-full transition-all duration-1000 ${percentageColor(fw.completion_percentage)}`}
                                        style={{ width: `${fw.completion_percentage}%` }}
                                    ></div>
                                </div>

                                <div className="flex justify-between text-xs text-gray-500 relative z-10 border-t border-gray-50 pt-3">
                                    <span className="flex items-center gap-1">
                                        <CheckCircle className="w-3 h-3 text-green-500" /> {fw.implemented_controls} / {fw.total_controls} Controls
                                    </span>
                                    <span className="flex items-center gap-1">
                                        <Activity className="w-3 h-3 text-blue-500" /> Auto-Testing On
                                    </span>
                                </div>

                                {/* Decorative Background Blob */}
                                <div className="absolute -bottom-10 -right-10 w-32 h-32 bg-gray-50 rounded-full group-hover:bg-blue-50 transition-colors z-0"></div>
                            </div>
                        ))}
                        {/* Add Framework Button Card */}
                        <div className="border-2 border-dashed border-gray-200 rounded-xl p-6 flex flex-col items-center justify-center text-gray-400 hover:border-blue-300 hover:text-blue-500 cursor-pointer transition-colors min-h-[220px]">
                            <div className="w-12 h-12 bg-gray-50 rounded-full flex items-center justify-center mb-3">
                                <span className="text-2xl">+</span>
                            </div>
                            <span className="font-medium text-sm">Add New Framework</span>
                        </div>
                    </div>
                </div>

                {/* RIGHT COLUMN: WIDGETS (Fixed width on large screens) */}
                <div className="w-full lg:w-96 space-y-8 flex-shrink-0">

                    {/* Action Required (Due Soon) */}
                    <div>
                        <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                            <Clock className="w-5 h-5 text-orange-500" /> Action Required
                        </h2>
                        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                            <div className="divide-y divide-gray-100">
                                {actionItems.map(item => (
                                    <div key={item.id} className="p-4 flex items-start gap-4 hover:bg-gray-50 transition-colors cursor-pointer group">
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

                    {/* Compliance Capability (Mini Stats) */}
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
                                <span className="text-sm font-bold text-gray-900">98% Healthy</span>
                            </div>
                            <div className="flex justify-between items-center">
                                <span className="text-sm font-medium text-gray-700">Policy Adherence</span>
                                <span className="text-sm font-bold text-orange-600">Needs Review</span>
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

// Utilities
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
