import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { ListChecks, Check, ArrowRight, Lock } from 'lucide-react';

const FrameworkSelector = ({ onComplete }) => {
    const [availableFrameworks, setAvailableFrameworks] = useState([]);
    const [selectedIds, setSelectedIds] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchCatalog();
    }, []);

    const fetchCatalog = async () => {
        try {
            // Fetch Global Catalog
            const res = await api.get('/frameworks?catalog=true');
            setAvailableFrameworks(res.data);
        } catch (err) {
            console.error("Failed to fetch framework catalog", err);
            setError("Failed to load framework options.");
        }
    };

    const toggleFramework = (id) => {
        setSelectedIds(prev => {
            if (prev.includes(id)) {
                return prev.filter(i => i !== id);
            } else {
                return [...prev, id];
            }
        });
    };

    const handleSubmit = async () => {
        if (selectedIds.length === 0) {
            alert("Please select at least one framework.");
            return;
        }

        setLoading(true);
        try {
            await api.post('/frameworks/tenant-link', {
                framework_ids: selectedIds
            });
            // Success - Trigger Check in Parent
            if (onComplete) onComplete();
        } catch (err) {
            console.error("Failed to link frameworks", err);
            setError(err.response?.data?.detail || "Failed to save selection.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-4xl mx-auto py-12 px-4 animate-fade-in">
            <div className="bg-white rounded-2xl shadow-xl border border-gray-200 overflow-hidden">
                <div className="p-8 border-b border-gray-100 bg-gradient-to-r from-blue-50 to-white">
                    <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-3">
                        <ListChecks className="w-8 h-8 text-blue-600" />
                        Configure Workspace
                    </h2>
                    <p className="text-gray-600 mt-2">
                        Your workspace is ready. Select the compliance frameworks you want to manage.
                    </p>
                </div>

                <div className="p-8">
                    {error && (
                        <div className="bg-red-50 text-red-600 p-4 rounded-lg mb-6 border border-red-100">
                            {error}
                        </div>
                    )}

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
                        {availableFrameworks.map(fw => {
                            const isSelected = selectedIds.includes(fw.id);
                            return (
                                <div
                                    key={fw.id}
                                    onClick={() => toggleFramework(fw.id)}
                                    className={`p-4 rounded-xl border-2 cursor-pointer transition-all flex items-start gap-4 ${isSelected ? 'border-blue-500 bg-blue-50/50' : 'border-gray-200 hover:border-blue-200 hover:bg-gray-50'}`}
                                >
                                    <div className={`w-6 h-6 rounded border flex items-center justify-center flex-shrink-0 mt-0.5 ${isSelected ? 'bg-blue-500 border-blue-500' : 'bg-white border-gray-300'}`}>
                                        {isSelected && <Check size={14} className="text-white" />}
                                    </div>
                                    <div>
                                        <div className="font-bold text-gray-900">{fw.name}</div>
                                        <div className="text-xs text-gray-500 font-mono mb-1">{fw.code}</div>
                                        <p className="text-sm text-gray-600 line-clamp-2">{fw.description}</p>
                                    </div>
                                </div>
                            );
                        })}
                        {availableFrameworks.length === 0 && !error && (
                            <div className="col-span-2 text-center py-12 text-gray-400 italic">
                                Loading available frameworks...
                            </div>
                        )}
                    </div>

                    <div className="bg-blue-50 p-4 rounded-lg flex items-start gap-3 mb-8">
                        <Lock className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
                        <div>
                            <h4 className="text-sm font-bold text-blue-900">One-Time Configuration</h4>
                            <p className="text-sm text-blue-700 mt-1">
                                Once configured, frameworks can only be modified by a Super Admin. Ensure your selection is correct.
                            </p>
                        </div>
                    </div>

                    <div className="flex justify-end pt-6 border-t border-gray-100">
                        <button
                            onClick={handleSubmit}
                            disabled={loading || selectedIds.length === 0}
                            className="bg-blue-600 hover:bg-blue-700 text-white rounded-xl px-8 py-3 font-bold flex items-center gap-2 shadow-lg shadow-blue-200 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                        >
                            {loading ? 'Setting up...' : 'Save & Enter Workspace'} <ArrowRight size={18} />
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default FrameworkSelector;
