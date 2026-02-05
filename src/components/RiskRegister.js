import React, { useState } from 'react';
import {
    AlertTriangle,
    ChevronDown,
    ChevronUp,
    Save,
    Plus
} from 'lucide-react';

const INITIAL_RISKS = [
    {
        id: 1,
        scenario: "Customer Data Breach via External Attack",
        category: "Security",
        likelihood: 3,
        impact: 5,
        treatment: "Mitigate: Implemented WAF, periodic pentests, and encryption at rest.",
        status: "Active"
    },
    {
        id: 2,
        scenario: "Insider Threat (Malicious Employee)",
        category: "Security",
        likelihood: 2,
        impact: 4,
        treatment: "Mitigate: Background checks, Principle of Least Privilege access controls.",
        status: "Active"
    },
    {
        id: 3,
        scenario: "Prolonged AWS Outage",
        category: "Availability",
        likelihood: 2,
        impact: 5,
        treatment: "Accept: Multi-region failover is too expensive for current stage.",
        status: "Accepted"
    },
    {
        id: 4,
        scenario: "Loss of Key Personnel (Bus Factor)",
        category: "Operational",
        likelihood: 4,
        impact: 3,
        treatment: "",
        status: "Draft"
    }
];

const IMPACT_LEVELS = [
    { val: 1, label: 'Negligible' },
    { val: 2, label: 'Minor' },
    { val: 3, label: 'Moderate' },
    { val: 4, label: 'Major' },
    { val: 5, label: 'Catastrophic' }
];

const LIKELIHOOD_LEVELS = [
    { val: 1, label: 'Rare' },
    { val: 2, label: 'Unlikely' },
    { val: 3, label: 'Possible' },
    { val: 4, label: 'Likely' },
    { val: 5, label: 'Almost Certain' }
];

const RiskRegister = () => {
    const [risks, setRisks] = useState(INITIAL_RISKS);
    const [editingId, setEditingId] = useState(null);
    const [editForm, setEditForm] = useState({});

    const startEdit = (risk) => {
        setEditingId(risk.id);
        setEditForm({ ...risk });
    };

    const saveEdit = () => {
        setRisks(risks.map(r => r.id === editingId ? editForm : r));
        setEditingId(null);
    };

    const cancelEdit = () => {
        setEditingId(null);
        setEditForm({});
    };

    const getScoreColor = (score) => {
        if (score >= 15) return 'bg-red-100 text-red-800 border-red-200'; // Critical
        if (score >= 10) return 'bg-orange-100 text-orange-800 border-orange-200'; // High
        if (score >= 5) return 'bg-yellow-100 text-yellow-800 border-yellow-200'; // Medium
        return 'bg-green-100 text-green-800 border-green-200'; // Low
    };

    return (
        <div className="space-y-6 h-full pb-20">
            {/* Header */}
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">Risk Register</h1>
                    <p className="text-sm text-gray-500">
                        Identify, assess, and treat organizational risks.
                        <strong> Automated</strong> templates provided; <strong>Manual</strong> scoring required.
                    </p>
                </div>
                <button className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 shadow-sm flex items-center gap-2">
                    <Plus className="w-5 h-5" />
                    Add Risk Scenario
                </button>
            </div>

            {/* Risk Table */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                <table className="w-full text-left">
                    <thead className="bg-gray-50 border-b border-gray-200">
                        <tr>
                            <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase w-1/3">Risk Scenario</th>
                            <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase text-center">Likelihood (1-5)</th>
                            <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase text-center">Impact (1-5)</th>
                            <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase text-center">Score</th>
                            <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase w-1/3">Treatment Plan</th>
                            <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase text-right">Actions</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                        {risks.map(risk => {
                            const isEditing = editingId === risk.id;
                            const currentScore = (isEditing ? editForm.likelihood : risk.likelihood) * (isEditing ? editForm.impact : risk.impact);

                            return (
                                <tr key={risk.id} className={`hover:bg-gray-50 transition-colors ${isEditing ? 'bg-blue-50/50' : ''}`}>
                                    <td className="px-6 py-4">
                                        <div className="flex items-start gap-3">
                                            <div className="mt-1">
                                                <AlertTriangle className={`w-5 h-5 ${risk.status === 'Accepted' ? 'text-gray-400' : 'text-red-500'}`} />
                                            </div>
                                            <div>
                                                <div className="font-medium text-gray-900 max-w-sm">{risk.scenario}</div>
                                                <div className="text-xs text-gray-500 mt-1">{risk.category}</div>
                                            </div>
                                        </div>
                                    </td>

                                    {/* Likelihood */}
                                    <td className="px-6 py-4 text-center">
                                        {isEditing ? (
                                            <select
                                                value={editForm.likelihood}
                                                onChange={(e) => setEditForm({ ...editForm, likelihood: parseInt(e.target.value) })}
                                                className="block w-full text-sm border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                                            >
                                                {LIKELIHOOD_LEVELS.map(l => (
                                                    <option key={l.val} value={l.val}>{l.val} - {l.label}</option>
                                                ))}
                                            </select>
                                        ) : (
                                            <span className="text-sm font-mono text-gray-600 font-bold">{risk.likelihood}</span>
                                        )}
                                    </td>

                                    {/* Impact */}
                                    <td className="px-6 py-4 text-center">
                                        {isEditing ? (
                                            <select
                                                value={editForm.impact}
                                                onChange={(e) => setEditForm({ ...editForm, impact: parseInt(e.target.value) })}
                                                className="block w-full text-sm border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                                            >
                                                {IMPACT_LEVELS.map(l => (
                                                    <option key={l.val} value={l.val}>{l.val} - {l.label}</option>
                                                ))}
                                            </select>
                                        ) : (
                                            <span className="text-sm font-mono text-gray-600 font-bold">{risk.impact}</span>
                                        )}
                                    </td>

                                    {/* Score */}
                                    <td className="px-6 py-4 text-center">
                                        <span className={`inline-flex items-center justify-center w-8 h-8 rounded-full text-sm font-bold border ${getScoreColor(currentScore)}`}>
                                            {currentScore}
                                        </span>
                                    </td>

                                    {/* Treatment Plan */}
                                    <td className="px-6 py-4">
                                        {isEditing ? (
                                            <textarea
                                                value={editForm.treatment}
                                                onChange={(e) => setEditForm({ ...editForm, treatment: e.target.value })}
                                                className="w-full text-sm border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                                                rows="2"
                                                placeholder="Explain how you will handle this risk..."
                                            />
                                        ) : (
                                            <div className="text-sm text-gray-600 italic">
                                                {risk.treatment || <span className="text-red-400">Missing treatment plan</span>}
                                            </div>
                                        )}
                                    </td>

                                    {/* Actions */}
                                    <td className="px-6 py-4 text-right">
                                        {isEditing ? (
                                            <div className="flex justify-end gap-2">
                                                <button onClick={saveEdit} className="text-green-600 hover:text-green-700 font-medium text-sm">Save</button>
                                                <button onClick={cancelEdit} className="text-gray-400 hover:text-gray-500 font-medium text-sm">Cancel</button>
                                            </div>
                                        ) : (
                                            <button
                                                onClick={() => startEdit(risk)}
                                                className="text-blue-600 hover:text-blue-700 font-medium text-sm"
                                            >
                                                Edit Score
                                            </button>
                                        )}
                                    </td>
                                </tr>
                            );
                        })}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default RiskRegister;
