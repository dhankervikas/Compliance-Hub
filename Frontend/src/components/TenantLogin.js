import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import SecurityStatusBadge from './SecurityStatusBadge';
import config from '../config';

const TenantLogin = () => {
    const { tenantId } = useParams();
    const navigate = useNavigate();
    const { login, token } = useAuth(); // token here might be admin token if we switched from super-admin? 
    // Actually AuthContext exposes 'token' as the active one. 
    // We need to check localStorage for 'admin_token' directly to be safe, or expose 'adminToken' from context.

    // We'll read admin_token from localStorage for the "Continue as Admin" feature
    const adminToken = localStorage.getItem('admin_token');

    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            const result = await login(username, password, tenantId);
            if (result.success) {
                navigate(`/t/${tenantId}/dashboard`);
            } else {
                setError(result.error);
            }
        } catch (err) {
            setError("Login failed");
        } finally {
            setLoading(false);
        }
    };

    const handleContinueAsAdmin = async () => {
        setLoading(true);
        try {
            // Use Impersonate API
            // We need to use the admin_token to authorize this request
            // const res = await axios.post('http://localhost:8000/api/v1/auth/impersonate',
            //    { tenant_id: tenantId },
            //    { headers: { Authorization: `Bearer ${adminToken}` } }
            // );

            // FIX: Use centralized config
            const res = await axios.post(`${config.API_BASE_URL}/auth/impersonate`,
                { tenant_id: tenantId },
                { headers: { Authorization: `Bearer ${adminToken}` } }
            );

            const newToken = res.data.access_token;
            localStorage.setItem('token', newToken);

            // Force reload/navigate to pick up new context
            window.location.href = `/t/${tenantId}/dashboard`;

        } catch (err) {
            console.error("Impersonation failed:", err);
            const msg = err.response?.data?.detail || err.message || "Failed to continue as Admin.";
            setError(msg);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
            <div className="max-w-md w-full bg-white rounded-xl shadow-lg p-8 border border-gray-100">
                <div className="text-center mb-8">
                    <h2 className="text-2xl font-bold text-gray-900">Workspace Access</h2>
                    <p className="text-sm text-gray-500 mt-2">
                        Sign in to <span className="font-mono text-blue-600 font-bold">{tenantId}</span>
                    </p>
                </div>

                {adminToken && (
                    <div className="mb-6 p-4 bg-blue-50 border border-blue-100 rounded-lg text-center">
                        <p className="text-sm text-blue-800 mb-3">You are logged in as Super Admin</p>
                        <button
                            onClick={handleContinueAsAdmin}
                            disabled={loading}
                            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 rounded-lg transition-colors shadow-sm"
                        >
                            Continue as Admin
                        </button>
                        <div className="relative my-4">
                            <div className="absolute inset-0 flex items-center">
                                <div className="w-full border-t border-gray-200"></div>
                            </div>
                            <div className="relative flex justify-center text-sm">
                                <span className="px-2 bg-blue-50 text-gray-500">Or sign in as user</span>
                            </div>
                        </div>
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-6">
                    {error && (
                        <div className="bg-red-50 text-red-600 p-3 rounded text-sm border border-red-100 break-words">
                            <strong>Error: </strong> {error}
                            {error.includes("Login failed") && (
                                <div className="mt-2 text-xs text-gray-500">
                                    Check console (F12) for details.
                                    <br />Target: {config.API_BASE_URL}
                                </div>
                            )}
                        </div>
                    )}
                    <div>
                        <label className="block text-xs font-bold text-gray-700 uppercase mb-2">Username</label>
                        <input
                            value={username}
                            onChange={e => setUsername(e.target.value)}
                            className="w-full border border-gray-300 rounded-lg p-3 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
                            placeholder="username"
                            required
                        />
                    </div>
                    <div>
                        <label className="block text-xs font-bold text-gray-700 uppercase mb-2">Password</label>
                        <input
                            type="password"
                            value={password}
                            onChange={e => setPassword(e.target.value)}
                            className="w-full border border-gray-300 rounded-lg p-3 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
                            placeholder="••••••••"
                            required
                        />
                    </div>
                    <button
                        disabled={loading}
                        className="w-full bg-slate-800 hover:bg-slate-900 text-white font-bold py-3 rounded-lg transition-all disabled:opacity-50"
                    >
                        {loading ? 'Authenticating...' : 'Access Workspace'}
                    </button>

                    <div className="text-center mt-4">
                        <button
                            type="button"
                            onClick={() => navigate('/super-admin')}
                            className="text-xs text-gray-400 hover:text-gray-600 underline"
                        >
                            Back to Workspace Selection
                        </button>
                    </div>
                </form>
                <SecurityStatusBadge />
            </div>
        </div>
    );
};

export default TenantLogin;
