
import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { Upload, FileText, CheckCircle, AlertCircle, RefreshCw, Users } from 'lucide-react';

const PeopleDirectory = () => {
    const [people, setPeople] = useState([]);
    const [loading, setLoading] = useState(true);
    const [importing, setImporting] = useState(false);
    const [error, setError] = useState(null);

    const fetchPeople = async () => {
        setLoading(true);
        try {
            const res = await api.get('/people/');
            setPeople(res.data);
        } catch (err) {
            console.error("Failed to fetch people", err);
            setError("Failed to load directory.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchPeople();
    }, []);

    const handleFileUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);

        setImporting(true);
        try {
            await api.post('/people/import', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            fetchPeople(); // Refresh list
        } catch (err) {
            console.error("Import failed", err);
            alert("Import failed: " + (err.response?.data?.detail || err.message));
        } finally {
            setImporting(false);
        }
    };

    // Simulation for "Sync from Source"
    const handleSimulatedSync = async () => {
        setImporting(true);
        const mockData = [
            { full_name: "Alice Good", email: "alice@example.com", employment_status: "Active", job_title: "Engineer", department: "Engineering", external_id: "EXT-001" },
            { full_name: "Bob Risk", email: "admin@testtest.local", employment_status: "Inactive", job_title: "Ex-Admin", department: "IT", external_id: "EXT-002" },
            { full_name: "Charlie Contractor", email: "charlie@vendor.com", employment_status: "Contractor", job_title: "Consultant", department: "Security", external_id: "EXT-003" }
        ];

        try {
            await api.post('/people/import', mockData); // JSON body
            fetchPeople();
        } catch (err) {
            console.error("Sync failed", err);
        } finally {
            setImporting(false);
        }
    };

    return (
        <div className="p-6">
            <div className="flex justify-between items-center mb-6">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                        <Users className="text-blue-600" />
                        People Directory
                    </h1>
                    <p className="text-sm text-gray-500">Source of Truth for Identity & Access Compliance</p>
                </div>
                <div className="flex gap-2">
                    <button
                        onClick={handleSimulatedSync}
                        disabled={importing}
                        className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 text-sm font-medium text-gray-700"
                    >
                        <RefreshCw size={16} className={importing ? "animate-spin" : ""} />
                        {importing ? "Syncing..." : "Simulate Azure AD Sync"}
                    </button>

                    <label className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 cursor-pointer text-sm font-medium">
                        <Upload size={16} />
                        Import CSV
                        <input type="file" className="hidden" accept=".csv,.json" onChange={handleFileUpload} />
                    </label>
                </div>
            </div>

            {loading ? (
                <div className="text-center py-12 text-gray-500">Loading directory...</div>
            ) : error ? (
                <div className="text-red-500 p-4 bg-red-50 rounded">{error}</div>
            ) : (
                <div className="bg-white rounded-lg shadow overflow-hidden border border-gray-200">
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                            <tr>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Email</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Title</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Source</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Last Synced</th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {people.map((person) => (
                                <tr key={person.id} className="hover:bg-gray-50">
                                    <td className="px-6 py-4 whitespace-nowrap font-medium text-gray-900">{person.full_name}</td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{person.email}</td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                                            ${person.employment_status === 'Active' ? 'bg-green-100 text-green-800' :
                                                person.employment_status === 'Inactive' ? 'bg-red-100 text-red-800' :
                                                    'bg-yellow-100 text-yellow-800'}`}>
                                            {person.employment_status}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                        {person.job_title}
                                        <div className="text-xs text-gray-400">{person.department}</div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 capitalize">{person.source?.replace('_', ' ')}</td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">
                                        {new Date(person.last_synced_at).toLocaleDateString()}
                                    </td>
                                </tr>
                            ))}
                            {people.length === 0 && (
                                <tr>
                                    <td colSpan="6" className="px-6 py-12 text-center text-gray-400">
                                        No people imported yet. Start by syncing or importing data.
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
};

export default PeopleDirectory;
