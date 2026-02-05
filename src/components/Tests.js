import React, { useState, useEffect } from 'react';
import axios from '../services/api';
import {
    CheckCircle,
    XCircle,
    Search,
    X,
    Code,
    Clock,
    AlertCircle
} from 'lucide-react'; // Switched to Lucide for consistency

const Tests = () => {
    const [tests, setTests] = useState([]);
    const [filter, setFilter] = useState('all'); // all, passing, failing, snoozed
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedTest, setSelectedTest] = useState(null);
    const [loading, setLoading] = useState(true);

    // Snooze Modal State
    const [snoozeModalOpen, setSnoozeModalOpen] = useState(false);
    const [justification, setJustification] = useState('');

    useEffect(() => {
        const fetchTests = async () => {
            try {
                // Mocking the backend response if needed, but assuming valid endpoint
                const res = await axios.get('/automated-tests/results');
                setTests(res.data);
                setLoading(false);
            } catch (err) {
                console.error("Failed to fetch tests", err);
                setLoading(false);
            }
        };
        fetchTests();
    }, []);

    const handleSnooze = (e) => {
        e.preventDefault();
        // Mock update local state
        const updatedTests = tests.map(t =>
            t.id === selectedTest.id
                ? { ...t, status: 'snoozed', justification: justification, snoozedAt: new Date().toLocaleDateString() }
                : t
        );
        setTests(updatedTests);
        // Update selected test view as well
        setSelectedTest({ ...selectedTest, status: 'snoozed', justification: justification });

        setSnoozeModalOpen(false);
        setJustification('');
    };

    const filteredTests = tests.filter(test => {
        const matchesSearch = test.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
            test.id.toLowerCase().includes(searchTerm.toLowerCase());
        const matchesFilter = filter === 'all' || test.status === filter;
        // Special case: 'failing' filter should NOT show snoozed tests
        if (filter === 'failing' && test.status === 'snoozed') return false;

        return matchesSearch && matchesFilter;
    });

    if (loading) return <div className="p-8 text-center text-gray-500">Loading tests...</div>;

    return (
        <div className="flex h-full relative">
            <div className={`flex-1 space-y-6 transition-all duration-300 ${selectedTest ? 'pr-96' : ''}`}>

                {/* Header & Controls */}
                <div className="flex justify-between items-center bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
                    <div>
                        <h1 className="text-2xl font-bold text-gray-900">Automated Tests</h1>
                        <p className="text-sm text-gray-500">Real-time validation against compliance frameworks.</p>
                    </div>
                    <div className="flex gap-4">
                        <div className="text-center px-4 border-r border-gray-200">
                            <div className="text-2xl font-bold text-green-600">{tests.filter(t => t.status === 'passing').length}</div>
                            <div className="text-xs text-gray-500 uppercase">Passing</div>
                        </div>
                        <div className="text-center px-4 border-r border-gray-200">
                            <div className="text-2xl font-bold text-red-600">{tests.filter(t => t.status === 'failing').length}</div>
                            <div className="text-xs text-gray-500 uppercase">Failing</div>
                        </div>
                        <div className="text-center px-4">
                            <div className="text-2xl font-bold text-gray-600">{tests.filter(t => t.status === 'snoozed').length}</div>
                            <div className="text-xs text-gray-500 uppercase">Snoozed</div>
                        </div>
                    </div>
                </div>

                {/* Toolbar */}
                <div className="flex justify-between items-center">
                    <div className="flex gap-2">
                        {['all', 'failing', 'passing', 'snoozed'].map(f => (
                            <button
                                key={f}
                                onClick={() => setFilter(f)}
                                className={`px-4 py-2 rounded-lg text-sm font-medium capitalize transition-colors ${filter === f
                                    ? 'bg-slate-900 text-white'
                                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                                    }`}
                            >
                                {f}
                            </button>
                        ))}
                    </div>
                    <div className="relative w-64">
                        <Search className="w-4 h-4 absolute left-3 top-3 text-gray-400" />
                        <input
                            type="text"
                            placeholder="Search tests..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="w-full pl-10 pr-4 py-2 bg-white border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none shadow-sm"
                        />
                    </div>
                </div>

                {/* Tests Table */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                    <table className="w-full text-left">
                        <thead className="bg-gray-50 border-b border-gray-100">
                            <tr>
                                <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase">Test Name</th>
                                <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase">Status</th>
                                <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase">Owner</th>
                                <th className="px-6 py-4 text-xs font-semibold text-gray-500 uppercase">Last Run</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-100">
                            {filteredTests.map(test => (
                                <tr
                                    key={test.id}
                                    onClick={() => setSelectedTest(test)}
                                    className={`cursor-pointer transition-colors ${selectedTest?.id === test.id ? 'bg-blue-50' : 'hover:bg-gray-50'}`}
                                >
                                    <td className="px-6 py-4">
                                        <div className="font-medium text-gray-900">{test.name}</div>
                                        <div className="text-xs text-gray-500 font-mono mt-1">{test.id}</div>
                                    </td>
                                    <td className="px-6 py-4">
                                        {test.status === 'passing' && (
                                            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-green-100 text-green-700">
                                                <CheckCircle className="w-3 h-3" /> Passing
                                            </span>
                                        )}
                                        {test.status === 'failing' && (
                                            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-red-100 text-red-700">
                                                <XCircle className="w-3 h-3" /> Failing
                                            </span>
                                        )}
                                        {test.status === 'snoozed' && (
                                            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-700">
                                                <Clock className="w-3 h-3" /> Snoozed
                                            </span>
                                        )}
                                    </td>
                                    <td className="px-6 py-4 text-sm text-gray-600">{test.owner}</td>
                                    <td className="px-6 py-4 text-sm text-gray-500">{test.last_run}</td>
                                </tr>
                            ))}
                            {filteredTests.length === 0 && (
                                <tr>
                                    <td colSpan="4" className="px-6 py-12 text-center text-gray-500">
                                        No tests found.
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Drill-Down Panel (Right Side) */}
            {selectedTest && (
                <div className="w-96 bg-white border-l border-gray-200 shadow-2xl h-[calc(100vh-4rem)] overflow-y-auto fixed right-0 top-0 bottom-0 p-6 z-20 animate-slide-in flex flex-col">

                    {/* Panel Header */}
                    <div className="flex justify-between items-start mb-6">
                        <button
                            onClick={() => setSelectedTest(null)}
                            className="p-2 text-gray-400 hover:text-gray-600 bg-gray-100 rounded-full hover:bg-gray-200 transition-colors"
                        >
                            <X className="w-5 h-5" />
                        </button>

                        {/* Snooze Button (Only for Failing Tests) */}
                        {selectedTest.status === 'failing' && (
                            <button
                                onClick={() => setSnoozeModalOpen(true)}
                                className="px-3 py-1.5 bg-gray-100 hover:bg-gray-200 text-gray-700 text-xs font-bold uppercase rounded flex items-center gap-1 border border-gray-300"
                            >
                                <Clock className="w-3 h-3" /> Snooze
                            </button>
                        )}
                    </div>

                    <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                            {selectedTest.status === 'passing' && <CheckCircle className="w-8 h-8 text-green-500" />}
                            {selectedTest.status === 'failing' && <XCircle className="w-8 h-8 text-red-500" />}
                            {selectedTest.status === 'snoozed' && <Clock className="w-8 h-8 text-gray-500" />}
                            <span className={`text-sm font-bold uppercase tracking-wide
                                ${selectedTest.status === 'passing' ? 'text-green-600' : ''}
                                ${selectedTest.status === 'failing' ? 'text-red-600' : ''}
                                ${selectedTest.status === 'snoozed' ? 'text-gray-600' : ''}
                            `}>
                                {selectedTest.status}
                            </span>
                        </div>
                        <h2 className="text-xl font-bold text-gray-900 mb-4">{selectedTest.name}</h2>
                        <div className="text-sm text-gray-500 font-mono bg-gray-100 px-2 py-1 rounded inline-block mb-6">
                            ID: {selectedTest.id}
                        </div>

                        {selectedTest.status === 'snoozed' && (
                            <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-6">
                                <h3 className="text-xs font-bold text-gray-500 uppercase mb-1">Justification</h3>
                                <p className="text-sm text-gray-800 italic">"{selectedTest.justification}"</p>
                            </div>
                        )}

                        <div className="space-y-6">
                            <div>
                                <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wide mb-2">Description</h3>
                                <p className="text-sm text-gray-600 leading-relaxed">{selectedTest.description}</p>
                            </div>

                            <div>
                                <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wide mb-2">Remediation</h3>
                                <div className="bg-blue-50 text-blue-800 p-4 rounded-lg text-sm whitespace-pre-line border border-blue-100">
                                    {selectedTest.remediation}
                                </div>
                            </div>

                            <div>
                                <div className="flex items-center gap-2 mb-2">
                                    <Code className="w-4 h-4 text-gray-400" />
                                    <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wide">Evidence Payload</h3>
                                </div>
                                <div className="bg-slate-900 text-slate-300 p-4 rounded-lg text-xs font-mono overflow-x-auto border border-slate-700 shadow-inner">
                                    <pre>{JSON.stringify(selectedTest.evidence, null, 2)}</pre>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Snooze Modal */}
            {snoozeModalOpen && (
                <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50">
                    <div className="bg-white rounded-xl shadow-2xl p-6 max-w-md w-full mx-4 animate-scale-in">
                        <div className="flex items-center gap-3 mb-4 text-gray-900">
                            <Clock className="w-6 h-6" />
                            <h2 className="text-xl font-bold">Snooze Test</h2>
                        </div>
                        <p className="text-sm text-gray-600 mb-4">
                            Snoozing a test will hide it from the failing list for a set period.
                            You <strong>must</strong> provide a valid business justification.
                        </p>

                        <form onSubmit={handleSnooze} className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Reason (Justification)</label>
                                <textarea
                                    value={justification}
                                    onChange={(e) => setJustification(e.target.value)}
                                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 min-h-[100px]"
                                    placeholder="e.g., False positive, or risk accepted for Q1..."
                                    required
                                />
                            </div>

                            <div className="flex gap-3 pt-2">
                                <button
                                    type="button"
                                    onClick={() => setSnoozeModalOpen(false)}
                                    className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium"
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    className="flex-1 px-4 py-2 bg-slate-900 text-white rounded-lg hover:bg-slate-800 font-medium"
                                >
                                    Confirm Snooze
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Tests;
