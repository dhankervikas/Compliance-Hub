import React, { useState, useEffect } from 'react';
import api from '../../services/api';

const AssessmentDrawer = ({ isOpen, onClose, context, onSave }) => {
    // context: { frameworkId, controlId, evidenceData, initialAssessment }
    const [status, setStatus] = useState('PENDING');
    const [remarks, setRemarks] = useState('');
    const [requestEvidence, setRequestEvidence] = useState(false);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (context?.initialAssessment) {
            setStatus(context.initialAssessment.status || 'PENDING');
            setRemarks(context.initialAssessment.remarks || '');
            setRequestEvidence(context.initialAssessment.evidence_request_flag || false);
        } else {
            // Reset if no prior assessment
            setStatus('PENDING');
            setRemarks('');
            setRequestEvidence(false);
        }
    }, [context]);

    const handleSave = async () => {
        if (!context) return;
        setLoading(true);
        try {
            const payload = {
                framework_id: context.frameworkId,
                control_id: context.controlId,
                status: status,
                remarks: remarks,
                evidence_request_flag: requestEvidence
            };

            await api.post('/auditor/assessments', payload);
            if (onSave) onSave(); // Refresh parent view
            onClose();
        } catch (error) {
            console.error("Failed to save assessment", error);
            alert("Error saving assessment.");
        } finally {
            setLoading(false);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 overflow-hidden">
            <div className="absolute inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={onClose} />
            <div className="fixed inset-y-0 right-0 max-w-md w-full flex">
                <div className="h-full flex flex-col bg-white shadow-xl overflow-y-scroll">
                    <div className="px-4 py-6 bg-slate-800 sm:px-6">
                        <div className="flex items-center justify-between">
                            <h2 className="text-lg font-medium text-white">Auditor Assessment</h2>
                            <button onClick={onClose} className="text-slate-400 hover:text-white">
                                <span className="sr-only">Close panel</span>
                                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                                </svg>
                            </button>
                        </div>
                        <p className="mt-1 text-sm text-slate-300">
                            Control: {context?.controlId}
                        </p>
                    </div>

                    <div className="relative flex-1 px-4 py-6 sm:px-6">
                        {/* Evidence Section (Read Only) */}
                        <div className="mb-6">
                            <h3 className="text-sm font-medium text-gray-900 border-b pb-2 mb-2">Evidence for Review</h3>
                            {context?.evidenceData ? (
                                <div className="bg-gray-50 p-3 rounded text-sm space-y-2">
                                    <div className="flex justify-between">
                                        <span className="text-gray-500">Resource:</span>
                                        <span className="font-medium text-gray-900">{context.evidenceData.resource_name || 'N/A'}</span>
                                    </div>
                                    <div className="flex justify-between">
                                        <span className="text-gray-500">Submitted:</span>
                                        <span className="font-medium text-gray-900">{context.evidenceData.submitted_at || 'N/A'}</span>
                                    </div>
                                    <div className="mt-2">
                                        <button className="text-blue-600 hover:text-blue-800 text-xs font-semibold uppercase tracking-wide bg-transparent border-0 p-0 underline cursor-pointer">
                                            View Document &rarr;
                                        </button>
                                    </div>
                                </div>
                            ) : (
                                <p className="text-sm text-gray-500 italic">No evidence linked to this control yet.</p>
                            )}
                        </div>

                        {/* Assessment Form */}
                        <div className="space-y-4">
                            <label className="block text-sm font-medium text-gray-700 mb-2">Compliance Rating</label>
                            <div className="grid grid-cols-2 gap-2">
                                <button
                                    onClick={() => setStatus('COMPLIANT')}
                                    className={`px-3 py-2 text-xs font-bold rounded border ${status === 'COMPLIANT' ? 'bg-green-100 text-green-700 border-green-300 ring-2 ring-green-500 ring-offset-1' : 'bg-white text-gray-600 border-gray-300 hover:bg-gray-50'}`}
                                >
                                    VERIFIED / CONFORMS
                                </button>
                                <button
                                    onClick={() => setStatus('OBSERVATION')}
                                    className={`px-3 py-2 text-xs font-bold rounded border ${status === 'OBSERVATION' ? 'bg-amber-100 text-amber-700 border-amber-300 ring-2 ring-amber-500 ring-offset-1' : 'bg-white text-gray-600 border-gray-300 hover:bg-gray-50'}`}
                                >
                                    OBSERVATION
                                </button>
                                <button
                                    onClick={() => setStatus('MINOR_NC')}
                                    className={`px-3 py-2 text-xs font-bold rounded border ${status === 'MINOR_NC' ? 'bg-red-50 text-red-600 border-red-200 ring-2 ring-red-400 ring-offset-1' : 'bg-white text-gray-600 border-gray-300 hover:bg-gray-50'}`}
                                >
                                    MINOR NC
                                </button>
                                <button
                                    onClick={() => setStatus('MAJOR_NC')}
                                    className={`px-3 py-2 text-xs font-bold rounded border ${status === 'MAJOR_NC' ? 'bg-red-100 text-red-800 border-red-300 ring-2 ring-red-600 ring-offset-1' : 'bg-white text-gray-600 border-gray-300 hover:bg-gray-50'}`}
                                >
                                    MAJOR NC
                                </button>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700">Auditor Remarks</label>
                                <textarea
                                    rows={4}
                                    value={remarks}
                                    onChange={(e) => setRemarks(e.target.value)}
                                    className="mt-1 block w-full shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm border-gray-300 rounded-md"
                                    placeholder="Enter findings, observations, or required actions..."
                                />
                            </div>

                            <div className="flex items-start">
                                <div className="flex items-center h-5">
                                    <input
                                        id="request_evidence"
                                        type="checkbox"
                                        checked={requestEvidence}
                                        onChange={(e) => setRequestEvidence(e.target.checked)}
                                        className="focus:ring-blue-500 h-4 w-4 text-blue-600 border-gray-300 rounded"
                                    />
                                </div>
                                <div className="ml-3 text-sm">
                                    <label htmlFor="request_evidence" className="font-medium text-gray-700">Request More Information</label>
                                    <p className="text-gray-500">Flags this item in the User Portal as "Requires Attention".</p>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="flex-shrink-0 px-4 py-4 bg-gray-50 border-t border-gray-200 flex justify-end">
                        <button
                            type="button"
                            onClick={onClose}
                            className="bg-white py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                        >
                            Cancel
                        </button>
                        <button
                            type="button"
                            onClick={handleSave}
                            disabled={loading}
                            className="ml-4 inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                        >
                            {loading ? 'Saving...' : 'Submit Assessment'}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AssessmentDrawer;
