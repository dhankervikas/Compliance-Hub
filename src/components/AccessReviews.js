import React, { useState } from 'react';
import {
    UserCheck,
    ShieldCheck,
    XCircle,
    CheckCircle,
    AlertOctagon,
    Search
} from 'lucide-react';

const MOCK_ACCESS_LIST = [
    { id: 1, user: "Alice Engineer", system: "AWS (Production)", role: "Admin", status: "Pending", lastLogin: "Today" },
    { id: 2, user: "Bob DevOps", system: "AWS (Production)", role: "Read-Only", status: "Pending", lastLogin: "Yesterday" },
    { id: 3, user: "Charlie Sales", system: "Salesforce", role: "User", status: "Pending", lastLogin: "2 days ago" },
    { id: 4, user: "Dave Intern", system: "GitHub", role: "Write", status: "Pending", lastLogin: "1 week ago" },
    { id: 5, user: "Eve Ex-Employee", system: "Slack", role: "Member", status: "Pending", lastLogin: "30 days ago", warning: "Terminated User" }
];

const AccessReviews = () => {
    const [reviews, setReviews] = useState(MOCK_ACCESS_LIST);
    const [justifyingId, setJustifyingId] = useState(null);
    const [justification, setJustification] = useState("");

    const handleDecision = (id, decision) => {
        if (decision === 'Keep' && !justifyingId) {
            // Require justification for Admin or Critical roles? For now just simple flow
            setReviews(reviews.map(r => r.id === id ? { ...r, status: 'Kept', decisionDate: new Date().toLocaleDateString() } : r));
        } else if (decision === 'Revoke') {
            setReviews(reviews.map(r => r.id === id ? { ...r, status: 'Revoked', decisionDate: new Date().toLocaleDateString() } : r));
        }
    };

    return (
        <div className="space-y-6 h-full pb-20">
            {/* Header */}
            <div>
                <h1 className="text-2xl font-bold text-gray-900">Access Reviews</h1>
                <p className="text-sm text-gray-500">
                    Quarterly review of user permissions.
                    <strong> Automated</strong> list generation; <strong>Manual</strong> approval required.
                </p>
            </div>

            {/* Stats */}
            <div className="flex gap-4">
                <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm flex-1">
                    <div className="text-gray-500 text-xs font-bold uppercase">Pending Reviews</div>
                    <div className="text-2xl font-bold text-blue-600">{reviews.filter(r => r.status === 'Pending').length}</div>
                </div>
                <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm flex-1">
                    <div className="text-gray-500 text-xs font-bold uppercase">Revoked Access</div>
                    <div className="text-2xl font-bold text-red-600">{reviews.filter(r => r.status === 'Revoked').length}</div>
                </div>
                <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm flex-1">
                    <div className="text-gray-500 text-xs font-bold uppercase">Verified Access</div>
                    <div className="text-2xl font-bold text-green-600">{reviews.filter(r => r.status === 'Kept').length}</div>
                </div>
            </div>

            {/* Review Table */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                <table className="w-full text-left">
                    <thead className="bg-gray-50 border-b border-gray-200">
                        <tr>
                            <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase">User / System</th>
                            <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase">Role</th>
                            <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase">Last Login</th>
                            <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase text-center">Decision</th>
                            <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase">Justification / Status</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                        {reviews.map(item => (
                            <tr key={item.id} className="hover:bg-gray-50">
                                <td className="px-6 py-4">
                                    <div className="flex items-center gap-3">
                                        <div className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center text-gray-600 font-bold text-xs">
                                            {item.user.charAt(0)}
                                        </div>
                                        <div>
                                            <div className="font-medium text-gray-900">{item.user}</div>
                                            <div className="text-xs text-gray-500">{item.system}</div>
                                            {item.warning && (
                                                <span className="inline-flex items-center gap-1 text-[10px] bg-red-100 text-red-700 px-1.5 py-0.5 rounded mt-1 font-bold">
                                                    <AlertOctagon className="w-3 h-3" /> {item.warning}
                                                </span>
                                            )}
                                        </div>
                                    </div>
                                </td>
                                <td className="px-6 py-4 text-sm text-gray-600">{item.role}</td>
                                <td className="px-6 py-4 text-sm text-gray-500">{item.lastLogin}</td>

                                <td className="px-6 py-4 text-center">
                                    {item.status === 'Pending' ? (
                                        <div className="flex justify-center gap-2">
                                            <button
                                                onClick={() => handleDecision(item.id, 'Keep')}
                                                className="px-3 py-1.5 bg-green-50 text-green-700 hover:bg-green-100 rounded-lg text-xs font-bold border border-green-200 transition-colors flex items-center gap-1"
                                            >
                                                <CheckCircle className="w-3 h-3" /> Keep
                                            </button>
                                            <button
                                                onClick={() => handleDecision(item.id, 'Revoke')}
                                                className="px-3 py-1.5 bg-red-50 text-red-700 hover:bg-red-100 rounded-lg text-xs font-bold border border-red-200 transition-colors flex items-center gap-1"
                                            >
                                                <XCircle className="w-3 h-3" /> Revoke
                                            </button>
                                            <button
                                                className="px-3 py-1.5 bg-gray-50 text-gray-700 hover:bg-gray-100 rounded-lg text-xs font-bold border border-gray-200 transition-colors"
                                            >
                                                Modify
                                            </button>
                                        </div>
                                    ) : (
                                        <div className="text-center">
                                            {item.status === 'Kept' ? (
                                                <span className="text-green-600 font-bold text-xs">Kept</span>
                                            ) : (
                                                <span className="text-red-500 font-bold text-xs">Revoked</span>
                                            )}
                                        </div>
                                    )}
                                </td>

                                <td className="px-6 py-4 text-sm text-gray-500">
                                    {item.status === 'Pending' ? (
                                        <span className="italic text-gray-400">Decision pending...</span>
                                    ) : (
                                        <span>Decision logged on {item.decisionDate}</span>
                                    )}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default AccessReviews;
