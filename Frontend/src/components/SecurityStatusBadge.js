import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { ShieldCheck, Lock, Users, Activity, AlertTriangle } from 'lucide-react';

const SecurityStatusBadge = () => {
    const [status, setStatus] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchStatus = async () => {
            try {
                // Fetch from public endpoint
                const res = await api.get('/health/security-integrity');
                setStatus(res.data);
            } catch (err) {
                console.error("Failed to fetch security status", err);
                const errorMsg = err.response?.status
                    ? `Status: ${err.response.status}`
                    : "Connecting..."; // Show connecting instead of error initially
                setStatus({ error: true, errorMsg });
            } finally {
                setLoading(false);
            }
        };

        fetchStatus();

        // Refresh every 30s to simulate "Live Pulse"
        const interval = setInterval(fetchStatus, 30000);
        return () => clearInterval(interval);
    }, []);


    // Helper to render indicators (even in mock/loading state if needed)
    const Indicator = ({ label, active, icon: Icon, loading }) => (
        <div className="flex flex-col items-center gap-1 group cursor-help relative">
            <div className={`p-1.5 rounded-full transition-all duration-500 ${loading ? 'bg-gray-100 text-gray-400 animate-pulse' : active ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'}`}>
                <Icon size={14} />
            </div>
            <span className="text-[10px] uppercase font-bold text-gray-500 tracking-wider">{label}</span>
            <div className={`w-1.5 h-1.5 rounded-full mt-1 ${loading ? 'bg-gray-300' : active ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />

            {/* Tooltip */}
            <div className="absolute bottom-full mb-2 hidden group-hover:block bg-gray-900 text-white text-xs p-2 rounded w-32 text-center z-10">
                {loading ? "Checking..." : active ? `${label} Active` : `${label} Offline`}
            </div>
        </div>
    );

    // If completely failed/loading, show a skeleton or "Checking" state instead of nothing
    if (loading || (!status && !loading)) {
        return (
            <div className="mt-8 border-t border-gray-100 pt-6">
                <div className="flex justify-center gap-8 opacity-50">
                    <Indicator label="Isolation" loading={true} icon={Users} />
                    <Indicator label="Encryption" loading={true} icon={Lock} />
                    <Indicator label="Guard" loading={true} icon={Activity} />
                </div>
                <div className="text-center mt-4">
                    <span className="text-[10px] text-gray-400">Verifying System Integrity...</span>
                </div>
            </div>
        );
    }

    // Error State (But still show icons in red/offline)
    if (status?.error) {
        return (
            <div className="mt-8 border-t border-gray-100 pt-6">
                <div className="flex justify-center gap-8">
                    <Indicator label="Isolation" active={false} icon={Users} />
                    <Indicator label="Encryption" active={false} icon={Lock} />
                    <Indicator label="Guard" active={false} icon={Activity} />
                </div>
                <div className="text-center mt-4">
                    <span className="inline-flex items-center gap-1 text-[10px] text-red-500 bg-red-50 px-2 py-1 rounded-full border border-red-100">
                        <AlertTriangle size={10} />
                        System Check Unavailable
                    </span>
                </div>
            </div>
        );
    }

    return (
        <div className="mt-8 border-t border-gray-100 pt-6">
            <div className="flex items-center justify-center gap-2 mb-4 text-xs text-gray-400">
                <ShieldCheck size={14} className="text-blue-500" />
                <span>System Integrity Verified</span>
                <span className="text-gray-300">•</span>
                <span className="font-mono">{new Date(status.verified_at).toLocaleTimeString()}</span>
            </div>

            <div className="flex justify-center gap-8">
                <Indicator
                    label="Isolation"
                    active={status?.checks?.tenant_isolation}
                    icon={Users}
                />
                <Indicator
                    label="Encryption"
                    active={status?.checks?.data_encryption}
                    icon={Lock}
                />
                <Indicator
                    label="Guard"
                    active={status?.checks?.access_guard}
                    icon={Activity}
                />
            </div>

            <div className="text-center mt-4">
                <span className="text-[10px] text-gray-300 bg-gray-50 px-2 py-1 rounded-full border border-gray-100">
                    Trusted Platform v{status.system_version}
                </span>
            </div>
        </div>
    );
};

export default SecurityStatusBadge;
