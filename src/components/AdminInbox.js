import React, { useState, useEffect } from 'react';
import axios from 'axios';
import config from '../config';

const API_URL = config.API_BASE_URL;

const AdminInbox = () => {
    const [tasks, setTasks] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchTasks();
    }, []);

    const fetchTasks = async () => {
        try {
            const token = localStorage.getItem('token');
            const res = await axios.get(`${API_URL}/tasks/`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            // Filter only pending approvals
            const pending = res.data.filter(t => t.status === "PENDING");
            setTasks(pending);
            setLoading(false);
        } catch (err) {
            console.error(err);
            setError("Failed to load tasks");
            setLoading(false);
        }
    };

    const handleView = (task) => {
        // Construct download URL
        const url = `${API_URL}/documents/download/${task.document_id}`;
        window.open(url, '_blank');
    };

    const handleApprove = async (task) => {
        if (!window.confirm("Are you sure you want to APPROVE this document? This will generate a final audit record.")) return;

        try {
            const token = localStorage.getItem('token');
            const res = await axios.post(`${API_URL}/documents/approve`, {
                control_id: task.control_id,
                version_filename: task.document_id,
                approver_name: "Admin User" // In real app, get from profile
            }, {
                headers: { Authorization: `Bearer ${token}` }
            });

            alert(res.data.message);

            // If PDF returned, open it
            if (res.data.pdf_url) {
                window.open(`${API_URL.replace('/api/v1', '')}${res.data.pdf_url}`, '_blank');
            }

            fetchTasks(); // Refresh list
        } catch (err) {
            console.error(err);
            alert("Approval failed: " + (err.response?.data?.detail || err.message));
        }
    };

    if (loading) return <div className="p-8 text-center text-gray-500">Loading Inbox...</div>;
    if (error) return <div className="p-8 text-center text-red-500">{error}</div>;

    return (
        <div className="p-6 max-w-6xl mx-auto">
            <h1 className="text-2xl font-bold text-gray-800 mb-6">Admin Notification Inbox</h1>

            <div className="bg-white rounded-lg shadow overflow-hidden">
                {tasks.length === 0 ? (
                    <div className="p-12 text-center text-gray-400 italic">
                        No pending tasks. You're all caught up!
                    </div>
                ) : (
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                            <tr>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Document / Task</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Control ID</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date Sent</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Requester</th>
                                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {tasks.map((task) => (
                                <tr key={task.id} className="hover:bg-gray-50">
                                    <td className="px-6 py-4">
                                        <div className="text-sm font-medium text-gray-900">{task.title}</div>
                                        <div className="text-sm text-gray-500">{task.document_id}</div>
                                    </td>
                                    <td className="px-6 py-4 text-sm text-gray-500">
                                        <span className="bg-blue-100 text-blue-800 px-2 py-0.5 rounded text-xs">{task.control_id}</span>
                                    </td>
                                    <td className="px-6 py-4 text-sm text-gray-500">
                                        {new Date(task.created_at).toLocaleDateString()}
                                    </td>
                                    <td className="px-6 py-4 text-sm text-gray-500">
                                        User (External)
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-3">
                                        <button
                                            onClick={() => handleView(task)}
                                            className="text-indigo-600 hover:text-indigo-900"
                                        >
                                            View & Review
                                        </button>
                                        <button
                                            onClick={() => handleApprove(task)}
                                            className="bg-green-600 text-white px-3 py-1 rounded hover:bg-green-700 transition-colors"
                                        >
                                            Approve
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>
        </div>
    );
};

export default AdminInbox;
