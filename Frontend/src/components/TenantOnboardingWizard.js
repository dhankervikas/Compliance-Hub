import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { Shield, Check, ArrowRight, Building, Lock, FileText, Globe, ListChecks } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

const TenantOnboardingWizard = () => {
    const { user } = useAuth(); // Token handled by api interceptor
    const navigate = useNavigate();

    const [step, setStep] = useState(1);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [successData, setSuccessData] = useState(null); // { login_url, slug, ... }
    const [availableFrameworks, setAvailableFrameworks] = useState([]);

    const [formData, setFormData] = useState({
        // Screen 1: Identity
        name: '',
        slug: '',
        admin_email: '',
        admin_username: '',
        password: '',
        framework_ids: [],

        // Screen 2: Security
        encryption_tier: 'standard', // standard, advanced
        data_residency: 'us-east-1',

        // Screen 3: ISO 42001 Context
        aims_scope: '',
        security_leader_role: '',
        existing_policies: false
    });

    useEffect(() => {
        fetchFrameworks();
    }, []);

    const fetchFrameworks = async () => {
        try {
            const res = await api.get('/frameworks');
            setAvailableFrameworks(res.data);
        } catch (err) {
            console.error("Failed to fetch frameworks", err);
        }
    };

    const toggleFramework = (id) => {
        setFormData(prev => {
            const ids = prev.framework_ids.includes(id)
                ? prev.framework_ids.filter(i => i !== id)
                : [...prev.framework_ids, id];
            return { ...prev, framework_ids: ids };
        });
    };

    const isISO42001Selected = () => {
        const iso = availableFrameworks.find(f => f.code.includes('42001'));
        return iso && formData.framework_ids.includes(iso.id);
    };

    const totalSteps = isISO42001Selected() ? 4 : 3;

    const handleNext = () => setStep(step + 1);
    const handleBack = () => setStep(step - 1);

    const handleSubmit = async () => {
        setLoading(true);
        setError(null);
        try {
            // POST to Users/Tenants Endpoint
            // Map 'name' to 'org_name' to match backend schema
            const payload = {
                ...formData,
                org_name: formData.name
            };
            const res = await api.post('/users/tenants', payload);
            setSuccessData(res.data);
            setStep('success');
        } catch (err) {
            console.error(err);
            let msg = err.response?.data?.detail || "Failed to create tenant";
            if (typeof msg === 'object') {
                msg = JSON.stringify(msg);
            }
            setError(msg);
        } finally {
            setLoading(false);
        }
    };

    const handleCopyLink = () => {
        if (successData?.login_url) {
            navigator.clipboard.writeText(successData.login_url);
            alert("Magic Link Copied!");
        }
    };

    // --- STEP COMPONENTS ---

    const StepIndicator = () => (
        <div className="flex items-center justify-center mb-8 gap-4">
            {Array.from({ length: totalSteps }, (_, i) => i + 1).map(i => (
                <div key={i} className={`flex items-center gap-2 ${step >= i ? 'text-blue-500' : 'text-gray-400'}`}>
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold border-2 ${step >= i ? 'border-blue-500 bg-blue-50' : 'border-gray-200'}`}>
                        {step > i ? <Check size={16} /> : i}
                    </div>
                </div>
            ))}
        </div>
    );

    if (step === 'success' && successData) {
        return (
            <div className="min-h-screen bg-slate-900 flex flex-col items-center justify-center p-6 text-white font-sans">
                <div className="max-w-lg w-full bg-slate-800 border border-slate-700 p-8 rounded-2xl shadow-2xl text-center">
                    <div className="w-20 h-20 bg-green-500/10 rounded-full flex items-center justify-center mx-auto mb-6 text-green-500">
                        <Check size={40} />
                    </div>
                    <h2 className="text-3xl font-bold mb-2">Tenant Created!</h2>
                    <p className="text-slate-400 mb-8">
                        The workspace <b>{successData.name}</b> has been successfully provisioned with AES-256 encryption.
                    </p>

                    <div className="bg-slate-900 border border-slate-700 p-4 rounded-xl mb-6 text-left">
                        <label className="text-xs text-slate-500 font-bold uppercase block mb-2">Internal Tenant ID</label>
                        <div className="font-mono text-xs text-blue-400 break-all">{successData.internal_tenant_id}</div>
                    </div>

                    <div className="bg-slate-900 border border-slate-700 p-4 rounded-xl mb-8">
                        <label className="text-xs text-slate-500 font-bold uppercase block mb-2">Magic Login Link</label>
                        <div className="flex gap-2">
                            <input readOnly value={successData.login_url} className="flex-1 bg-transparent text-sm text-slate-300 outline-none font-mono" />
                            <button onClick={handleCopyLink} className="text-blue-500 hover:text-white font-bold text-sm">COPY</button>
                        </div>
                    </div>

                    <button
                        onClick={() => navigate('/super-admin')}
                        className="w-full py-3 bg-blue-600 hover:bg-blue-700 rounded-xl font-bold transition-colors"
                    >
                        Return to Dashboard
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-slate-900 flex flex-col items-center justify-center p-6 font-sans">
            <div className="max-w-2xl w-full">
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-white mb-2">New Workspace Setup</h1>
                    <p className="text-slate-400">Configure a new secure tenant environment.</p>
                </div>

                <StepIndicator />

                <div className="bg-slate-800 border border-slate-700 rounded-2xl p-8 shadow-xl">
                    {/* ERROR MSG */}
                    {error && (
                        <div className="bg-red-500/10 border border-red-500/50 text-red-500 p-4 rounded-lg mb-6">
                            {error}
                        </div>
                    )}

                    {/* STEPS */}
                    {step === 1 && (
                        <div className="space-y-4 animate-fade-in-up">
                            <h3 className="text-xl font-bold text-white flex items-center gap-2 mb-4">
                                <Building className="text-blue-500" /> Identity
                            </h3>
                            <div>
                                <label className="block text-sm font-medium text-slate-400 mb-1">Organization Name</label>
                                <input
                                    className="w-full bg-slate-900 border border-slate-700 rounded-lg p-3 text-white focus:ring-2 focus:ring-blue-500 outline-none"
                                    placeholder="Acme Corp"
                                    value={formData.name}
                                    onChange={e => setFormData({ ...formData, name: e.target.value })}
                                />
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-slate-400 mb-1">URL Slug</label>
                                    <div className="flex items-center bg-slate-900 border border-slate-700 rounded-lg overflow-hidden focus-within:ring-2 focus-within:ring-blue-500">
                                        <span className="pl-3 text-slate-500 text-sm">/t/</span>
                                        <input
                                            className="w-full bg-transparent p-3 text-white outline-none"
                                            placeholder="acme"
                                            value={formData.slug}
                                            onChange={e => setFormData({ ...formData, slug: e.target.value.toLowerCase().replace(/[^a-z0-9-]/g, '') })}
                                        />
                                    </div>
                                </div>
                                <div>
                                    <input
                                        className="w-full bg-slate-900 border border-slate-700 rounded-lg p-3 text-white focus:ring-2 focus:ring-blue-500 outline-none"
                                        placeholder="admin@acme.com"
                                        type="email"
                                        value={formData.admin_email}
                                        onChange={e => setFormData({ ...formData, admin_email: e.target.value })}
                                    />
                                </div>
                            </div>

                            {/* CREDENTIALS */}
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-slate-400 mb-1">Admin Username</label>
                                    <input
                                        className="w-full bg-slate-900 border border-slate-700 rounded-lg p-3 text-white focus:ring-2 focus:ring-blue-500 outline-none"
                                        placeholder="admin_acme"
                                        value={formData.admin_username}
                                        onChange={e => setFormData({ ...formData, admin_username: e.target.value })}
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-slate-400 mb-1">Password</label>
                                    <input
                                        className="w-full bg-slate-900 border border-slate-700 rounded-lg p-3 text-white focus:ring-2 focus:ring-blue-500 outline-none"
                                        type="password"
                                        placeholder="••••••••"
                                        value={formData.password}
                                        onChange={e => setFormData({ ...formData, password: e.target.value })}
                                    />
                                </div>
                            </div>
                        </div>
                    )}

                    {step === 2 && (
                        <div className="space-y-6 animate-fade-in-up">
                            <h3 className="text-xl font-bold text-white flex items-center gap-2 mb-4">
                                <Lock className="text-blue-500" /> Security Configuration
                            </h3>

                            {/* Encryption Selection */}
                            <div className="grid grid-cols-2 gap-4">
                                <button
                                    onClick={() => setFormData({ ...formData, encryption_tier: 'standard' })}
                                    className={`p-4 rounded-xl border text-left transition-all ${formData.encryption_tier === 'standard' ? 'bg-blue-600/10 border-blue-500 ring-1 ring-blue-500' : 'bg-slate-900 border-slate-700 hover:border-slate-500'}`}
                                >
                                    <div className="font-bold text-white mb-1">Standard Encryption</div>
                                    <div className="text-xs text-slate-400">AES-256 at rest (Managed Keys)</div>
                                </button>
                                <button
                                    onClick={() => setFormData({ ...formData, encryption_tier: 'advanced' })}
                                    className={`p-4 rounded-xl border text-left transition-all ${formData.encryption_tier === 'advanced' ? 'bg-purple-600/10 border-purple-500 ring-1 ring-purple-500' : 'bg-slate-900 border-slate-700 hover:border-slate-500'}`}
                                >
                                    <div className="font-bold text-white mb-1">Advanced (BYOK)</div>
                                    <div className="text-xs text-slate-400">Customer Managed Keys (Enterprise)</div>
                                </button>
                            </div>

                            {/* Data Residency */}
                            <div>
                                <label className="block text-sm font-medium text-slate-400 mb-2 flex items-center gap-2">
                                    <Globe size={16} /> Data Residency (Region)
                                </label>
                                <select
                                    className="w-full bg-slate-900 border border-slate-700 rounded-lg p-3 text-white focus:ring-2 focus:ring-blue-500 outline-none"
                                    value={formData.data_residency}
                                    onChange={e => setFormData({ ...formData, data_residency: e.target.value })}
                                >
                                    <option value="us-east-1">US East (N. Virginia)</option>
                                    <option value="eu-central-1">Europe (Frankfurt)</option>
                                    <option value="ap-southeast-1">Asia Pacific (Singapore)</option>
                                </select>
                            </div>
                        </div>
                    )}

                    {/* STEP 3: FRAMEWORKS (NEW) */}
                    {step === 3 && (
                        <div className="space-y-6 animate-fade-in-up">
                            <h3 className="text-xl font-bold text-white flex items-center gap-2 mb-4">
                                <ListChecks className="text-blue-500" /> Compliance Frameworks
                            </h3>
                            <p className="text-slate-400 text-sm mb-4">Select the standards this tenant will adhere to.</p>

                            <div className="space-y-3 max-h-60 overflow-y-auto">
                                {availableFrameworks.map(fw => {
                                    const isSelected = formData.framework_ids.includes(fw.id);
                                    return (
                                        <div
                                            key={fw.id}
                                            onClick={() => toggleFramework(fw.id)}
                                            className={`flex items-center justify-between p-4 rounded-xl border cursor-pointer transition-all ${isSelected ? 'bg-blue-600/10 border-blue-500/50' : 'bg-slate-900 border-slate-700 hover:bg-slate-800'}`}
                                        >
                                            <div className="flex items-center gap-3">
                                                <div className={`w-5 h-5 rounded flex items-center justify-center border ${isSelected ? 'bg-blue-500 border-blue-500' : 'bg-slate-800 border-slate-500'}`}>
                                                    {isSelected && <Check size={14} className="text-white" />}
                                                </div>
                                                <div>
                                                    <div className="font-bold text-white text-sm">{fw.name}</div>
                                                    <div className="text-xs text-slate-500">{fw.code}</div>
                                                </div>
                                            </div>
                                        </div>
                                    );
                                })}
                                {availableFrameworks.length === 0 && (
                                    <div className="text-center text-slate-500 py-8 italic">
                                        No frameworks found.
                                    </div>
                                )}
                            </div>

                            <div className="bg-slate-700/30 p-3 rounded-lg flex items-center gap-2 text-xs text-slate-400">
                                <Lock size={12} />
                                <span>Client self-service disabled (Default: Unlocked).</span>
                            </div>
                        </div>
                    )}

                    {/* STEP 4: CONTEXT */}
                    {step === 4 && (
                        <div className="space-y-4 animate-fade-in-up">
                            <h3 className="text-xl font-bold text-white flex items-center gap-2 mb-4">
                                <FileText className="text-blue-500" /> ISO 42001 Context
                            </h3>
                            <div className="bg-blue-900/20 border border-blue-500/30 p-4 rounded-lg mb-4 text-sm text-blue-200">
                                Rapidly configure the AIMS environment based on initial inputs.
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-slate-400 mb-1">AIMS Scope (Clause 4.1)</label>
                                <textarea
                                    className="w-full bg-slate-900 border border-slate-700 rounded-lg p-3 text-white focus:ring-2 focus:ring-blue-500 outline-none h-24"
                                    placeholder="Describe the boundaries of your Management System..."
                                    value={formData.aims_scope}
                                    onChange={e => setFormData({ ...formData, aims_scope: e.target.value })}
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-slate-400 mb-1">Security Leader Role (Clause 5.3)</label>
                                <input
                                    className="w-full bg-slate-900 border border-slate-700 rounded-lg p-3 text-white focus:ring-2 focus:ring-blue-500 outline-none"
                                    placeholder="e.g. CISO, Ethics Officer"
                                    value={formData.security_leader_role}
                                    onChange={e => setFormData({ ...formData, security_leader_role: e.target.value })}
                                />
                            </div>

                            <label className="flex items-center gap-3 p-3 bg-slate-900 border border-slate-700 rounded-lg cursor-pointer hover:bg-slate-800 transition-colors">
                                <input
                                    type="checkbox"
                                    className="w-5 h-5 rounded border-slate-600 text-blue-600 focus:ring-blue-500 bg-slate-800"
                                    checked={formData.existing_policies}
                                    onChange={e => setFormData({ ...formData, existing_policies: e.target.checked })}
                                />
                                <span className="text-slate-300 text-sm">We have existing security policies to import</span>
                            </label>
                        </div>
                    )}

                    {/* NAV ACTIONS */}
                    <div className="flex justify-between mt-8 pt-6 border-t border-slate-700">
                        {step === 1 ? (
                            <button
                                onClick={() => navigate('/super-admin')}
                                className="text-slate-400 hover:text-white font-medium px-4 py-2"
                            >
                                Cancel
                            </button>
                        ) : (
                            <button
                                onClick={handleBack}
                                className="text-slate-400 hover:text-white font-medium px-4 py-2"
                            >
                                Back
                            </button>
                        )}

                        {step < totalSteps ? (
                            <button
                                onClick={handleNext}
                                className="bg-blue-600 hover:bg-blue-700 text-white rounded-lg px-6 py-2 font-bold flex items-center gap-2 transition-colors"
                            >
                                Next Step <ArrowRight size={16} />
                            </button>
                        ) : (
                            <button
                                onClick={handleSubmit}
                                disabled={loading}
                                className="bg-green-600 hover:bg-green-700 text-white rounded-lg px-6 py-2 font-bold flex items-center gap-2 shadow-lg shadow-green-900/20 disabled:opacity-50"
                            >
                                {loading ? 'Provisioning...' : 'Complete & Generate Link'}
                            </button>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default TenantOnboardingWizard;
