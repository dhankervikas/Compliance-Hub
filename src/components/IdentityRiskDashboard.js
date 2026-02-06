
import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { AlertTriangle, UserX, ShieldAlert } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const IdentityRiskDashboard = () => {
    const [risks, setRisks] = useState([]);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchRisks = async () => {
            try {
                const res = await api.get('/people/risks');
                setRisks(res.data);
            } catch (err) {
                console.error("Failed to fetch risks", err);
            } finally {
                setLoading(false);
            }
        };
        fetchRisks();
    }, []);

    if (loading) return <div className="p-6 text-gray-500">Analyzing Identity Risks...</div>;

    if (risks.length === 0) return (
        <div className="p-6 bg-green-50 border border-green-200 rounded-lg flex items-center gap-4 m-6">
            <div className="p-2 bg-green-100 rounded-full text-green-600">
                <ShieldAlert size={24} />
            </div>
            <div>
                <h3 className="font-bold text-green-800">No Identity Risks Detected</h3>
                <p className="text-sm text-green-700">All active system users correspond to active employment records.</p>
            </div>
        </div>
    );

    return (
        <div className="p-6">
            <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-6 rounded-r-lg">
                <div className="flex items-start">
                    <div className="flex-shrink-0">
                        <AlertTriangle className="h-5 w-5 text-red-500" />
                    </div>
                    <div className="ml-3">
                        <h3 className="text-sm font-medium text-red-800">Critical Compliance Risks Detected</h3>
                        <div className="mt-2 text-sm text-red-700">
                            <p>Found {risks.length} "Zombie Accounts" - Terminated employees who still have active system access.</p>
                        </div>
                    </div>
                </div>
            </div>

            <div className="grid gap-6">
                {risks.map((risk, index) => (
                    <div key={index} className="bg-white border border-red-200 rounded-lg shadow-sm overflow-hidden">
                        <div className="px-6 py-4 border-b border-gray-100 flex justify-between items-center bg-red-50/30">
                            <div className="flex items-center gap-3">
                                <div className="p-2 bg-red-100 rounded-full text-red-600">
                                    <UserX size={20} />
                                </div>
                                <div>
                                    <h4 className="font-bold text-gray-900">{risk.person.name}</h4>
                                    <p className="text-xs text-gray-500">{risk.person.email}</p>
                                </div>
                            </div>
                            <span className="px-3 py-1 bg-red-100 text-red-800 text-xs font-bold rounded uppercase tracking-wider">
                                {risk.risk_level}
                            </span>
                        </div>

                        <div className="px-6 py-4 grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div>
                                <h5 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Finding</h5>
                                <p className="text-sm text-gray-800">{risk.description}</p>
                                <div className="mt-2 flex gap-2 flex-wrap">
                                    {risk.framework_mapping.map(fw => (
                                        <span key={fw} className="text-[10px] bg-gray-100 text-gray-600 px-2 py-1 rounded border border-gray-200">
                                            {fw}
                                        </span>
                                    ))}
                                </div>
                            </div>

                            <div className="flex flex-col items-end justify-center">
                                <button
                                    onClick={() => navigate('../admin/users')}
                                    className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded text-sm font-medium transition-colors shadow-sm"
                                >
                                    Deactivate User Account
                                </button>
                                <p className="text-xs text-gray-400 mt-2">
                                    User ID: {risk.user_account.username}
                                </p>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default IdentityRiskDashboard;
