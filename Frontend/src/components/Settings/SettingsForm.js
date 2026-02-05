import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import axios from '../../services/api';
import { Save, AlertCircle, CheckCircle, Layers } from 'lucide-react';
import FrameworkSetupWizard from '../Wizards/FrameworkSetupWizard';

const SettingsForm = () => {
    const { section } = useParams();
    const [data, setData] = useState({});
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [message, setMessage] = useState(null); // { type: 'success' | 'error', text: '' }
    const [showWizard, setShowWizard] = useState(false);

    // Hardcoded Schema Definitions for UI Rendering (simplified version of Pydantic)
    // In a real app, we might fetch this from an OPTIONS endpoint.
    const schemas = {
        org_profile: [
            { name: 'legal_name', label: 'Legal Entity Name', type: 'text', required: true },
            { name: 'dba', label: 'Doing Business As (DBA)', type: 'text' },
            { name: 'address', label: 'Headquarters Address', type: 'textarea' },
            { name: 'industry', label: 'Industry', type: 'text' },
            { name: 'headcount', label: 'Headcount', type: 'select', options: ['<10', '10-50', '50-200', '200+'] },
            { name: 'support_model', label: 'Support Model', type: 'select', options: ['Business Hours', '24x7'] }
        ],
        scope: [
            { name: 'scope_statement', label: 'ISMS Scope Statement', type: 'textarea', required: true, help: 'Describe exactly what is covered by the certification.' },
            { name: 'locations', label: 'Locations in Scope (comma separated)', type: 'text' },
            { name: 'frameworks', label: 'Applicable Frameworks', type: 'multi-select', options: ['ISO 27001', 'SOC 2', 'HIPAA', 'GDPR'] }
        ],
        tech_stack: [
            { name: 'hosting_model', label: 'Hosting Model', type: 'select', options: ['Cloud-Native', 'Hybrid', 'On-Prem'] },
            { name: 'cloud_providers', label: 'Cloud Providers', type: 'multi-select', options: ['AWS', 'Azure', 'GCP', 'DigitalOcean', 'Heroku', 'Vercel'] },
            { name: 'idp_tool', label: 'Identity Provider (IdP)', type: 'text', placeholder: 'e.g. Okta, Google Workspace' },
            { name: 'ticketing_tool', label: 'Ticketing System', type: 'text', placeholder: 'e.g. Jira' },
            { name: 'code_repos', label: 'Code Repositories', type: 'text', placeholder: 'e.g. GitHub, GitLab' }
        ],
        // ... We can add others or handle generic fallback
    };

    const currentSchema = schemas[section] || [];

    const fetchData = React.useCallback(async () => {
        setLoading(true);
        setMessage(null);
        try {
            const res = await axios.get(`/settings/${section}`);
            setData(res.data.content || {});
        } catch (err) {
            console.error("Failed to fetch settings", err);
            const msg = err.response?.data?.detail || err.message || "Unknown error";
            setMessage({ type: 'error', text: `Failed to load settings: ${msg}` });
        } finally {
            setLoading(false);
        }
    }, [section]);

    useEffect(() => {
        fetchData();
    }, [fetchData]);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setData(prev => ({ ...prev, [name]: value }));
    };

    // Handle array inputs (comma separated for now for simplicity)
    const handleArrayChange = (e) => {
        const { name, value } = e.target;
        setData(prev => ({ ...prev, [name]: value.split(',').map(s => s.trim()) }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setSaving(true);
        setMessage(null);

        // Clean data: remove empty strings for Select/Literal fields to avoid Pydantic validation errors
        // Recursive function not needed since our structure is flat-ish, but let's be safe for simple fields
        const cleanData = Object.entries(data).reduce((acc, [key, value]) => {
            if (value === "" || value === null || value === undefined) {
                return acc; // Skip empty values, let Pydantic use defaults
            }
            if (Array.isArray(value) && value.length === 1 && value[0] === "") {
                return acc; // Skip empty arrays (from split)
            }
            acc[key] = value;
            return acc;
        }, {});

        try {
            console.log("Submitting payload:", { section, content: cleanData }); // Debug
            await axios.put(`/settings/${section}`, {
                section: section,
                content: cleanData
            });
            setMessage({ type: 'success', text: 'Settings saved successfully.' });

            // Re-fetch to ensure sync (optional but good practice)
            await fetchData();

        } catch (err) {
            console.error("Failed to save settings", err);
            const errorMsg = err.response?.data?.detail
                ? (typeof err.response.data.detail === 'object' ? JSON.stringify(err.response.data.detail) : err.response.data.detail)
                : 'Failed to save.';
            setMessage({ type: 'error', text: errorMsg });
        } finally {
            setSaving(false);
        }
    };

    if (loading && !data) return <div className="p-8">Loading settings...</div>; // Allow loading state update without unmounting if data exists

    return (
        <div className="bg-white shadow rounded-lg p-6">
            {showWizard && (
                <FrameworkSetupWizard
                    onComplete={() => {
                        setShowWizard(false);
                        fetchData(); // Refresh data from backend to avoid stale overwrite
                    }}
                    onCancel={() => setShowWizard(false)}
                />
            )}
            <h1 className="text-xl font-bold text-gray-900 mb-6 capitalize">{section === 'scope' ? 'Framework Scope' : section.replace('_', ' ')}</h1>

            {/* SOC 2 WIZARD TRIGGER FOR SCOPE SECTION */}
            {section === 'scope' && (
                <div className="mb-8 bg-orange-50 border border-orange-200 rounded-xl p-6 flex flex-col md:flex-row items-center justify-between gap-4">
                    <div className="flex items-start gap-4">
                        <div className="p-3 bg-white rounded-lg border border-orange-100 shadow-sm">
                            <Layers className="w-6 h-6 text-orange-600" />
                        </div>
                        <div>
                            <h3 className="text-lg font-bold text-gray-900">SOC 2 Type II Configuration</h3>
                            <p className="text-sm text-gray-600 mb-2">
                                Configure your Trust Services Criteria (TSC) scope.
                            </p>
                            <div className="flex flex-wrap gap-2">
                                {data.soc2_selected_principles && data.soc2_selected_principles.length > 0 ? (
                                    data.soc2_selected_principles.map(p => (
                                        <span key={p} className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
                                            {p}
                                        </span>
                                    ))
                                ) : (
                                    <span className="text-xs text-gray-400 italic">No principles selected (Security is mandatory)</span>
                                )}
                            </div>
                        </div>
                    </div>
                    <button
                        type="button"
                        onClick={() => setShowWizard(true)}
                        className="whitespace-nowrap px-4 py-2 bg-orange-600 hover:bg-orange-700 text-white font-bold rounded-lg shadow-sm transition-colors"
                    >
                        Configure SOC 2 Scope
                    </button>
                </div>
            )}

            {message && (
                <div className={`mb-4 p-4 rounded flex items-center gap-2 ${message.type === 'success' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`}>
                    {message.type === 'success' ? <CheckCircle size={18} /> : <AlertCircle size={18} />}
                    {message.text}
                </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-6">
                {currentSchema.length > 0 ? (
                    currentSchema.map((field) => (
                        <div key={field.name}>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                {field.label} {field.required && <span className="text-red-500">*</span>}
                            </label>
                            {field.type === 'textarea' ? (
                                <textarea
                                    name={field.name}
                                    value={data[field.name] || ''}
                                    onChange={handleChange}
                                    className="w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                                    rows={4}
                                />
                            ) : field.type === 'select' ? (
                                <select
                                    name={field.name}
                                    value={data[field.name] || ''}
                                    onChange={handleChange}
                                    className="w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                                >
                                    <option value="">Select...</option>
                                    {field.options.map(opt => (
                                        <option key={opt} value={opt}>{opt}</option>
                                    ))}
                                </select>
                            ) : (
                                <input
                                    type={field.type === 'text' ? 'text' : 'text'}
                                    name={field.name}
                                    value={Array.isArray(data[field.name]) ? data[field.name].join(', ') : (data[field.name] || '')}
                                    onChange={Array.isArray(data[field.name]) || field.name === 'locations' ? handleArrayChange : handleChange}
                                    className="w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                                    placeholder={field.placeholder}
                                />
                            )}
                            {field.help && <p className="mt-1 text-xs text-gray-500">{field.help}</p>}
                        </div>
                    ))
                ) : (
                    <div className="text-gray-500 italic">
                        Generic JSON Editor for {section} (Schema not defined in UI yet)
                        <textarea
                            value={JSON.stringify(data, null, 2)}
                            onChange={(e) => {
                                try {
                                    setData(JSON.parse(e.target.value));
                                } catch { }
                            }}
                            className="w-full mt-2 font-mono text-sm border-gray-300 rounded-md"
                            rows={10}
                        />
                    </div>
                )}

                <div className="pt-4 flex justify-end">
                    <button
                        type="submit"
                        disabled={saving}
                        className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
                    >
                        <Save size={18} />
                        {saving ? 'Saving...' : 'Save Changes'}
                    </button>
                </div>
            </form>
        </div>
    );
};

export default SettingsForm;
