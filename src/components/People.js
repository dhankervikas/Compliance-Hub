import React, { useState } from 'react';
import {
    Users,
    UserMinus,
    CheckCircle,
    XCircle,
    AlertTriangle,
    Search,
    Filter,
    MoreVertical
} from 'lucide-react';

// Mock Data for Demo
const MOCK_PEOPLE = [
    { id: 1, name: "Alice Engineer", role: "Software Engineer", email: "alice@company.com", status: "Active", bgCheck: true, training: true, policy: true, accounts: ["AWS", "GitHub", "Slack"] },
    { id: 2, name: "Bob DevOps", role: "DevOps Engineer", email: "bob@company.com", status: "Active", bgCheck: true, training: false, policy: true, accounts: ["AWS", "GitHub"] },
    { id: 3, name: "Charlie Sales", role: "Account Executive", email: "charlie@company.com", status: "Active", bgCheck: true, training: true, policy: false, accounts: ["Salesforce", "Slack"] },
    { id: 4, name: "Dave Intern", role: "Engineering Intern", email: "dave@company.com", status: "Active", bgCheck: false, training: false, policy: false, accounts: ["GitHub", "Slack"] },
    { id: 5, name: "Eve Ex-Employee", role: "Former PM", email: "eve@company.com", status: "Terminated", bgCheck: true, training: true, policy: true, accounts: ["GitHub", "Slack"], terminatedAt: "2024-01-15" },
];

const People = () => {
    const [people, setPeople] = useState(MOCK_PEOPLE);
    const [activeTab, setActiveTab] = useState('active'); // active, offboarding
    const [searchTerm, setSearchTerm] = useState('');

    const filteredPeople = people.filter(p => {
        const matchesSearch = p.name.toLowerCase().includes(searchTerm.toLowerCase()) || p.email.toLowerCase().includes(searchTerm.toLowerCase());
        if (activeTab === 'active') return matchesSearch && p.status === 'Active';
        if (activeTab === 'offboarding') return matchesSearch && p.status === 'Terminated';
        return false;
    });

    const offboardingAlerts = people.filter(p => p.status === 'Terminated' && p.accounts.length > 0).length;

    return (
        <div className="space-y-6 h-full flex flex-col">
            {/* Header */}
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">People & Access</h1>
                    <p className="text-sm text-gray-500">Manage personnel security, onboarding, and offboarding.</p>
                </div>
                <div className="flex gap-2">
                    <button className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 bg-white">
                        Sync from Okta
                    </button>
                    <button className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 shadow-sm">
                        Add Person
                    </button>
                </div>
            </div>

            {/* Tabs */}
            <div className="border-b border-gray-200">
                <nav className="-mb-px flex gap-8">
                    <button
                        onClick={() => setActiveTab('active')}
                        className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center gap-2 ${activeTab === 'active'
                                ? 'border-blue-500 text-blue-600'
                                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                            }`}
                    >
                        <Users className="w-4 h-4" />
                        Active Roster
                        <span className="bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full text-xs">
                            {people.filter(p => p.status === 'Active').length}
                        </span>
                    </button>
                    <button
                        onClick={() => setActiveTab('offboarding')}
                        className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center gap-2 ${activeTab === 'offboarding'
                                ? 'border-red-500 text-red-600'
                                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                            }`}
                    >
                        <UserMinus className="w-4 h-4" />
                        Offboarding
                        {offboardingAlerts > 0 && (
                            <span className="bg-red-100 text-red-600 px-2 py-0.5 rounded-full text-xs font-bold animate-pulse">
                                {offboardingAlerts} Alerts
                            </span>
                        )}
                    </button>
                </nav>
            </div>

            {/* Filters */}
            <div className="flex justify-between items-center bg-white p-2 rounded-lg border border-gray-200 shadow-sm">
                <div className="relative flex-1 max-w-md">
                    <Search className="absolute left-3 top-2.5 w-4 h-4 text-gray-400" />
                    <input
                        type="text"
                        placeholder="Search by name or email..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="pl-9 pr-4 py-2 w-full text-sm border-none focus:ring-0 text-gray-600 placeholder-gray-400"
                    />
                </div>
                <button className="p-2 text-gray-400 hover:text-gray-600">
                    <Filter className="w-4 h-4" />
                </button>
            </div>

            {/* Table */}
            <div className="bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden flex-1">
                <table className="w-full text-left">
                    <thead className="bg-gray-50 border-b border-gray-200">
                        <tr>
                            <th className="px-6 py-3 text-xs font-semibold text-gray-500 uppercase">Employee</th>
                            <th className="px-6 py-3 text-xs font-semibold text-gray-500 uppercase">Role</th>
                            {activeTab === 'active' && (
                                <>
                                    <th className="px-6 py-3 text-xs font-semibold text-gray-500 uppercase">Background Check</th>
                                    <th className="px-6 py-3 text-xs font-semibold text-gray-500 uppercase">Security Training</th>
                                    <th className="px-6 py-3 text-xs font-semibold text-gray-500 uppercase">Policy Acceptance</th>
                                </>
                            )}
                            {activeTab === 'offboarding' && (
                                <>
                                    <th className="px-6 py-3 text-xs font-semibold text-gray-500 uppercase">Terminated Date</th>
                                    <th className="px-6 py-3 text-xs font-semibold text-gray-500 uppercase">Active Access (Critical)</th>
                                </>
                            )}
                            <th className="px-6 py-3 text-xs font-semibold text-gray-500 uppercase text-right">Actions</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                        {filteredPeople.map((person) => (
                            <tr key={person.id} className="hover:bg-gray-50 transition-colors">
                                <td className="px-6 py-4">
                                    <div className="flex items-center gap-3">
                                        <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-bold text-xs">
                                            {person.name.charAt(0)}
                                        </div>
                                        <div>
                                            <div className="font-medium text-gray-900 text-sm">{person.name}</div>
                                            <div className="text-xs text-gray-500">{person.email}</div>
                                        </div>
                                    </div>
                                </td>
                                <td className="px-6 py-4 text-sm text-gray-600">{person.role}</td>

                                {activeTab === 'active' && (
                                    <>
                                        <td className="px-6 py-4">
                                            {person.bgCheck ? (
                                                <span className="inline-flex items-center gap-1.5 text-xs font-medium text-green-700 bg-green-100 px-2.5 py-1 rounded-full"><CheckCircle className="w-3.5 h-3.5" /> Passed</span>
                                            ) : (
                                                <span className="inline-flex items-center gap-1.5 text-xs font-medium text-yellow-700 bg-yellow-100 px-2.5 py-1 rounded-full">Pending</span>
                                            )}
                                        </td>
                                        <td className="px-6 py-4">
                                            {person.training ? (
                                                <span className="inline-flex items-center gap-1.5 text-xs font-medium text-green-700 bg-green-100 px-2.5 py-1 rounded-full"><CheckCircle className="w-3.5 h-3.5" /> Complete</span>
                                            ) : (
                                                <span className="inline-flex items-center gap-1.5 text-xs font-medium text-red-700 bg-red-100 px-2.5 py-1 rounded-full"><XCircle className="w-3.5 h-3.5" /> Incomplete</span>
                                            )}
                                        </td>
                                        <td className="px-6 py-4">
                                            {person.policy ? (
                                                <span className="inline-flex items-center gap-1.5 text-xs font-medium text-green-700 bg-green-100 px-2.5 py-1 rounded-full"><CheckCircle className="w-3.5 h-3.5" /> Signed</span>
                                            ) : (
                                                <span className="inline-flex items-center gap-1.5 text-xs font-medium text-red-700 bg-red-100 px-2.5 py-1 rounded-full"><XCircle className="w-3.5 h-3.5" /> Needs Sign</span>
                                            )}
                                        </td>
                                    </>
                                )}

                                {activeTab === 'offboarding' && (
                                    <>
                                        <td className="px-6 py-4 text-sm text-gray-600">{person.terminatedAt}</td>
                                        <td className="px-6 py-4">
                                            {person.accounts.length > 0 ? (
                                                <div className="flex gap-2">
                                                    {person.accounts.map(acc => (
                                                        <span key={acc} className="inline-flex items-center gap-1 px-2 py-1 bg-red-50 text-red-700 border border-red-200 rounded text-xs font-bold">
                                                            <AlertTriangle className="w-3 h-3" /> {acc}
                                                        </span>
                                                    ))}
                                                </div>
                                            ) : (
                                                <span className="text-gray-400 text-sm">All access revoked</span>
                                            )}
                                        </td>
                                    </>
                                )}

                                <td className="px-6 py-4 text-right">
                                    <button className="text-gray-400 hover:text-gray-600">
                                        <MoreVertical className="w-4 h-4" />
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default People;
