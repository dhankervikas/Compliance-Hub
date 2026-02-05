import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import {
    ArrowLeft, Search, Filter, Shield, FileText, CheckCircle,
    AlertTriangle, Lock, Eye, Download, Upload, Server, Activity
} from 'lucide-react';

const API_URL = 'https://assurisk-backend.onrender.com/api/v1';

// HIPAA SPECIFIC COLORS & ICONS
const STATUS_COLORS = {
    "Required": "bg-blue-100 text-blue-800 border-blue-200",
    "Addressable": "bg-teal-100 text-teal-800 border-teal-200"
};

const SAFEGUARD_GROUPS = {
    "Administrative": { icon: Shield, color: "text-blue-600", bg: "bg-blue-50" },
    "Physical": { icon: Server, color: "text-purple-600", bg: "bg-purple-50" },
    "Technical": { icon: Lock, color: "text-teal-600", bg: "bg-teal-50" }
};

const FrameworkDetail_HIPAA = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const [framework, setFramework] = useState(null);
    const [controls, setControls] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState("");
    const [selectedSafeguard, setSelectedSafeguard] = useState("All");

    useEffect(() => {
        fetchData();
    }, [id]);

    const fetchData = async () => {
        try {
            const token = localStorage.getItem('token');
            const headers = { Authorization: `Bearer ${token}` };

            const [fwRes, ctrlRes] = await Promise.all([
                axios.get(`${API_URL}/frameworks/${id}`, { headers }),
                axios.get(`${API_URL}/controls/`, { headers })
            ]);

            setFramework(fwRes.data);

            // FILTER & PARSE CONTROLS
            const fwControls = ctrlRes.data.filter(c => c.framework_id === parseInt(id));

            // Enrich with HIPAA Metadata parsed from Title
            // Format: "164.308(a)(1)(i) ... (Required)"
            const enriched = fwControls.map(c => {
                let implementationSpec = "Required"; // Default
                if (c.title.includes("(Addressable)")) implementationSpec = "Addressable";

                let safeguard = "Administrative";
                if (c.title.includes("164.310")) safeguard = "Physical";
                if (c.title.includes("164.312")) safeguard = "Technical";

                return { ...c, implementationSpec, safeguard };
            });

            setControls(enriched);
            setLoading(false);
        } catch (error) {
            console.error("Error fetching HIPAA data:", error);
            setLoading(false);
        }
    };

    const handleBack = () => navigate('/dashboard');

    // FILTERING
    const filteredControls = controls.filter(c => {
        const matchesSearch = c.title.toLowerCase().includes(searchTerm.toLowerCase());
        const matchesGroup = selectedSafeguard === "All" || c.safeguard === selectedSafeguard;
        return matchesSearch && matchesGroup;
    });

    if (loading) return <div className="p-10 text-center text-gray-400">Loading HIPAA Protocols...</div>;

    return (
        <div className="min-h-screen bg-gray-50 pb-20 font-sans">
            {/* HEADER */}
            <div className="bg-white border-b border-gray-200 sticky top-0 z-10 shadow-sm">
                <div className="max-w-7xl mx-auto px-6 py-4">
                    <div className="flex items-center gap-4 mb-4">
                        <button onClick={handleBack} className="p-2 hover:bg-gray-100 rounded-lg text-gray-500 transition-colors">
                            <ArrowLeft className="w-5 h-5" />
                        </button>
                        <div>
                            <div className="flex items-center gap-3">
                                <h1 className="text-2xl font-bold text-gray-900">{framework?.name}</h1>
                                <span className="px-3 py-1 bg-teal-100 text-teal-700 text-xs font-bold rounded-full border border-teal-200">
                                    45 CFR Part 164
                                </span>
                            </div>
                            <p className="text-sm text-gray-500 mt-1">Security Standards for the Protection of Electronic Protected Health Information</p>
                        </div>
                    </div>

                    {/* FILTERS */}
                    <div className="flex flex-col md:flex-row gap-4 justify-between items-center">
                        <div className="flex gap-2">
                            {["All", "Administrative", "Physical", "Technical"].map(mode => (
                                <button
                                    key={mode}
                                    onClick={() => setSelectedSafeguard(mode)}
                                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${selectedSafeguard === mode
                                            ? 'bg-gray-900 text-white shadow-md'
                                            : 'bg-white border border-gray-200 text-gray-600 hover:bg-gray-50'
                                        }`}
                                >
                                    {mode}
                                </button>
                            ))}
                        </div>
                        <div className="relative w-full md:w-64">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                            <input
                                type="text"
                                placeholder="Search regulations..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent outline-none text-sm"
                            />
                        </div>
                    </div>
                </div>
            </div>

            {/* MAIN CONTENT */}
            <div className="max-w-7xl mx-auto px-6 py-8">
                <div className="grid gap-4">
                    {filteredControls.map(c => (
                        <div key={c.id} className="bg-white rounded-xl border border-gray-200 p-6 hover:shadow-md transition-shadow group">
                            <div className="flex justify-between items-start mb-4">
                                <div className="flex gap-3">
                                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center shrink-0 ${SAFEGUARD_GROUPS[c.safeguard].bg} ${SAFEGUARD_GROUPS[c.safeguard].color}`}>
                                        {React.createElement(SAFEGUARD_GROUPS[c.safeguard].icon, { className: "w-5 h-5" })}
                                    </div>
                                    <div>
                                        <div className="flex items-center gap-2 mb-1">
                                            <span className={`px-2 py-0.5 text-xs font-bold rounded border ${STATUS_COLORS[c.implementationSpec]}`}>
                                                {c.implementationSpec.toUpperCase()}
                                            </span>
                                            <span className="text-xs font-mono text-gray-400">{c.control_id}</span>
                                        </div>
                                        <h3 className="text-lg font-bold text-gray-900 group-hover:text-teal-700 transition-colors">
                                            {c.title}
                                        </h3>
                                        <p className="text-sm text-gray-500 mt-1">{c.description}</p>
                                    </div>
                                </div>
                                <div className="flex gap-2">
                                    <button className="px-3 py-1.5 text-sm font-medium text-gray-600 bg-gray-50 rounded-lg border border-gray-200 hover:bg-white hover:border-gray-300 transition-all">
                                        Upload Evidence
                                    </button>
                                </div>
                            </div>
                        </div>
                    ))}
                    {filteredControls.length === 0 && (
                        <div className="text-center py-20 bg-white rounded-xl border border-dashed border-gray-300">
                            <Shield className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                            <p className="text-gray-500 font-medium">No safeguards found matching your filters.</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default FrameworkDetail_HIPAA;
