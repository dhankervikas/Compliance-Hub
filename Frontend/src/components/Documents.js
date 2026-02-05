import React, { useState, useEffect } from 'react';
import axios from '../services/api';
import { FileText, Search, Download, Eye, ShieldCheck } from 'lucide-react';

const Documents = () => {
    const [documents, setDocuments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState("");

    useEffect(() => {
        fetchDocuments();
    }, []);

    const fetchDocuments = async () => {
        try {
            // In a real app, might have a specific /documents endpoint
            // For now, fetch all policies and filter by status='Approved'
            const res = await axios.get('/policies');
            const approved = res.data.filter(p => p.status === 'Approved');
            setDocuments(approved);
        } catch (error) {
            console.error("Failed to fetch documents", error);
        } finally {
            setLoading(false);
        }
    };

    const filteredDocs = documents.filter(doc =>
        doc.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        doc.description?.toLowerCase().includes(searchTerm.toLowerCase())
    );

    return (
        <div className="p-6 max-w-7xl mx-auto animate-in fade-in duration-500">
            <div className="flex justify-between items-center mb-8">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                        <ShieldCheck className="w-8 h-8 text-green-600" />
                        Approved Documents
                    </h1>
                    <p className="text-gray-500 mt-1">Official repository of approved compliance artifacts.</p>
                </div>

                {/* Search */}
                <div className="relative w-64">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                    <input
                        type="search"
                        placeholder="Search documents..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 text-sm"
                    />
                </div>
            </div>

            {loading ? (
                <div className="text-center py-12 text-gray-500">Loading library...</div>
            ) : filteredDocs.length === 0 ? (
                <div className="bg-gray-50 rounded-xl p-12 text-center border-2 border-dashed border-gray-200">
                    <FileText className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900">No Approved Documents</h3>
                    <p className="text-gray-500 mt-1 text-sm">Policies must be approved in the Policy Editor before appearing here.</p>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {filteredDocs.map(doc => (
                        <div key={doc.id} className="bg-white border border-gray-200 rounded-xl p-5 hover:shadow-md transition-shadow group relative overflow-hidden">
                            <div className="absolute top-0 right-0 w-16 h-16 bg-green-50 rounded-bl-full -mr-8 -mt-8 transition-transform group-hover:scale-110"></div>

                            <div className="flex items-start justify-between mb-4 relative z-10">
                                <div className="p-2 bg-green-50 text-green-700 rounded-lg">
                                    <FileText className="w-6 h-6" />
                                </div>
                                <span className="text-xs font-semibold bg-green-100 text-green-700 px-2 py-1 rounded-full border border-green-200">
                                    v{doc.version}
                                </span>
                            </div>

                            <h3 className="font-bold text-gray-900 mb-1 line-clamp-1" title={doc.name}>{doc.name}</h3>
                            <p className="text-sm text-gray-500 mb-4 line-clamp-2 min-h-[2.5em]">{doc.description}</p>

                            <div className="flex items-center justify-between text-xs text-gray-400 pt-4 border-t border-gray-100">
                                <span>Approved: {new Date(doc.updated_at).toLocaleDateString()}</span>
                                <div className="flex gap-2">
                                    <button className="p-1.5 hover:bg-gray-100 rounded text-gray-600 transition-colors" title="View">
                                        <Eye className="w-4 h-4" />
                                    </button>
                                    <button className="p-1.5 hover:bg-gray-100 rounded text-gray-600 transition-colors" title="Download PDF">
                                        <Download className="w-4 h-4" />
                                    </button>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default Documents;
