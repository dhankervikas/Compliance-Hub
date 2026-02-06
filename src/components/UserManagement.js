import React, { useState, useEffect } from 'react';
import axios from 'axios';
import config from '../config';
import { Users, Edit, Shield, Layers } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

const UserManagement = () => {
    const { token } = useAuth();
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [editingUser, setEditingUser] = useState(null);
    const [showModal, setShowModal] = useState(false);

    // Form State
    const [formData, setFormData] = useState({
        role: 'user',
        allowed_frameworks: []
    });

    const [error, setError] = useState(null);

    useEffect(() => {
        if (token) {
            fetchUsers();
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [token]);

    const fetchUsers = async () => {
        setLoading(true);
        setError(null);
        try {
            console.log("Fetching users from:", `${config.API_BASE_URL}/users/`);
            const res = await axios.get(`${config.API_BASE_URL}/users/`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            console.log("Users response:", res.data);
            setUsers(res.data);
            if (res.data.length === 0) setError("No users returned from API.");
        } catch (err) {
            console.error("Failed to fetch users", err);
            setError(err.message || "Failed to load users");
        } finally {
            setLoading(false);
        }
    };

    const handleEdit = (user) => {
        setEditingUser(user);
        setFormData({
            role: user.role,
            allowed_frameworks: user.allowed_frameworks === 'ALL' ? ['ISO27001', 'SOC2', 'NIST_CSF'] : (user.allowed_frameworks || '').split(',')
        });
        setShowModal(true);
    };

    const handleSave = async () => {
        try {
            // Convert array back to string
            const fwString = formData.allowed_frameworks.length === 3 ? 'ALL' : formData.allowed_frameworks.join(',');

            await axios.put(`${config.API_BASE_URL}/users/${editingUser.id}`, {
                role: formData.role,
                allowed_frameworks: fwString
            }, {
                headers: { Authorization: `Bearer ${token}` }
            });

            setShowModal(false);
            fetchUsers();
        } catch (err) {
            alert("Failed to update user");
        }
    };

    const toggleFramework = (fw) => {
        setFormData(prev => {
            const current = prev.allowed_frameworks;
            if (current.includes(fw)) {
                return { ...prev, allowed_frameworks: current.filter(f => f !== fw) };
            } else {
                return { ...prev, allowed_frameworks: [...current, fw] };
            }
        });
    };

    if (loading) return <div className="p-8">Loading users...</div>;

    return (
        <div className="p-8">
            <h1 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
                <Users className="w-6 h-6 text-blue-600" />
                User Management
            </h1>

            {error && (
                <div className="mb-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative">
                    <strong className="font-bold">Error:</strong>
                    <span className="block sm:inline ml-2">{error}</span>
                    <div className="text-xs mt-2 text-red-800">
                        Attempted: {config.API_BASE_URL}/users/
                    </div>
                    <button onClick={fetchUsers} className="ml-4 underline">Retry</button>
                </div>
            )}

            <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                <table className="w-full text-left border-collapse">
                    <thead>
                        <tr className="bg-gray-50 border-b border-gray-200 text-xs font-bold text-gray-500 uppercase tracking-wider">
                            <th className="p-4">User</th>
                            <th className="p-4">Email</th>
                            <th className="p-4">Role</th>
                            <th className="p-4">Allowed Frameworks</th>
                            <th className="p-4 text-right">Actions</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                        {users.map(user => (
                            <tr key={user.id} className="hover:bg-gray-50">
                                <td className="p-4 font-medium text-gray-900">{user.username}</td>
                                <td className="p-4 text-gray-600">{user.email}</td>
                                <td className="p-4">
                                    <span className={`px-2 py-1 rounded text-xs font-bold ${user.role === 'admin' ? 'bg-purple-100 text-purple-700' :
                                        user.role === 'auditor' ? 'bg-orange-100 text-orange-700' : 'bg-gray-100 text-gray-600'
                                        }`}>
                                        {user.role.toUpperCase()}
                                    </span>
                                </td>
                                <td className="p-4 text-sm text-gray-600">
                                    {user.allowed_frameworks === 'ALL' ? (
                                        <span className="bg-green-100 text-green-700 px-2 py-0.5 rounded text-xs">All Frameworks</span>
                                    ) : (
                                        <div className="flex gap-1">
                                            {user.allowed_frameworks?.split(',').map(fw => (
                                                <span key={fw} className="bg-blue-50 text-blue-600 border border-blue-100 px-1.5 py-0.5 rounded text-[10px]">{fw}</span>
                                            ))}
                                        </div>
                                    )}
                                </td>
                                <td className="p-4 text-right">
                                    <button onClick={() => handleEdit(user)} className="p-2 hover:bg-blue-50 text-blue-600 rounded">
                                        <Edit className="w-4 h-4" />
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {/* EDIT MODAL */}
            {showModal && (
                <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
                    <div className="bg-white rounded-xl shadow-2xl max-w-md w-full p-6">
                        <h3 className="text-xl font-bold mb-4">Edit User: {editingUser.username}</h3>

                        <div className="mb-4">
                            <label className="block text-sm font-bold text-gray-700 mb-2">Role</label>
                            <select
                                value={formData.role}
                                onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                                className="w-full border border-gray-300 rounded p-2"
                            >
                                <option value="user">User</option>
                                <option value="admin">Admin</option>
                                <option value="auditor">Auditor</option>
                            </select>
                        </div>

                        <div className="mb-6">
                            <label className="block text-sm font-bold text-gray-700 mb-2">Allowed Frameworks</label>
                            <div className="space-y-2">
                                {[
                                    { id: 'ISO27001', label: 'ISO 27001:2022', icon: Shield },
                                    { id: 'SOC2', label: 'SOC 2 Type II', icon: Layers },
                                    { id: 'NIST_CSF', label: 'NIST CSF 2.0', icon: Shield }
                                ].map(fw => (
                                    <label key={fw.id} className="flex items-center gap-3 p-3 border rounded-lg cursor-pointer hover:bg-gray-50">
                                        <input
                                            type="checkbox"
                                            checked={formData.allowed_frameworks.includes(fw.id)}
                                            onChange={() => toggleFramework(fw.id)}
                                            className="w-4 h-4 text-blue-600 rounded"
                                        />
                                        <fw.icon className="w-4 h-4 text-gray-400" />
                                        <span className="text-sm font-medium">{fw.label}</span>
                                    </label>
                                ))}
                            </div>
                        </div>

                        <div className="flex justify-end gap-3">
                            <button onClick={() => setShowModal(false)} className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded">Cancel</button>
                            <button onClick={handleSave} className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">Save Changes</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default UserManagement;
