import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { Building, Plus, User, LogOut, ArrowRight, Shield, Settings } from 'lucide-react';

const Workspaces = () => {
    const { token, logout, user } = useAuth();
    const navigate = useNavigate();
    const [tenants, setTenants] = useState([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);
    const [formData, setFormData] = useState({
        org_name: '',
        admin_username: '',
        admin_email: '',
        password: ''
    });
    const [error, setError] = useState(null);

    // Edit Modal State
    const [showEditModal, setShowEditModal] = useState(false);
    const [editingTenant, setEditingTenant] = useState(null);
    const [entitlements, setEntitlements] = useState(null);
    const [saving, setSaving] = useState(false);
    const [activeTab, setActiveTab] = useState('frameworks'); // frameworks | features

    useEffect(() => {
        fetchTenants();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const fetchTenants = async () => {
        try {
            const res = await api.get('/users/tenants');
            setTenants(res.data);
        } catch (err) {
            console.error(err);
            setError("Failed to load workspaces.");
        } finally {
            setLoading(false);
        }
    };

    const handleCreate = async (e) => {
        e.preventDefault();
        try {
            await api.post('/users/tenants', formData);
            setShowModal(false);
            setFormData({ org_name: '', admin_username: '', admin_email: '', password: '' });
            fetchTenants();
        } catch (err) {
            setError(err.response?.data?.detail || "Failed to create workspace");
        }
    };

    const handleSelectWorkspace = async (tenantId) => {
        // "Switch Context" Logic:
        // 1. Call /impersonate to get a scoped token for this tenant
        // 2. Switch to this new token and reload/navigate

        try {
            const res = await api.post('/auth/impersonate',
                { tenant_id: tenantId }
            );

            const newToken = res.data.access_token;

            // Backup Admin Token if not already
            if (!localStorage.getItem('admin_token')) {
                localStorage.setItem('admin_token', token);
            }

            // Set new active token
            localStorage.setItem('token', newToken);

            console.log("Impersonation successful. Switching context...");
            // Force hard reload to ensure clean state and correct AuthContext initialization
            window.location.href = `/t/${tenantId}/dashboard`;

        } catch (err) {
            console.error("Impersonation failed:", err);
            // Fallback to manual login
            window.location.href = `/t/${tenantId}/login`;
        }
    };

    const handleCopyMagicLink = (tenantId) => {
        const magicLink = `https://app.assurisk.ai/t/${tenantId}/login`;
        navigator.clipboard.writeText(magicLink);
        alert(`Magic Link Copied:\n${magicLink}`);
    };

    const handleStatusToggle = async (tenantId, currentStatus) => {
        if (!window.confirm(`Are you sure you want to ${currentStatus ? 'deactivate' : 'activate'} this workspace?`)) return;

        try {
            await api.patch(`/users/tenants/${tenantId}/status`, {
                is_active: !currentStatus
            });
            fetchTenants();
        } catch (err) {
            console.error("Failed to update status", err);
            alert("Failed to update status");
        }
    };

    const handleEdit = async (tenant) => {
        setEditingTenant(tenant);
        setShowEditModal(true);
        setEntitlements(null); // Reset
        try {
            const res = await api.get(`/users/tenants/${tenant.tenant_id}/entitlements`);
            setEntitlements(res.data);
        } catch (err) {
            console.error("Failed to load entitlements", err);
            const status = err.response?.status;
            const detail = err.response?.data?.detail;
            alert(`Failed to load entitlement details. Error ${status}: ${detail}`);
            setShowEditModal(false);
        }
    };

    const handleSaveEntitlements = async () => {
        if (!entitlements || !editingTenant) return;
        setSaving(true);
        try {
            // Prepare Payload
            const payload = {
                framework_ids: entitlements.frameworks.filter(f => f.is_active).map(f => f.id),
                active_features: entitlements.features.filter(f => f.is_active).map(f => f.key),
                account_status: entitlements.account_status
            };

            await api.put(`/users/tenants/${editingTenant.tenant_id}/entitlements`, payload);
            setShowEditModal(false);
            fetchTenants(); // Refresh main list
        } catch (err) {
            console.error("Failed to save entitlements", err);
            alert("Failed to save changes.");
        } finally {
            setSaving(false);
        }
    };

    const toggleFramework = (id) => {
        if (!entitlements) return;
        setEntitlements(prev => ({
            ...prev,
            frameworks: prev.frameworks.map(f =>
                f.id === id ? { ...f, is_active: !f.is_active } : f
            )
        }));
    };

    const toggleFeature = (key) => {
        if (!entitlements) return;
        setEntitlements(prev => ({
            ...prev,
            features: prev.features.map(f =>
                f.key === key ? { ...f, is_active: !f.is_active } : f
            )
        }));
    };

    if (loading) return <div className="p-10 text-center">Loading Workspaces...</div>;

    return (
        <div className="min-h-screen bg-slate-900 flex flex-col items-center justify-center p-6 font-sans">
            <div className="max-w-4xl w-full">
                {/* Header */}
                <div className="flex items-center justify-between mb-8">
                    <div className="flex items-center gap-3 text-white">
                        <div className="p-3 bg-blue-600 rounded-lg">
                            <Shield className="w-8 h-8" />
                        </div>
                        <div>
                            <h1 className="text-2xl font-bold">Select Workspace</h1>
                            <p className="text-slate-400">Welcome back, {user?.username}</p>
                        </div>
                    </div>
                    <button
                        onClick={logout}
                        className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors"
                    >
                        <LogOut size={18} />
                        Sign Out
                    </button>
                </div>

                {error && (
                    <div className="bg-red-500/10 border border-red-500/50 text-red-500 p-4 rounded-lg mb-6">
                        {error}
                    </div>
                )}

                {/* Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {tenants.map((t) => (
                        <div
                            key={t.tenant_id}
                            className="bg-slate-800 border border-slate-700 hover:border-blue-500 p-6 rounded-xl transition-all group relative overflow-hidden flex flex-col justify-between"
                        >
                            {/* Card Content */}
                            <div onClick={() => t.is_active && handleSelectWorkspace(t.tenant_id)} className={`cursor-pointer ${!t.is_active && 'opacity-50 grayscale cursor-not-allowed'}`}>
                                <div className="flex justify-between items-start mb-4">
                                    <div className={`p-2 rounded-lg transition-colors ${t.is_active ? 'bg-slate-700/50 text-blue-400 group-hover:bg-blue-600 group-hover:text-white' : 'bg-slate-800 text-slate-600'}`}>
                                        <Building size={24} />
                                    </div>
                                    <div className="flex gap-2">
                                        <span className={`text-xs font-bold px-2 py-1 rounded ${t.is_active ? 'bg-green-500/10 text-green-500' : 'bg-red-500/10 text-red-500'}`}>
                                            {t.is_active ? 'ACTIVE' : 'INACTIVE'}
                                        </span>
                                        <span className="text-xs font-medium text-slate-500 bg-slate-900/50 px-2 py-1 rounded">
                                            {t.user_count} User{t.user_count !== 1 ? 's' : ''}
                                        </span>
                                    </div>
                                </div>
                                <h3 className="text-lg font-bold text-white mb-1 group-hover:text-blue-400">
                                    {t.name || t.tenant_id}
                                </h3>
                                <p className="text-slate-400 text-sm mb-4">Organization Workspace</p>

                                {t.is_active && (
                                    <div className="flex items-center gap-2 text-sm text-blue-500 font-medium opacity-0 group-hover:opacity-100 transition-opacity mb-4">
                                        Enter Workspace <ArrowRight size={16} />
                                    </div>
                                )}
                            </div>

                            <button
                                onClick={(e) => {
                                    e.stopPropagation();
                                    handleEdit(t);
                                }}
                                className="absolute top-4 right-4 p-2 bg-slate-800 text-slate-400 hover:text-white rounded-lg opacity-0 group-hover:opacity-100 transition-all hover:bg-slate-700"
                                title="Edit Entitlements"
                            >
                                <Settings size={16} />
                            </button>
                            {/* Settings Button */}

                            {/* Utility Actions */}
                            <div className="pt-4 border-t border-slate-700 mt-2 flex gap-2">
                                <button
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        handleStatusToggle(t.tenant_id, t.is_active);
                                    }}
                                    className={`flex-1 py-2 text-xs font-bold rounded transition-colors ${t.is_active
                                        ? 'text-red-400 hover:text-white hover:bg-red-500/20'
                                        : 'text-green-400 hover:text-white hover:bg-green-500/20'
                                        }`}
                                >
                                    {t.is_active ? 'Deactivate' : 'Activate'}
                                </button>
                                <button
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        handleCopyMagicLink(t.tenant_id);
                                    }}
                                    className="w-full py-2 text-xs font-medium text-slate-400 hover:text-white bg-slate-900/50 hover:bg-slate-700 rounded transition-colors flex items-center justify-center gap-2"
                                >
                                    <span>🔗</span> Copy Client Link
                                </button>
                            </div>
                        </div>
                    ))}

                    {/* New Workspace Card */}
                    <button
                        onClick={() => navigate('/super-admin/onboarding')}
                        className="bg-slate-800/50 border border-dashed border-slate-700 hover:border-blue-500 hover:bg-slate-800 p-6 rounded-xl flex flex-col items-center justify-center gap-4 text-slate-500 hover:text-blue-400 transition-all min-h-[200px]"
                    >
                        <div className="p-4 rounded-full bg-slate-700/30">
                            <Plus size={32} />
                        </div>
                        <span className="font-bold">Create New Workspace</span>
                    </button>
                </div>
            </div >

            {/* Modal */}
            {
                showModal && (
                    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 backdrop-blur-sm">
                        <div className="bg-slate-800 p-8 rounded-2xl w-full max-w-md border border-slate-700 shadow-2xl">
                            <h2 className="text-xl font-bold text-white mb-6">Create New Workspace</h2>
                            <form onSubmit={handleCreate} className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-slate-400 mb-1">Organization Name</label>
                                    <input
                                        className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-white focus:ring-2 focus:ring-blue-500 outline-none"
                                        placeholder="e.g. Acme Corp"
                                        required
                                        value={formData.org_name}
                                        onChange={e => setFormData({ ...formData, org_name: e.target.value })}
                                    />
                                </div>
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-sm font-medium text-slate-400 mb-1">Admin Username</label>
                                        <input
                                            className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-white focus:ring-2 focus:ring-blue-500 outline-none"
                                            placeholder="admin_acme"
                                            required
                                            value={formData.admin_username}
                                            onChange={e => setFormData({ ...formData, admin_username: e.target.value })}
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-slate-400 mb-1">Admin Email</label>
                                        <input
                                            className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-white focus:ring-2 focus:ring-blue-500 outline-none"
                                            type="email"
                                            placeholder="admin@acme.com"
                                            required
                                            value={formData.admin_email}
                                            onChange={e => setFormData({ ...formData, admin_email: e.target.value })}
                                        />
                                    </div>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-slate-400 mb-1">Password</label>
                                    <input
                                        className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2.5 text-white focus:ring-2 focus:ring-blue-500 outline-none"
                                        type="password"
                                        required
                                        value={formData.password}
                                        onChange={e => setFormData({ ...formData, password: e.target.value })}
                                    />
                                </div>

                                <div className="flex gap-3 mt-6 pt-4 border-t border-slate-700">
                                    <button
                                        type="button"
                                        onClick={() => setShowModal(false)}
                                        className="flex-1 py-2.5 text-slate-400 hover:text-white font-medium"
                                    >
                                        Cancel
                                    </button>
                                    <button
                                        type="submit"
                                        className="flex-1 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-bold shadow-lg shadow-blue-900/20"
                                    >
                                        Create Workspace
                                    </button>
                                </div>
                            </form>
                        </div>
                    </div>
                )
            }

            {/* Edit Entitlements Modal */}
            {
                showEditModal && editingTenant && (
                    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 backdrop-blur-sm">
                        <div className="bg-slate-800 rounded-2xl w-full max-w-2xl border border-slate-700 shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
                            {/* Header */}
                            <div className="p-6 border-b border-slate-700 flex justify-between items-center bg-slate-900/50">
                                <div>
                                    <h2 className="text-xl font-bold text-white">Workspace Configuration</h2>
                                    <p className="text-slate-400 text-sm mt-1">Managing: <span className="text-blue-400">{editingTenant.name}</span></p>
                                </div>
                                <button onClick={() => setShowEditModal(false)} className="text-slate-400 hover:text-white">
                                    <LogOut size={20} className="rotate-180" /> {/* Using LogOut as Close/Exit icon variant */}
                                </button>
                            </div>

                            {/* Tabs */}
                            <div className="flex border-b border-slate-700">
                                {[
                                    { id: 'frameworks', label: 'Frameworks' },
                                    { id: 'features', label: 'Features & Scanners' },
                                    { id: 'status', label: 'Account Status' }
                                ].map(tab => (
                                    <button
                                        key={tab.id}
                                        onClick={() => setActiveTab(tab.id)}
                                        className={`flex-1 py-4 text-sm font-bold border-b-2 transition-colors ${activeTab === tab.id
                                            ? 'border-blue-500 text-blue-400 bg-slate-800'
                                            : 'border-transparent text-slate-500 hover:text-slate-300 hover:bg-slate-700/50'
                                            }`}
                                    >
                                        {tab.label}
                                    </button>
                                ))}
                            </div>

                            {/* Content */}
                            <div className="p-6 overflow-y-auto flex-1 bg-slate-800">
                                {!entitlements ? (
                                    <div className="text-center py-10 text-slate-500">Loading entitlements...</div>
                                ) : (
                                    <>
                                        {activeTab === 'frameworks' && (
                                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                                {entitlements.frameworks.map(fw => (
                                                    <div
                                                        key={fw.id}
                                                        onClick={() => toggleFramework(fw.id)}
                                                        className={`p-4 rounded-xl border cursor-pointer transition-all flex items-center justify-between ${fw.is_active
                                                            ? 'bg-blue-600/10 border-blue-500/50 hover:bg-blue-600/20'
                                                            : 'bg-slate-900 border-slate-700 hover:border-slate-500'
                                                            }`}
                                                    >
                                                        <div>
                                                            <h4 className={`font-bold ${fw.is_active ? 'text-white' : 'text-slate-400'}`}>{fw.name}</h4>
                                                            <p className="text-xs text-slate-500">{fw.code}</p>
                                                        </div>
                                                        <div className={`w-5 h-5 rounded-full border flex items-center justify-center ${fw.is_active ? 'bg-blue-500 border-blue-500' : 'border-slate-600'
                                                            }`}>
                                                            {fw.is_active && <div className="w-2 h-2 bg-white rounded-full" />}
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        )}

                                        {activeTab === 'features' && (
                                            <div className="space-y-4">
                                                {entitlements.features.map(feat => (
                                                    <div
                                                        key={feat.key}
                                                        onClick={() => toggleFeature(feat.key)}
                                                        className={`p-4 rounded-xl border cursor-pointer transition-all flex items-center gap-4 ${feat.is_active
                                                            ? 'bg-purple-600/10 border-purple-500/50'
                                                            : 'bg-slate-900 border-slate-700'
                                                            }`}
                                                    >
                                                        <div className={`p-2 rounded-lg ${feat.is_active ? 'bg-purple-500 text-white' : 'bg-slate-800 text-slate-500'}`}>
                                                            <Shield size={20} />
                                                        </div>
                                                        <div className="flex-1">
                                                            <h4 className={`font-bold ${feat.is_active ? 'text-white' : 'text-slate-400'}`}>
                                                                {feat.key.replace(/_/g, ' ').toUpperCase()}
                                                            </h4>
                                                            <p className="text-xs text-slate-500">Enable access to this module.</p>
                                                        </div>

                                                        <div className={`w-12 h-6 rounded-full p-1 transition-colors ${feat.is_active ? 'bg-purple-500' : 'bg-slate-700'
                                                            }`}>
                                                            <div className={`w-4 h-4 rounded-full bg-white transition-transform ${feat.is_active ? 'translate-x-6' : 'translate-x-0'
                                                                }`} />
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        )}

                                        {activeTab === 'status' && (
                                            <div className="bg-slate-900 p-6 rounded-xl border border-slate-700 text-center">
                                                <h3 className="text-lg font-bold text-white mb-2">Workspace Status</h3>
                                                <p className="text-slate-400 mb-6">Deactivating a workspace will prevent all users from logging in.</p>

                                                <div className="flex justify-center gap-4">
                                                    <button
                                                        onClick={() => setEntitlements({ ...entitlements, account_status: 'active' })}
                                                        className={`px-6 py-3 rounded-lg font-bold border ${entitlements.account_status === 'active'
                                                            ? 'bg-green-600 border-green-500 text-white'
                                                            : 'bg-slate-800 border-slate-700 text-slate-400 hover:text-white'
                                                            }`}
                                                    >
                                                        Active
                                                    </button>
                                                    <button
                                                        onClick={() => setEntitlements({ ...entitlements, account_status: 'deactivated' })}
                                                        className={`px-6 py-3 rounded-lg font-bold border ${entitlements.account_status === 'deactivated'
                                                            ? 'bg-red-600 border-red-500 text-white'
                                                            : 'bg-slate-800 border-slate-700 text-slate-400 hover:text-white'
                                                            }`}
                                                    >
                                                        Deactivated
                                                    </button>
                                                </div>
                                            </div>
                                        )}
                                    </>
                                )}
                            </div>

                            {/* Footer */}
                            <div className="p-6 border-t border-slate-700 bg-slate-900/50 flex justify-end gap-3">
                                <button
                                    onClick={() => setShowEditModal(false)}
                                    className="px-5 py-2.5 text-slate-400 hover:text-white font-medium"
                                    disabled={saving}
                                >
                                    Cancel
                                </button>
                                <button
                                    onClick={handleSaveEntitlements}
                                    disabled={saving || !entitlements}
                                    className={`px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-bold shadow-lg shadow-blue-900/20 flex items-center gap-2 ${saving ? 'opacity-70 cursor-wait' : ''}`}
                                >
                                    {saving ? 'Saving...' : 'Save Configuration'}
                                </button>
                            </div>
                        </div>
                    </div>
                )
            }
        </div>
    );
};

export default Workspaces;
