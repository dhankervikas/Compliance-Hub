import React, { useState, useEffect } from 'react';
import axios from '../services/api';
import { FileSpreadsheet, FileText, Shield, CheckCircle, XCircle, Settings as SettingsIcon, Eye, Filter, Check } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useEntitlements } from '../contexts/EntitlementContext';
import { generateSoA } from '../utils/soaGenerator';
import SoAEditor from './SoAEditor';

const StatementOfApplicability = () => {
    const [activeTab, setActiveTab] = useState('preview'); // 'preview' | 'config'
    const [controls, setControls] = useState([]);
    const [frameworks, setFrameworks] = useState([]);
    const [selectedFrameworks, setSelectedFrameworks] = useState([]); // IDs
    const [loading, setLoading] = useState(true);
    const [generating, setGenerating] = useState(false);
    const [isScopeOpen, setIsScopeOpen] = useState(false);

    const [error, setError] = useState(null);

    const { entitlements, loading: loadingEntitlements } = useEntitlements();
    const token = localStorage.getItem('token');

    // Initial Load
    useEffect(() => {
        if (!loadingEntitlements && entitlements) {
            fetchFrameworks();
        }
    }, [loadingEntitlements, entitlements]);

    // Re-fetch when selection changes or tab switches
    useEffect(() => {
        if (selectedFrameworks.length > 0) {
            fetchData();
        } else if (!loading && frameworks.length > 0) {
            // Ensure one is selected if frameworks exist
            const defaultFw = frameworks.find(f => f.code === 'ISO27001') || frameworks[0];
            if (defaultFw && !selectedFrameworks.includes(defaultFw.id)) {
                setSelectedFrameworks([defaultFw.id]);
            }
        }
    }, [activeTab, selectedFrameworks, frameworks]);

    const fetchFrameworks = async () => {
        setError(null);
        try {
            // STRICT FILTERING: Use Entitlements instead of direct API
            // const res = await axios.get('/frameworks/');
            // setFrameworks(res.data);

            const activeFw = entitlements.frameworks.filter(f => f.is_active);
            setFrameworks(activeFw);

            if (activeFw.length > 0) {
                // Try to keep existing selection or default
                if (selectedFrameworks.length === 0) {
                    const defaultFw = activeFw.find(f => f.code === 'ISO27001') || activeFw[0];
                    setSelectedFrameworks([defaultFw.id]);
                }
            } else {
                setLoading(false);
                setError("No authorized frameworks found for this tenant.");
            }
        } catch (err) {
            console.error("Failed to load frameworks", err);
            setLoading(false);
            const msg = err.response?.data?.detail || err.message || "Failed to load frameworks";
            setError(`Error: ${msg}`);
        }
    };

    const fetchData = async () => {
        setLoading(true);
        setError(null);
        try {
            // Build Query Params for multiple IDs
            const params = new URLSearchParams();
            selectedFrameworks.forEach(id => params.append('framework_ids', id));

            const res = await axios.get(`/controls/?${params.toString()}`);

            // Filter for Annex A (ISO 27001) OR ISO 42001 (All controls or just Annex? User wants SOA)
            // Filter logic
            console.log("Controls fetched:", res.data.length);

            // Refined Filter: STRICTLY Annex A for ISO 27001
            let soaControls = res.data.filter(c => {
                // ISO 27001 (Framework ID 1): Only allow "A.*" controls
                if (c.framework_id === 1) {
                    return c.control_id.startsWith('A.');
                }

                // ISO 42001: Include all (or refince to Annex A if needed later)
                if (c.control_id.includes('ISO42001')) {
                    return true;
                }

                // Global Safety Check: Exclude Management Clauses (4.1 - 10.2) if they slipped through without framework_id
                if (/^([4-9]|10)\./.test(c.control_id) && !c.control_id.startsWith('A.')) {
                    return false;
                }

                // Fallback for other standards (SOC2, HIPAA, NIST)
                return true;
            });

            console.log("Filtered SoA Controls:", soaControls.length);

            // Safety net: If filtering removed everything but we had data, restore key components
            if (soaControls.length === 0 && res.data.length > 0) {
                console.warn("Filter removed all controls. Restoring full set.");
                soaControls = res.data;
            }

            // Deduplicate
            const uniqueControls = Array.from(new Map(soaControls.map(item => [item.control_id, item])).values());

            // Smart Sort
            uniqueControls.sort((a, b) =>
                a.control_id.localeCompare(b.control_id, undefined, { numeric: true, sensitivity: 'base' })
            );

            setControls(uniqueControls);
            setLoading(false);
        } catch (err) {
            console.error(err);
            setLoading(false);
        }
    };

    const handleDownloadExcel = async () => {
        setGenerating(true);
        try {
            // Compute Dynamic Scope Name
            const selectedNames = frameworks
                .filter(f => selectedFrameworks.includes(f.id))
                .map(f => f.code || f.name)
                .join(" & ");

            const scopeName = selectedNames || "ISO 27001:2022";

            // Pass the FULL controls list AND FRAMEWORKS list to the generator
            // This enables the generator to lookup names for IDs
            const buffer = await generateSoA(scopeName, controls, [], frameworks);

            const blob = new Blob([buffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `SoA_${scopeName.replace(/[^a-z0-9]/gi, '_')}_${new Date().toISOString().split('T')[0]}.xlsx`);
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (err) {
            console.error(err);
            alert("Export Failed");
        } finally {
            setGenerating(false);
        }
    };

    const toggleScope = () => setIsScopeOpen(!isScopeOpen);

    if (loading) return <div className="p-12 text-center text-gray-500">Loading Statement of Applicability...</div>;

    const applicableCount = controls.filter(c => c.is_applicable !== false).length;
    const excludedCount = controls.length - applicableCount;

    return (
        <div className="p-8 bg-gray-50 min-h-screen">
            <div className="max-w-7xl mx-auto">
                {/* DEBUG PANEL - REMOVE IN PROD */}
                <div className="mb-4 p-4 bg-gray-800 text-green-400 font-mono text-xs rounded-lg overflow-x-auto">
                    <h4 className="font-bold underline mb-2">DIAGNOSTICS</h4>
                    <div>Tenant Token: {token ? "Present" : "MISSING"}</div>
                    <div>Frameworks Loaded: {frameworks.length}</div>
                    <div>Selected IDs: {JSON.stringify(selectedFrameworks)}</div>
                    <div>Loading: {loading ? "Yes" : "No"}</div>
                    <div>Controls Loaded: {controls.length}</div>
                    <div>Error State: {error || "None"}</div>
                </div>

                {error && (
                    <div className="mb-6 p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg flex items-center gap-3">
                        <XCircle size={20} />
                        <div>
                            <div className="font-bold">Error Loading Data</div>
                            <div>{error}</div>
                        </div>
                    </div>
                )}

                <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
                    <div>
                        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                            <Shield className="text-blue-600" />
                            Statement of Applicability
                        </h1>
                        <p className="text-gray-500">Applicability Assessment & Justification</p>
                    </div>

                    <div className="flex flex-wrap gap-3 items-center">
                        {/* Scope Selector */}
                        <div className="relative">
                            <button
                                onClick={toggleScope}
                                className={`bg-white border text-gray-700 px-4 py-2 rounded-lg font-bold flex items-center gap-2 shadow-sm transition-colors ${isScopeOpen ? 'border-blue-500 ring-2 ring-blue-100' : 'border-gray-300 hover:bg-gray-50'}`}
                            >
                                <Filter size={16} className="text-gray-500" />
                                Scope: {selectedFrameworks.length} Standards
                                <div className="bg-gray-200 text-gray-600 text-xs px-1.5 rounded-full ml-1">{isScopeOpen ? '▲' : '▼'}</div>
                            </button>

                            {/* Dropdown Menu */}
                            {isScopeOpen && (
                                <div className="absolute right-0 top-full mt-2 w-72 bg-white border border-gray-200 rounded-xl shadow-xl z-50 p-2 animate-fade-in-down">
                                    <div className="flex justify-between items-center mb-2 px-2">
                                        <div className="text-xs font-bold text-gray-400 uppercase tracking-wider">Select Frameworks</div>
                                        <button onClick={() => setIsScopeOpen(false)} className="text-gray-400 hover:text-gray-600">
                                            <XCircle size={14} />
                                        </button>
                                    </div>
                                    <div className="max-h-64 overflow-y-auto space-y-1">
                                        {frameworks.map(fw => {
                                            const isSelected = selectedFrameworks.includes(fw.id);
                                            return (
                                                <div
                                                    key={fw.id}
                                                    onClick={() => {
                                                        if (isSelected) {
                                                            setSelectedFrameworks(prev => prev.filter(id => id !== fw.id));
                                                        } else {
                                                            setSelectedFrameworks(prev => [...prev, fw.id]);
                                                        }
                                                    }}
                                                    className={`flex items-center gap-3 p-2.5 rounded-lg cursor-pointer transition-colors border ${isSelected ? 'bg-blue-50 border-blue-200 text-blue-700' : 'border-transparent hover:bg-gray-50 text-gray-700'}`}
                                                >
                                                    <div className={`w-5 h-5 rounded flex items-center justify-center border ${isSelected ? 'bg-blue-600 border-blue-600' : 'bg-white border-gray-300'}`}>
                                                        {isSelected && <Check size={14} className="text-white" />}
                                                    </div>
                                                    <span className="font-medium text-sm">{fw.name}</span>
                                                </div>
                                            );
                                        })}
                                        {frameworks.length === 0 && (
                                            <div className="p-4 text-center text-gray-400 text-xs italic">
                                                No frameworks available
                                            </div>
                                        )}
                                    </div>
                                    <div className="mt-2 pt-2 border-t border-gray-100 px-2 text-xs text-center text-gray-400">
                                        Click outside to close
                                    </div>
                                </div>
                            )}
                        </div>

                        <button className="bg-white border text-gray-700 px-4 py-2 rounded-lg font-bold flex items-center gap-2 hover:bg-gray-50 border-gray-300">
                            <FileText size={16} />
                            PDF
                        </button>
                        <button
                            onClick={handleDownloadExcel}
                            disabled={generating}
                            className="bg-green-600 text-white px-4 py-2 rounded-lg font-bold flex items-center gap-2 hover:bg-green-700 shadow-lg disabled:opacity-70"
                        >
                            <FileSpreadsheet size={16} />
                            {generating ? "Generating..." : "Export SoA (.xlsx)"}
                        </button>
                    </div>
                </div>

                {/* TAB NAVIGATION */}
                <div className="flex gap-4 border-b border-gray-200 mb-6">
                    <button
                        onClick={() => setActiveTab('preview')}
                        className={`pb-3 px-4 font-bold text-sm flex items-center gap-2 border-b-2 transition-colors ${activeTab === 'preview' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'}`}
                    >
                        <Eye size={16} /> SoA Preview (Live)
                    </button>
                    <button
                        onClick={() => setActiveTab('config')}
                        className={`pb-3 px-4 font-bold text-sm flex items-center gap-2 border-b-2 transition-colors ${activeTab === 'config' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700'}`}
                    >
                        <SettingsIcon size={16} /> Configuration & Scoping
                    </button>
                </div>

                {activeTab === 'config' ? (
                    <SoAEditor controls={controls} />
                ) : (
                    <>
                        {/* Summary Cards */}
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                                <div className="text-gray-500 text-xs font-bold uppercase mb-2">Total Controls</div>
                                <div className="text-3xl font-bold text-gray-900">{controls.length}</div>
                                <div className="text-xs text-gray-400 mt-1">ISO 27001:2022 Annex A</div>
                            </div>
                            <div className="bg-white p-6 rounded-xl shadow-sm border border-green-200 bg-green-50/50">
                                <div className="text-green-600 text-xs font-bold uppercase mb-2">Applicable</div>
                                <div className="text-3xl font-bold text-green-700">{applicableCount}</div>
                                <div className="text-xs text-green-600/70 mt-1">In Scope for Audit</div>
                            </div>
                            <div className="bg-white p-6 rounded-xl shadow-sm border border-red-200 bg-red-50/50">
                                <div className="text-red-600 text-xs font-bold uppercase mb-2">Excluded</div>
                                <div className="text-3xl font-bold text-red-700">{excludedCount}</div>
                                <div className="text-xs text-red-600/70 mt-1">Justification Required</div>
                            </div>
                        </div>

                        {/* Live SoA Table */}
                        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                            <div className="bg-gray-50 px-6 py-4 border-b border-gray-200 flex justify-between items-center">
                                <h3 className="font-bold text-gray-700">Preview: Annex A Applicability Matrix</h3>
                                <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded font-bold">LIVE PREVIEW</span>
                            </div>
                            <div className="overflow-x-auto">
                                <table className="w-full text-sm text-left">
                                    <thead className="text-xs text-gray-500 uppercase bg-gray-50 border-b">
                                        <tr>
                                            <th className="px-6 py-3 w-24">ID</th>
                                            <th className="px-6 py-3 w-1/4">Control Name</th>
                                            <th className="px-6 py-3 w-32 text-center">Applicability</th>
                                            <th className="px-6 py-3">Justification Category & Detail</th>
                                            <th className="px-6 py-3 w-48">Method</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-gray-100">
                                        {/* GROUPING LOGIC */}
                                        {(() => {
                                            if (controls.length === 0) return (
                                                <tr>
                                                    <td colSpan="5" className="px-6 py-12 text-center text-gray-400">
                                                        No controls found in scope. Please select frameworks in the filter above.
                                                    </td>
                                                </tr>
                                            );

                                            // 1. Group Controls
                                            const grouped = {};
                                            controls.forEach(ctrl => {
                                                let id = ctrl.framework_id;
                                                if (!id) {
                                                    if (ctrl.control_id.startsWith('A.')) id = 1;
                                                    else if (ctrl.control_id.includes('ISO42001')) id = 2;
                                                    else id = "other";
                                                }
                                                if (!grouped[id]) grouped[id] = [];
                                                grouped[id].push(ctrl);
                                            });

                                            // 2. Render Groups
                                            return Object.keys(grouped).sort().map(fwId => {
                                                // Resolve Internal Name
                                                let sectionName = "Other Standards";
                                                if (frameworks && frameworks.length > 0) {
                                                    const fw = frameworks.find(f => String(f.id) === String(fwId));
                                                    if (fw) sectionName = fw.name;
                                                }
                                                // Fallback
                                                if (sectionName === "Other Standards") {
                                                    if (String(fwId) === "1") sectionName = "ISO/IEC 27001:2022";
                                                    if (String(fwId) === "2") sectionName = "ISO/IEC 42001:2023";
                                                }

                                                return (
                                                    <React.Fragment key={fwId}>
                                                        {/* Section Header */}
                                                        <tr className="bg-gray-100 border-y border-gray-200">
                                                            <td colSpan="5" className="px-6 py-2 font-bold text-gray-800 uppercase tracking-wide text-xs">
                                                                {sectionName}
                                                            </td>
                                                        </tr>

                                                        {/* Controls in Group */}
                                                        {grouped[fwId].map((ctrl, i) => {
                                                            // Display ID Cleanup
                                                            let displayId = ctrl.control_id;
                                                            if (String(fwId) === "2" || sectionName.includes("42001")) {
                                                                displayId = displayId.replace("ISO42001-", "");
                                                            }

                                                            return (
                                                                <tr key={`${fwId}-${i}`} className={`hover:bg-gray-50 ${ctrl.is_applicable === false ? 'bg-red-50/30' : ''}`}>
                                                                    <td className="px-6 py-3 font-mono text-gray-500 font-bold">{displayId}</td>
                                                                    <td className="px-6 py-3 font-medium text-gray-900">{ctrl.title}</td>
                                                                    <td className="px-6 py-3 text-center">
                                                                        {ctrl.is_applicable !== false ? (
                                                                            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-bold bg-green-100 text-green-700">
                                                                                <CheckCircle size={10} /> YES
                                                                            </span>
                                                                        ) : (
                                                                            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-bold bg-red-100 text-red-700">
                                                                                <XCircle size={10} /> NO
                                                                            </span>
                                                                        )}
                                                                    </td>
                                                                    <td className="px-6 py-3 text-gray-600">
                                                                        {ctrl.justification_reason && (
                                                                            <div className="text-xs font-bold uppercase text-gray-500 mb-1">
                                                                                {ctrl.justification_reason}
                                                                            </div>
                                                                        )}
                                                                        <div className="italic">
                                                                            {ctrl.justification || (ctrl.is_applicable !== false ? "Standard requirement included in scope." : <span className="text-red-500 font-bold">MISSING JUSTIFICATION</span>)}
                                                                        </div>
                                                                    </td>
                                                                    <td className="px-6 py-3 text-gray-600">
                                                                        {ctrl.implementation_method || "N/A"}
                                                                    </td>
                                                                </tr>
                                                            );
                                                        })}
                                                    </React.Fragment>
                                                );
                                            });
                                        })()}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </>
                )}
            </div>
        </div>
    );
};

export default StatementOfApplicability;
