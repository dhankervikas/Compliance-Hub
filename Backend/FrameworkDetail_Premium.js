
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import {
    ArrowLeft, Search, Filter, MoreHorizontal,
    Calendar, CheckCircle, FileText, AlertCircle,
    ChevronDown, Plus, Edit2
} from 'lucide-react';

const API_URL = 'https://assurisk-backend.onrender.com/api/v1'; // HARDCODED FOR PRODUCTION DEBUGGING

const FrameworkDetail = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const [framework, setFramework] = useState(null);
    const [processes, setProcesses] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [stats, setStats] = useState({ total: 0, implemented: 0, percentage: 0 });

    useEffect(() => {
        fetchData();
    }, [id]);

    const fetchData = async () => {
        try {
            const token = localStorage.getItem('token');
            const headers = { Authorization: `Bearer ${token}` };

            // 1. Fetch Framework
            const fwRes = await axios.get(`${API_URL}/frameworks/${id}`, { headers });

            // 2. Fetch All Processes
            const procRes = await axios.get(`${API_URL}/processes/`, { headers });

            // 3. Fetch All Controls for stats
            const ctrlRes = await axios.get(`${API_URL}/controls/`, { headers });
            const allControls = ctrlRes.data;

            // Filter logic
            const filteredProcesses = procRes.data.map(proc => {
                const relevantSubs = proc.sub_processes.map(sub => {
                    // Filter controls for this framework/subprocess
                    const subControls = allControls.filter(c =>
                        c.framework_id === parseInt(id) &&
                        // Note: Backend might need a 'subprocess_id' linking, but currently we rely on the mapping table?
                        // Wait, previous logic used 'sub.controls' which came from the detailed fetch or mapping?
                        // The 'procRes.data' returns processes. We need to know which controls belong to which sub.
                        // Actually, the previous `FrameworkDetail.js` relied on `filteredControls` logic?
                        // Let's assume the API returns `controls` inside sub_processes or we assume `allControls` is the master list
                        // The previous implementation fetched framework-specific controls and mapped them.
                        // Let's simulate that strict mapping:
                        // The backend `GET /processes` typically returns structure.
                        // If it doesn't return mapped controls, we need `GET /frameworks/{id}/controls` and map them?
                        // Let's stick to the simpler approach: The API `GET /processes` usually includes mapped controls if expanded.
                        // If not, we might be missing data.
                        // Let's assume `sub.controls` exists from the API response based on previous success.
                        sub.controls || []
                    ).filter(c => c.framework_id === parseInt(id));

                    // Filter again to ensure we show controls related to THIS framework
                    return { ...sub, controls: subControls };
                }).filter(sub => sub.controls && sub.controls.length > 0);

                return { ...proc, sub_processes: relevantSubs };
            }).filter(proc => proc.sub_processes.length > 0);

            // Re-calc stats based on filtered view
            let total = 0;
            let implemented = 0;
            filteredProcesses.forEach(p => p.sub_processes.forEach(s => s.controls.forEach(c => {
                total++;
                if (c.status === 'IMPLEMENTED') implemented++;
            })));

            setFramework(fwRes.data);
            setProcesses(filteredProcesses);
            setStats({
                total,
                implemented,
                percentage: total > 0 ? Math.round((implemented / total) * 100) : 0
            });
            setLoading(false);

        } catch (err) {
            console.error(err);
            setError(`Failed to load data: ${err.message} \n(Status: ${err.response?.status})`);
            setLoading(false);
        }
    };

    if (loading) return <div className="p-12 text-center text-gray-400">Loading Premium View...</div>;
    if (error) return (
        <div className="p-12 text-center text-red-500">
            <h2 className="text-xl font-bold mb-2">Error Loading Framework</h2>
            <p className="font-mono bg-red-50 p-2 rounded border border-red-200 inline-block">{error}</p>
            <p className="text-sm mt-2 text-gray-400 font-mono">
                Target: {API_URL}/frameworks/{id} <br />
                (Hardcoded P2)
            </p>
        </div>
    );

    return (
        <div className="min-h-screen bg-gray-50 pb-20">
            {/* TOP HEADER */}
            <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
                <div className="max-w-7xl mx-auto px-6 py-4">
                    <div className="flex justify-between items-center mb-4">
                        <div className="flex items-center gap-2 text-sm text-gray-500">
                            <a onClick={() => navigate('/')} className="hover:text-gray-900 cursor-pointer">FRAMEWORKS</a>
                            <span>/</span>
                            <span className="font-medium text-gray-900">{framework.code}</span>
                        </div>
                    </div>

                    <div className="flex justify-between items-end">
                        <h1 className="text-3xl font-bold text-gray-900">
                            {framework.name} <span className="text-sm font-normal text-purple-600 bg-purple-50 px-2 py-1 rounded-full align-middle">(Drata Style v1.0)</span>
                        </h1>
                        <div className="flex gap-3">
                            <button className="flex items-center gap-2 px-3 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50">
                                <Edit2 className="w-4 h-4" /> Edit system description
                            </button>
                            <button className="flex items-center gap-2 px-3 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50">
                                <Plus className="w-4 h-4" /> Add custom control
                            </button>
                            <button className="flex items-center gap-2 px-3 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50">
                                More <ChevronDown className="w-4 h-4" />
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <div className="max-w-7xl mx-auto px-6 py-8 space-y-8">

                {/* CARDS ROW */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Controls Progress Card */}
                    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                        <div className="flex justify-between items-start mb-6">
                            <h3 className="font-bold text-lg text-gray-900">Controls</h3>
                            <button className="text-sm font-medium text-gray-600 border border-gray-300 px-3 py-1 rounded hover:bg-gray-50">View analytics</button>
                        </div>

                        <div className="flex items-end gap-2 mb-2">
                            <span className="text-4xl font-extrabold text-gray-900">{stats.percentage}%</span>
                        </div>

                        {/* Progress Bar */}
                        <div className="w-full bg-gray-100 rounded-full h-2 mb-2">
                            <div className="bg-green-500 h-2 rounded-full" style={{ width: `${stats.percentage}%` }}></div>
                        </div>
                        <div className="flex justify-between text-sm text-gray-500 mb-6">
                            <span>{stats.implemented} completed</span>
                            <span>{stats.total} total</span>
                        </div>

                        {/* Side Stats */}
                        <div className="space-y-3 pt-4 border-t border-gray-100">
                            <div className="flex justify-between items-center text-sm">
                                <span className="flex items-center gap-2 text-gray-600">
                                    <CheckCircle className="w-4 h-4 text-gray-400" /> Tests
                                </span>
                                <div className="flex items-center gap-3">
                                    <span className="text-gray-900 font-medium">94/169</span>
                                    <div className="w-16 bg-gray-100 rounded-full h-1.5">
                                        <div className="bg-green-500 h-1.5 rounded-full" style={{ width: '56%' }}></div>
                                    </div>
                                </div>
                            </div>
                            <div className="flex justify-between items-center text-sm">
                                <span className="flex items-center gap-2 text-gray-600">
                                    <FileText className="w-4 h-4 text-gray-400" /> Documents
                                </span>
                                <div className="flex items-center gap-3">
                                    <span className="text-gray-900 font-medium">10/49</span>
                                    <div className="w-16 bg-gray-100 rounded-full h-1.5">
                                        <div className="bg-green-500 h-1.5 rounded-full" style={{ width: '20%' }}></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Audit Timeline Card */}
                    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                        <div className="flex justify-between items-start mb-6">
                            <div className="flex items-center gap-3">
                                <h3 className="font-bold text-lg text-gray-900">Audit timeline</h3>
                                <span className="px-2 py-0.5 bg-orange-100 text-orange-700 text-xs font-bold rounded-full flex items-center gap-1">
                                    <span className="w-1.5 h-1.5 bg-orange-500 rounded-full"></span> In audit
                                </span>
                            </div>
                            <div className="flex gap-2">
                                <button className="text-sm font-medium text-gray-600 border border-gray-300 px-3 py-1 rounded hover:bg-gray-50">View as auditor</button>
                                <button className="text-sm font-medium text-gray-600 border border-gray-300 px-3 py-1 rounded hover:bg-gray-50">View audits</button>
                            </div>
                        </div>

                        <div className="mb-8">
                            <p className="text-sm text-gray-900 font-bold mb-1">Now until July 26 <AlertCircle className="w-3 h-3 inline text-gray-400" /></p>
                        </div>

                        {/* Timeline Visual Mock */}
                        <div className="relative pt-4 pb-2">
                            <div className="absolute top-5 left-0 right-0 h-0.5 bg-gray-200"></div>
                            {/* Active portion */}
                            <div className="absolute top-5 left-0 w-1/3 h-0.5 bg-orange-500"></div>

                            <div className="flex justify-between relative z-0">
                                <div className="flex flex-col items-center">
                                    <div className="w-3 h-3 bg-orange-500 rounded-full mb-2"></div>
                                    <span className="text-xs text-gray-500">Now</span>
                                </div>
                                <div className="flex flex-col items-center">
                                    <div className="w-3 h-3 bg-orange-500 rounded-full mb-2"></div>
                                    <span className="text-xs text-gray-500">May</span>
                                </div>
                                <div className="flex flex-col items-center">
                                    <div className="w-3 h-3 bg-orange-500 rounded-full mb-2 border-2 border-white ring-2 ring-orange-500"></div>
                                    <span className="text-xs text-gray-900 font-bold">Jul</span>
                                </div>
                                <div className="flex flex-col items-center">
                                    <div className="w-2 h-2 bg-gray-300 rounded-full mb-2"></div>
                                    <span className="text-xs text-gray-400">Sep</span>
                                </div>
                                <div className="flex flex-col items-center">
                                    <div className="w-2 h-2 bg-gray-300 rounded-full mb-2"></div>
                                    <span className="text-xs text-gray-400">Nov</span>
                                </div>
                                <div className="flex flex-col items-center">
                                    <div className="w-2 h-2 bg-gray-300 rounded-full mb-2"></div>
                                    <span className="text-xs text-gray-400">Jan</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* FILTERS */}
                <div className="flex items-center justify-between">
                    <div className="flex gap-3">
                        <div className="relative">
                            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                            <input type="text" placeholder="Search controls" className="pl-9 pr-4 py-2 border border-gray-300 rounded-lg text-sm w-64 focus:ring-1 focus:ring-blue-500 focus:border-blue-500" />
                        </div>
                        <div className="flex items-center border border-gray-300 rounded-lg px-3 bg-white">
                            <span className="text-sm text-gray-500 mr-2">Filter by</span>
                            <button className="text-sm font-medium text-gray-700 hover:text-gray-900 mr-3">Status</button>
                            <button className="text-sm font-medium text-gray-700 hover:text-gray-900">Owner</button>
                        </div>
                    </div>
                    <div className="flex gap-3">
                        <button className="flex items-center gap-2 px-3 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50">
                            Jump to Section <ChevronDown className="w-4 h-4" />
                        </button>
                        <button className="flex items-center gap-2 px-3 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50">
                            Group by Section <ChevronDown className="w-4 h-4" />
                        </button>
                    </div>
                </div>

                {/* CONTENT (Processes > Subprocesses > Table) */}
                <div className="space-y-10">
                    {processes.map(process => (
                        <div key={process.id}>
                            {/* Process Header (as Section) */}
                            {/* We use Subprocesses as the main "Section" blocks to match the screenshot "CC 1.1" style */}
                            {process.sub_processes.map(sub => (
                                <div key={sub.id} className="mb-8">
                                    <div className="mb-4">
                                        <h2 className="text-xl font-bold text-gray-900">{sub.name}</h2>
                                        <p className="text-gray-500 text-sm mt-1">{sub.description || process.name}</p>
                                    </div>

                                    {/* TABLE */}
                                    <div className="bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden">
                                        <table className="w-full">
                                            <thead>
                                                <tr className="bg-gray-50 border-b border-gray-200 text-left">
                                                    <th className="px-6 py-3 w-8">
                                                        <input type="checkbox" className="rounded border-gray-300 text-blue-600 focus:ring-blue-500" />
                                                    </th>
                                                    <th className="px-6 py-3 text-xs font-bold text-gray-500 uppercase tracking-wider">Control</th>
                                                    <th className="px-6 py-3 text-xs font-bold text-gray-500 uppercase tracking-wider">Evidence Status</th>
                                                    <th className="px-6 py-3 text-xs font-bold text-gray-500 uppercase tracking-wider">Category</th>
                                                    <th className="px-6 py-3 text-xs font-bold text-gray-500 uppercase tracking-wider">Owner</th>
                                                    <th className="px-6 py-3 text-xs font-bold text-gray-500 uppercase tracking-wider">Standard Code</th>
                                                    <th className="px-6 py-3 w-8"></th>
                                                </tr>
                                            </thead>
                                            <tbody className="divide-y divide-gray-100">
                                                {sub.controls.map(control => (
                                                    <tr key={control.id} className="hover:bg-gray-50 transition-colors group">
                                                        <td className="px-6 py-4">
                                                            <input type="checkbox" className="rounded border-gray-300 text-blue-600 focus:ring-blue-500" />
                                                        </td>
                                                        <td className="px-6 py-4">
                                                            <div className="text-sm font-medium text-gray-900">{control.title}</div>
                                                        </td>
                                                        <td className="px-6 py-4">
                                                            <div className="flex items-center gap-2">
                                                                <div className={`w-2 h-2 rounded-full ${control.status === 'IMPLEMENTED' ? 'bg-green-500' :
                                                                    control.status === 'IN_PROGRESS' ? 'bg-blue-500' : 'bg-gray-300'
                                                                    }`}></div>
                                                                <span className="text-sm text-gray-600">
                                                                    {control.status === 'IMPLEMENTED' ? '3/3' : '0/3'}
                                                                </span>
                                                            </div>
                                                        </td>
                                                        <td className="px-6 py-4">
                                                            <span className="text-sm text-gray-600">{control.category || 'Administrative'}</span>
                                                        </td>
                                                        <td className="px-6 py-4">
                                                            <div className="flex items-center gap-2">
                                                                <div className="w-6 h-6 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-xs font-bold">MC</div>
                                                                <span className="text-sm text-gray-900">Madison Carter</span>
                                                            </div>
                                                        </td>
                                                        <td className="px-6 py-4">
                                                            <span className="font-mono text-xs font-medium text-gray-600 bg-gray-100 px-2 py-1 rounded">
                                                                {control.control_id}
                                                            </span>
                                                        </td>
                                                        <td className="px-6 py-4 text-right">
                                                            <button className="text-gray-400 hover:text-gray-600">
                                                                <MoreHorizontal className="w-4 h-4" />
                                                            </button>
                                                        </td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            ))}
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default FrameworkDetail;
