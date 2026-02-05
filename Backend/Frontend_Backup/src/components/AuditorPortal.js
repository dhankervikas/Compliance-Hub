import React, { useState } from 'react';
import { Shield, Globe } from 'lucide-react';

const AuditorPortal = () => {
    // Determine which step of the wizard to show. 
    // Screenshot shows Step 1: Select Audit Type
    const [step, setStep] = useState(1);
    const [auditType, setAuditType] = useState(null);

    const handleSelectType = (type) => {
        setAuditType(type);
        setStep(2); // Move to next step (mock interaction)
    };

    return (
        <div className="min-h-screen bg-gray-50 flex flex-col items-center pt-24">

            {/* Header / Title Section from Screenshot */}
            <div className="w-full max-w-4xl bg-[#1E3A8A] text-white rounded-t-xl overflow-hidden shadow-lg">
                <div className="p-8">
                    <div className="flex items-center gap-3 mb-2">
                        <Shield className="w-6 h-6 text-white" />
                        <h1 className="text-2xl font-bold">Audit Initiation</h1>
                    </div>
                    <p className="text-blue-200 text-sm">Step {step} of 3: Select Audit Type</p>
                </div>

                {/* Progress Bar Mock */}
                <div className="w-full bg-blue-900 h-1.5">
                    <div className="w-1/3 bg-blue-400 h-1.5"></div>
                </div>
            </div>

            {/* Content Area */}
            <div className="w-full max-w-4xl bg-white rounded-b-xl shadow-lg p-12 border border-gray-200 border-t-0">

                {step === 1 && (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                        {/* Internal Audit Card */}
                        <button
                            onClick={() => handleSelectType('internal')}
                            className="text-left p-8 rounded-xl border border-gray-200 hover:border-blue-500 hover:ring-1 hover:ring-blue-500 transition group"
                        >
                            <div className="w-12 h-12 bg-blue-50 text-blue-600 rounded-lg flex items-center justify-center mb-6 group-hover:bg-blue-600 group-hover:text-white transition">
                                <Shield className="w-6 h-6" />
                            </div>
                            <h3 className="text-lg font-bold text-gray-900 mb-2">Internal Audit</h3>
                            <p className="text-gray-500 text-sm leading-relaxed">
                                Gap analysis, readiness checks, and internal improvement cycles.
                            </p>
                        </button>

                        {/* External Certification Card */}
                        <button
                            onClick={() => handleSelectType('external')}
                            className="text-left p-8 rounded-xl border border-gray-200 hover:border-purple-500 hover:ring-1 hover:ring-purple-500 transition group"
                        >
                            <div className="w-12 h-12 bg-purple-50 text-purple-600 rounded-lg flex items-center justify-center mb-6 group-hover:bg-purple-600 group-hover:text-white transition">
                                <Globe className="w-6 h-6" />
                            </div>
                            <h3 className="text-lg font-bold text-gray-900 mb-2">External Certification</h3>
                            <p className="text-gray-500 text-sm leading-relaxed">
                                Formal ISO 27001 / SOC 2 certification audit with a 3rd party.
                            </p>
                        </button>
                    </div>
                )}

                {step === 2 && (
                    <div className="text-center py-12">
                        <div className="w-16 h-16 bg-green-100 text-green-600 rounded-full flex items-center justify-center mx-auto mb-4">
                            <Shield className="w-8 h-8" />
                        </div>
                        <h3 className="text-xl font-bold text-gray-900 mb-2">Audit Initialized</h3>
                        <p className="text-gray-500 mb-6">You selected {auditType === 'internal' ? 'Internal Audit' : 'External Certification'}.</p>
                        <button
                            onClick={() => setStep(1)}
                            className="px-6 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 font-medium"
                        >
                            Back to Start
                        </button>
                    </div>
                )}

            </div>

        </div>
    );
};

export default AuditorPortal;
