import React, { useState, useEffect } from 'react';
import axios from '../services/api';
import {
    Upload,
    FileText,
    Trash2,
    Eye,

    Search,
    CheckCircle,
    Folder,
    FolderOpen,
    ChevronRight,
    ChevronDown,
    AlertTriangle
} from 'lucide-react';

const Evidence = ({ readOnly = false }) => {
    const [evidence, setEvidence] = useState([]);
    const [controls, setControls] = useState([]);
    const [processes, setProcesses] = useState([]);
    const [controlToProcessMap, setControlToProcessMap] = useState({});

    // UI State
    const [filter, setFilter] = useState('all');
    const [searchTerm, setSearchTerm] = useState('');
    const [loading, setLoading] = useState(true);
    const [expandedGroups, setExpandedGroups] = useState({}); // { processId: true/false }

    // Debug Error States
    const [error, setError] = useState(null);

    // Upload Modal State
    const [uploadModalOpen, setUploadModalOpen] = useState(false);
    const [selectedFile, setSelectedFile] = useState(null);
    const [selectedControlId, setSelectedControlId] = useState('');
    const [description, setDescription] = useState('');
    const [uploading, setUploading] = useState(false);

    const fetchData = async () => {
        setLoading(true);
        try {
            const [ctrlRes, eviRes, procRes] = await Promise.all([
                axios.get('/controls/'),
                axios.get('/evidence/'),
                axios.get('/processes/')
            ]);

            setControls(ctrlRes.data);
            setEvidence(eviRes.data);
            setProcesses(procRes.data);

            // Build Map: ControlID -> Process Name
            const mapping = {};
            procRes.data.forEach(proc => {
                proc.sub_processes.forEach(sub => {
                    sub.controls.forEach(c => {
                        mapping[c.id] = proc.name;
                    });
                });
            });
            setControlToProcessMap(mapping);

            // Auto-expand all groups initially
            const initialExpanded = {};
            procRes.data.forEach(p => initialExpanded[p.name] = true);
            initialExpanded['Uncategorized'] = true;
            setExpandedGroups(initialExpanded);

            setError(null);
        } catch (err) {
            console.error("Data Fetch Error:", err);
            setError("Failed to load data. Please ensure the backend is running.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    const toggleGroup = (groupName) => {
        setExpandedGroups(prev => ({
            ...prev,
            [groupName]: !prev[groupName]
        }));
    };

    const handleFileChange = (e) => {
        if (e.target.files && e.target.files[0]) {
            setSelectedFile(e.target.files[0]);
        }
    };

    const handleUpload = async (e) => {
        e.preventDefault();
        if (!selectedFile || !selectedControlId) return;

        setUploading(true);
        const formData = new FormData();
        formData.append('file', selectedFile);
        formData.append('control_id', selectedControlId);
        formData.append('title', selectedFile.name);
        formData.append('description', description);

        try {
            await axios.post('/evidence/upload', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            await fetchData(); // Refresh list
            setUploadModalOpen(false);
            resetForm();
        } catch (err) {
            console.error("Upload failed", err);
            alert("Upload failed: " + (err.response?.data?.detail || err.message));
        } finally {
            setUploading(false);
        }
    };

    const handleDelete = async (id) => {
        if (readOnly) return;
        if (!window.confirm("Are you sure you want to delete this evidence?")) return;
        try {
            // await axios.delete(`/evidence/${id}`); // Uncomment when endpoint exists
            setEvidence(evidence.filter(e => e.id !== id)); // Optimistic UI
            alert("Deleted (Mock)");
        } catch (err) {
            console.error("Delete failed", err);
        }
    };

    const resetForm = () => {
        setSelectedFile(null);
        setSelectedControlId('');
        setDescription('');
    };

    // --- Grouping Logic ---
    const getFilteredEvidence = () => {
        return evidence.filter(item => {
            const matchesSearch = item.filename.toLowerCase().includes(searchTerm.toLowerCase()) ||
                item.title.toLowerCase().includes(searchTerm.toLowerCase());
            const matchesFilter = filter === 'all' ||
                (filter === 'manual' && item.validation_source === 'manual') ||
                (filter === 'automated' && item.validation_source !== 'manual');
            return matchesSearch && matchesFilter;
        });
    };

    const groupedEvidence = () => {
        const filtered = getFilteredEvidence();
        const groups = {};

        // Initialize groups from processes ensuring strict order if needed
        processes.forEach(p => groups[p.name] = []);
        groups['Uncategorized'] = [];

        filtered.forEach(item => {
            const procName = controlToProcessMap[item.control_id] || 'Uncategorized';
            if (!groups[procName]) groups[procName] = []; // Handle unknown dynamically
            groups[procName].push(item);
        });

        return groups;
    };

    const groups = groupedEvidence();

    if (loading) return <div className="p-12 text-center text-gray-500">Loading Evidence Library...</div>;

    return (
        <div className="space-y-6 h-full relative">

            {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-center gap-3">
                    <AlertTriangle className="w-5 h-5" />
                    <div>
                        <p className="font-bold">System Error</p>
                        <p className="text-sm">{error}</p>
                    </div>
                </div>
            )}

            {/* Header */}
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">Evidence Library</h1>
                    <p className="text-sm text-gray-500">Central repository grouped by Organizational Process.</p>
                </div>
                {!readOnly && (
                    <button
                        onClick={() => setUploadModalOpen(true)}
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 shadow-sm flex items-center gap-2"
                    >
                        <Upload className="w-5 h-5" />
                        Upload Evidence
                    </button>
                )}
            </div>

            {/* Filters */}
            <div className="flex justify-between items-center bg-white p-2 rounded-xl border border-gray-200 shadow-sm">
                <div className="flex gap-2">
                    {['all', 'manual', 'automated'].map(f => (
                        <button
                            key={f}
                            onClick={() => setFilter(f)}
                            className={`px-4 py-2 rounded-lg text-sm font-medium capitalize transition-colors ${filter === f ? 'bg-slate-900 text-white' : 'text-gray-600 hover:bg-gray-100'}`}
                        >
                            {f === 'manual' ? 'Manual Uploads' : f}
                        </button>
                    ))}
                </div>
                <div className="relative mr-2">
                    <Search className="absolute left-3 top-2.5 w-4 h-4 text-gray-400" />
                    <input
                        type="text"
                        placeholder="Search files..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="pl-9 pr-4 py-2 w-64 text-sm bg-gray-50 border-none rounded-lg focus:ring-0"
                    />
                </div>
            </div>

            {/* Grouped Lists */}
            <div className="space-y-4">
                {Object.entries(groups).map(([groupName, items]) => {
                    // Hide empty groups if searching/filtering, OR show all if desired. 
                    // Let's hide empty strictly to reduce noise, unless 'Uncategorized' has items.
                    if (items.length === 0) return null;

                    const isExpanded = expandedGroups[groupName];

                    return (
                        <div key={groupName} className="bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm">
                            <button
                                onClick={() => toggleGroup(groupName)}
                                className="w-full px-6 py-4 flex items-center justify-between bg-gray-50 hover:bg-gray-100 transition-colors"
                            >
                                <div className="flex items-center gap-3">
                                    {isExpanded ? <ChevronDown className="w-5 h-5 text-gray-500" /> : <ChevronRight className="w-5 h-5 text-gray-500" />}
                                    <div className="p-2 bg-white rounded-lg border border-gray-200 text-blue-600">
                                        <Folder className="w-5 h-5" />
                                    </div>
                                    <div className="text-left">
                                        <h3 className="font-semibold text-gray-900">{groupName}</h3>
                                        <p className="text-xs text-gray-500">{items.length} file{items.length !== 1 && 's'}</p>
                                    </div>
                                </div>
                            </button>

                            {isExpanded && (
                                <div className="border-t border-gray-100">
                                    <table className="w-full text-left">
                                        <thead className="bg-white border-b border-gray-50">
                                            <tr>
                                                <th className="px-6 py-3 text-xs font-semibold text-gray-400 uppercase">File</th>
                                                <th className="px-6 py-3 text-xs font-semibold text-gray-400 uppercase">Source</th>
                                                <th className="px-6 py-3 text-xs font-semibold text-gray-400 uppercase">Linked Control</th>
                                                <th className="px-6 py-3 text-xs font-semibold text-gray-400 uppercase">Status</th>
                                                <th className="px-6 py-3 text-xs font-semibold text-gray-400 uppercase text-right">Actions</th>
                                            </tr>
                                        </thead>
                                        <tbody className="divide-y divide-gray-50">
                                            {items.map(item => {
                                                const isAutomated = item.validation_source !== 'manual';
                                                return (
                                                    <tr key={item.id} className="hover:bg-blue-50/30 transition-colors">
                                                        <td className="px-6 py-3">
                                                            <div className="flex items-center gap-3">
                                                                <FileText className="w-4 h-4 text-gray-400" />
                                                                <span className="text-sm font-medium text-gray-700">{item.title}</span>
                                                            </div>
                                                        </td>
                                                        <td className="px-6 py-3">
                                                            {isAutomated ? (
                                                                <span className="text-xs font-bold text-purple-600">Automated</span>
                                                            ) : (
                                                                <span className="text-xs font-bold text-blue-600">Manual</span>
                                                            )}
                                                        </td>
                                                        <td className="px-6 py-3">
                                                            <span className="font-mono text-xs text-gray-500 bg-gray-100 px-1.5 py-0.5 rounded">
                                                                {controls.find(c => c.id === item.control_id)?.control_id || item.control_id}
                                                            </span>
                                                        </td>
                                                        <td className="px-6 py-3">
                                                            <span className="inline-flex items-center gap-1 text-xs text-green-700">
                                                                <CheckCircle className="w-3 h-3" /> Valid
                                                            </span>
                                                        </td>
                                                        <td className="px-6 py-3 text-right">
                                                            <div className="flex justify-end gap-2">
                                                                <button className="text-gray-400 hover:text-blue-600">
                                                                    <Eye className="w-4 h-4" />
                                                                </button>
                                                                {!readOnly && (
                                                                    <button className="text-gray-400 hover:text-red-500" onClick={() => handleDelete(item.id)}>
                                                                        <Trash2 className="w-4 h-4" />
                                                                    </button>
                                                                )}
                                                            </div>
                                                        </td>
                                                    </tr>
                                                )
                                            })}
                                        </tbody>
                                    </table>
                                </div>
                            )}
                        </div>
                    );
                })}

                {getFilteredEvidence().length === 0 && (
                    <div className="bg-gray-50 border border-dashed border-gray-300 rounded-xl p-12 text-center text-gray-500">
                        <FolderOpen className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                        <p>No documents found matching your filters.</p>
                    </div>
                )}
            </div>

            {/* Upload Modal */}
            {uploadModalOpen && !readOnly && (
                <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50">
                    <div className="bg-white rounded-xl shadow-2xl p-6 max-w-md w-full mx-4 animate-scale-in">
                        <h2 className="text-xl font-bold text-gray-900 mb-4">Upload Evidence</h2>
                        <form onSubmit={handleUpload} className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Select File</label>
                                <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:bg-gray-50 cursor-pointer relative">
                                    <input type="file" onChange={handleFileChange} className="absolute inset-0 w-full h-full opacity-0 cursor-pointer" />
                                    <Upload className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                                    <p className="text-sm text-gray-600">{selectedFile ? selectedFile.name : "Click to browse"}</p>
                                </div>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Link to Control</label>
                                <select
                                    value={selectedControlId}
                                    onChange={(e) => setSelectedControlId(e.target.value)}
                                    className="w-full px-3 py-2 border rounded-lg"
                                    required
                                >
                                    <option value="">Select a control...</option>
                                    {controls.map(c => (
                                        <option key={c.id} value={c.id}>{c.control_id} - {c.title}</option>
                                    ))}
                                </select>
                            </div>
                            <div className="flex gap-3 pt-4">
                                <button type="button" onClick={() => setUploadModalOpen(false)} className="flex-1 px-4 py-2 border rounded-lg">Cancel</button>
                                <button type="submit" disabled={uploading} className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg">
                                    {uploading ? 'Uploading...' : 'Upload'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Evidence;
