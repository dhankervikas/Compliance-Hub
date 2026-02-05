
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, FileText, CheckCircle, ArrowRight, User, Globe, AlertTriangle } from 'lucide-react';
import { auditService } from '../../services/auditService';

const InitiationWizard = () => {
    const navigate = useNavigate();
    const [step, setStep] = useState(1);
    const [formData, setFormData] = useState({
        type: '',
        audit_period: '',
        risk_area: '',
        auditor_name: '',
        certification_body: '',
        stage: '',
        ack_scope: false
    });
    const [loading, setLoading] = useState(false);

    const handleSelectType = (type) => {
        setFormData({ ...formData, type });
        setStep(2);
    };

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData({
            ...formData,
            [name]: type === 'checkbox' ? checked : value
        });
    };

    const handleSubmit = async () => {
        setLoading(true);
        try {
            await auditService.initiateAudit(formData);
            // Redirect to the main Dashboard view
            navigate('/auditor-portal/dashboard');
        } catch (err) {
            alert("Failed to initiate audit: " + err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-50 flex flex-col justify-center items-center p-6">
            <div className="max-w-2xl w-full bg-white rounded-xl shadow-lg overflow-hidden">
                {/* Header */}
                <div className="bg-blue-900 px-8 py-6 text-white">
                    <h1 className="text-2xl font-bold flex items-center gap-2">
                        <Shield className="w-6 h-6" />
                        Audit Initiation
                    </h1>
                    <p className="text-blue-200 mt-2">Step {step} of 3: {step === 1 ? 'Select Audit Type' : step === 2 ? 'Audit Details' : 'Scope Confirmation'}</p>
                </div>

                {/* Progress Bar */}
                <div className="w-full bg-gray-200 h-1">
                    <div className="bg-blue-500 h-1 transition-all duration-300" style={{ width: `${(step / 3) * 100}%` }}></div>
                </div>

                <div className="p-8">
                    {/* STEP 1: TYPE SELECTION */}
                    {step === 1 && (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <button
                                onClick={() => handleSelectType('INTERNAL')}
                                className="p-6 border-2 border-gray-100 rounded-xl hover:border-blue-500 hover:bg-blue-50 transition-all text-left group"
                            >
                                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4 text-blue-600 group-hover:bg-blue-600 group-hover:text-white transition-colors">
                                    <FileText className="w-6 h-6" />
                                </div>
                                <h3 className="font-bold text-lg text-gray-900">Internal Audit</h3>
                                <p className="text-sm text-gray-500 mt-2">Gap analysis, readiness checks, and internal improvement cycles.</p>
                            </button>

                            <button
                                onClick={() => handleSelectType('EXTERNAL')}
                                className="p-6 border-2 border-gray-100 rounded-xl hover:border-purple-500 hover:bg-purple-50 transition-all text-left group"
                            >
                                <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4 text-purple-600 group-hover:bg-purple-600 group-hover:text-white transition-colors">
                                    <Globe className="w-6 h-6" />
                                </div>
                                <h3 className="font-bold text-lg text-gray-900">External Certification</h3>
                                <p className="text-sm text-gray-500 mt-2">Formal ISO 27001 / SOC 2 certification audit with a 3rd party.</p>
                            </button>
                        </div>
                    )}

                    {/* STEP 2: DYNAMIC DETAILS */}
                    {step === 2 && (
                        <div className="space-y-6 animate-fade-in">
                            <h2 className="text-xl font-bold text-gray-800">
                                {formData.type === 'INTERNAL' ? 'Internal Audit Parameters' : 'External Certification Details'}
                            </h2>

                            {formData.type === 'INTERNAL' ? (
                                <>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">Internal Auditor Name</label>
                                        <div className="relative">
                                            <User className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
                                            <input
                                                name="auditor_name"
                                                value={formData.auditor_name}
                                                onChange={handleChange}
                                                className="pl-10 w-full rounded-lg border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 py-2.5 bg-gray-50 border"
                                                placeholder="e.g. Jane Doe"
                                            />
                                        </div>
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">Audit Period</label>
                                        <input
                                            name="audit_period"
                                            value={formData.audit_period}
                                            onChange={handleChange}
                                            className="w-full rounded-lg border-gray-300 shadow-sm py-2.5 px-3 bg-gray-50 border"
                                            placeholder="e.g. Q1 2026"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">Risk Priority Area</label>
                                        <select
                                            name="risk_area"
                                            value={formData.risk_area}
                                            onChange={handleChange}
                                            className="w-full rounded-lg border-gray-300 shadow-sm py-2.5 px-3 bg-gray-50 border"
                                        >
                                            <option value="">Select Priority...</option>
                                            <option value="ORGANIZATIONAL">Organizational Controls (A.5)</option>
                                            <option value="PEOPLE">People Controls (A.6)</option>
                                            <option value="PHYSICAL">Physical Controls (A.7)</option>
                                            <option value="TECHNOLOGICAL">Technological Controls (A.8)</option>
                                            <option value="FULL_SCOPE">Full Scope</option>
                                        </select>
                                    </div>
                                </>
                            ) : (
                                <>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">Certification Body</label>
                                        <select
                                            name="certification_body"
                                            value={formData.certification_body}
                                            onChange={handleChange}
                                            className="w-full rounded-lg border-gray-300 shadow-sm py-2.5 px-3 bg-gray-50 border"
                                        >
                                            <option value="">Select Body...</option>
                                            <option value="BSI">BSI Group</option>
                                            <option value="TUV">TÜV SÜD</option>
                                            <option value="DNV">DNV GL</option>
                                            <option value="OTHER">Other</option>
                                        </select>
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">Audit Stage</label>
                                        <select
                                            name="stage"
                                            value={formData.stage}
                                            onChange={handleChange}
                                            className="w-full rounded-lg border-gray-300 shadow-sm py-2.5 px-3 bg-gray-50 border"
                                        >
                                            <option value="">Select Stage...</option>
                                            <option value="STAGE_1">Stage 1 (Documentation Review)</option>
                                            <option value="STAGE_2">Stage 2 (Implementation Audit)</option>
                                            <option value="SURVEILLANCE">Surveillance Audit</option>
                                        </select>
                                    </div>
                                </>
                            )}

                            <div className="flex justify-between pt-4">
                                <button onClick={() => setStep(1)} className="text-gray-500 hover:text-gray-700 font-medium">Back</button>
                                <button
                                    onClick={() => setStep(3)}
                                    className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition flex items-center gap-2"
                                >
                                    Continue <ArrowRight className="w-4 h-4" />
                                </button>
                            </div>
                        </div>
                    )}

                    {/* STEP 3: SCOPE CONFIRMATION */}
                    {step === 3 && (
                        <div className="space-y-6 animate-fade-in">
                            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 flex gap-3">
                                <AlertTriangle className="w-6 h-6 text-yellow-600 flex-shrink-0" />
                                <div>
                                    <h4 className="font-bold text-yellow-800">Scope Verification Required</h4>
                                    <p className="text-sm text-yellow-700 mt-1">Please confirm the scope defined by the client before proceeding. Any deviations must be flagged.</p>
                                </div>
                            </div>

                            <div className="bg-gray-50 p-6 rounded-lg border border-gray-200">
                                <h3 className="font-bold text-gray-900 mb-4">Defined Scope (ISMS-01)</h3>
                                <ul className="space-y-2 text-sm text-gray-700">
                                    <li className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-green-500" /> Production AWS Environment (us-east-1)</li>
                                    <li className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-green-500" /> Corporate GitHub Repositories</li>
                                    <li className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-green-500" /> NY & London Office Locations</li>
                                    <li className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-green-500" /> All Full-time Employees & Contractors</li>
                                </ul>
                            </div>

                            <label className="flex items-center gap-3 p-4 border rounded-lg hover:bg-gray-50 cursor-pointer">
                                <input
                                    type="checkbox"
                                    name="ack_scope"
                                    checked={formData.ack_scope}
                                    onChange={handleChange}
                                    className="w-5 h-5 text-blue-600 rounded focus:ring-blue-500"
                                />
                                <span className="font-medium text-gray-900">I confirm the audit will be conducted within these boundaries.</span>
                            </label>

                            <div className="flex justify-between pt-4">
                                <button onClick={() => setStep(2)} className="text-gray-500 hover:text-gray-700 font-medium">Back</button>
                                <button
                                    onClick={handleSubmit}
                                    disabled={!formData.ack_scope || loading}
                                    className={`bg-green-600 text-white px-8 py-3 rounded-lg hover:bg-green-700 transition flex items-center gap-2 shadow-lg ${(!formData.ack_scope || loading) ? 'opacity-50 cursor-not-allowed' : ''}`}
                                >
                                    {loading ? 'Initiating...' : 'Start Audit Interface'} <ArrowRight className="w-5 h-5" />
                                </button>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default InitiationWizard;
