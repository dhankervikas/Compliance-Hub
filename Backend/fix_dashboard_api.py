
import os

dashboard_path = r"..\..\Frontend\src\components\Dashboard.js"

# I'll rewrite the component to use absolute URLs and add logging
content = r"""import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { 
    Activity, 
    Shield, 
    Server, 
    RefreshCw 
} from 'lucide-react';

const Dashboard = () => {
    const navigate = useNavigate();
    const [frameworks, setFrameworks] = useState([]);
    const [loading, setLoading] = useState(true);
    const [integrationHealth, setIntegrationHealth] = useState({
        github: { status: 'healthy', lastSync: '10m ago' },
        aws: { status: 'syncing', lastSync: '1h ago' },
        jira: { status: 'warning', lastSync: '1d ago' }
    });

    useEffect(() => {
        fetchFrameworks();
    }, []);

    const fetchFrameworks = async () => {
        try {
            console.log("[Dashboard] Fetching frameworks...");
            // FIXED: Use absolute URL
            const res = await axios.get('http://localhost:8000/api/v1/frameworks/');
            console.log("[Dashboard] Frameworks data:", res.data);

            if (!Array.isArray(res.data)) {
                console.error("[Dashboard] Expected array but got:", typeof res.data, res.data);
                setFrameworks([]); 
                setLoading(false);
                return;
            }

            // Fetch stats for each to get progress
            const frameworksWithStats = await Promise.all(res.data.map(async (fw) => {
                try {
                    const statRes = await axios.get(`http://localhost:8000/api/v1/frameworks/${fw.id}/stats`);
                    return statRes.data;
                } catch (e) {
                    console.warn(`[Dashboard] Failed to fetch stats for fw ${fw.id}`, e);
                    return { ...fw, completion_percentage: 0, total_controls: 0, implemented_controls: 0 };
                }
            }));
            setFrameworks(frameworksWithStats);
            setLoading(false);
        } catch (err) {
            console.error("[Dashboard] Failed to load frameworks", err);
            // Don't crash the UI, just stop loading
            setLoading(false);
        }
    };

    // Calculate overall compliance
    const overallProgress = frameworks.length > 0
        ? Math.round(frameworks.reduce((acc, fw) => acc + (fw.completion_percentage || 0), 0) / frameworks.length)
        : 0;

    if (loading) return <div className="p-8 text-center text-gray-500">Loading Dashboard...</div>;

    return (
        <div className="space-y-8 animate-fade-in p-6">
            {/* Hero Section */}
            <div className="bg-gradient-to-r from-blue-900 to-slate-900 rounded-2xl p-8 text-white shadow-xl relative overflow-hidden">
                <div className="absolute top-0 right-0 w-64 h-64 bg-white opacity-5 rounded-full -mr-16 -mt-16 blur-2xl"></div>

                <div className="relative z-10 flex flex-col md:flex-row justify-between items-center gap-8">
                    <div>
                        <h1 className="text-3xl font-bold mb-2">Compliance Overview</h1>
                        <p className="text-blue-200">System is secure and monitoring is active.</p>

                        <div className="mt-6 flex items-center gap-4">
                            <div className="flex -space-x-2">
                                {[1, 2, 3].map(i => (
                                    <div key={i} className="w-10 h-10 rounded-full border-2 border-slate-800 bg-slate-700 flex items-center justify-center text-xs">
                                        User
                                    </div>
                                ))}
                                <div className="w-10 h-10 rounded-full border-2 border-slate-800 bg-slate-600 flex items-center justify-center text-xs">
                                    +12
                                </div>
                            </div>
                            <span className="text-sm text-blue-200">Active Contributors</span>
                        </div>
                    </div>

                    <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 min-w-[300px] border border-white/10">
                        <div className="flex justify-between items-end mb-2">
                            <span className="text-blue-100 font-medium">Overall Score</span>
                            <span className="text-4xl font-bold">{overallProgress}%</span>
                        </div>
                        <div className="w-full bg-slate-700 rounded-full h-2 mb-2">
                            <div
                                className="bg-blue-400 h-2 rounded-full transition-all duration-1000"
                                style={{ width: `${overallProgress}%` }}
                            ></div>
                        </div>
                        <div className="text-xs text-blue-200 flex justify-between">
                            <span>Last audit: 2 days ago</span>
                            <span className="text-green-300 flex items-center gap-1">
                                <Activity className="w-3 h-3" /> Trending Up
                            </span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Frameworks Grid */}
            <h2 className="text-xl font-bold text-gray-900">Active Frameworks</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {frameworks.length === 0 && (
                    <div className="col-span-3 text-center text-gray-400 py-10">
                        No frameworks found. Run the seeder?
                    </div>
                )}
                {frameworks.map(fw => (
                    <div
                        key={fw.id}
                        onClick={() => navigate(`/frameworks/${fw.id}`)}
                        className="bg-white rounded-xl p-6 shadow-sm border border-gray-100 hover:shadow-md hover:border-blue-200 transition-all cursor-pointer group"
                    >
                        <div className="flex justify-between items-start mb-4">
                            <div className="p-3 bg-blue-50 rounded-lg text-blue-600 group-hover:bg-blue-600 group-hover:text-white transition-colors">
                                <Shield className="w-6 h-6" />
                            </div>
                            <span className={`px-2 py-1 rounded text-xs font-bold ${fw.completion_percentage === 100 ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'
                                }`}>
                                {fw.completion_percentage === 100 ? 'COMPLIANT' : 'ACTIVE'}
                            </span>
                        </div>

                        <h3 className="text-lg font-bold text-gray-900 mb-1">{fw.name}</h3>
                        <p className="text-sm text-gray-500 mb-4 line-clamp-2">{fw.description}</p>

                        <div className="space-y-2">
                            <div className="flex justify-between text-sm">
                                <span className="text-gray-600">Progress</span>
                                <span className="font-medium text-gray-900">{fw.completion_percentage}%</span>
                            </div>
                            <div className="w-full bg-gray-100 rounded-full h-1.5">
                                <div
                                    className="bg-blue-600 h-1.5 rounded-full transition-all"
                                    style={{ width: `${fw.completion_percentage}%` }}
                                ></div>
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {/* Bottom Widgets */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Integration Health */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                    <h3 className="font-bold text-gray-900 mb-4 flex items-center gap-2">
                        <Server className="w-5 h-5 text-gray-500" /> Integration Health
                    </h3>
                    <div className="space-y-4">
                        {Object.entries(integrationHealth).map(([key, val]) => (
                            <div key={key} className="flex justify-between items-center p-3 hover:bg-gray-50 rounded-lg transition-colors border border-transparent hover:border-gray-100">
                                <div className="flex items-center gap-3">
                                    <div className={`w-2 h-2 rounded-full ${val.status === 'healthy' ? 'bg-green-500' :
                                            val.status === 'syncing' ? 'bg-blue-500 animate-pulse' : 'bg-orange-500'
                                        }`}></div>
                                    <span className="capitalize font-medium text-gray-700">{key}</span>
                                </div>
                                <div className="flex items-center gap-2">
                                    <span className="text-xs text-gray-400">{val.lastSync}</span>
                                    {val.status === 'syncing' && <RefreshCw className="w-3 h-3 text-blue-500 animate-spin" />}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
"""

try:
    with open(dashboard_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"SUCCESS: Updated {os.path.abspath(dashboard_path)}")
except Exception as e:
    print(f"ERROR: Failed to update file. {e}")
