import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { FileSpreadsheet, FileText, Shield, CheckCircle, XCircle, Settings as SettingsIcon, Eye } from 'lucide-react';
import config from '../config';
import { generateSoA } from '../utils/soaGenerator';
import SoAEditor from './SoAEditor';

const API_URL = config.API_BASE_URL;

const StatementOfApplicability = () => {
    const [activeTab, setActiveTab] = useState('preview'); // 'preview' | 'config'
    const [controls, setControls] = useState([]);
    const [loading, setLoading] = useState(true);
    const [generating, setGenerating] = useState(false);

    // Re-fetch when tab switches to preview to get latest changes
    useEffect(() => {
        if (activeTab === 'preview') {
            fetchData();
        }
    }, [activeTab]);

    const fetchData = async () => {
        try {
            const token = localStorage.getItem('token');
            const res = await axios.get(`${API_URL}/controls?framework_id=1`, {
                headers: { Authorization: `Bearer ${token}` }
            });

            // Filter for Annex A controls for the SoA
            let annexControls = res.data.filter(c => c.control_id.startsWith('A.'));

            // Deduplicate (Defensive Fix for 94 vs 93 issue)
            const uniqueControls = Array.from(new Map(annexControls.map(item => [item.control_id, item])).values());

            // Natural Sort (Fix for "not in order" issue: A.5.2 vs A.5.10)
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
            // Pass the FULL controls list (with user's is_applicable choice) to the generator
            const buffer = await generateSoA("ISO 27001:2022", controls, []); // Empty evidence list for now, or fetch if needed

            const blob = new Blob([buffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `SoA_ISO27001_${new Date().toISOString().split('T')[0]}.xlsx`);
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

    if (loading) return <div className="p-12 text-center text-gray-500">Loading Statement of Applicability...</div>;

    const applicableCount = controls.filter(c => c.is_applicable !== false).length;
    const excludedCount = controls.length - applicableCount;

    return (
        <div className="p-8 bg-gray-50 min-h-screen">
            <div className="max-w-7xl mx-auto">
                <div className="flex justify-between items-center mb-8">
                    <div>
                        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                            <Shield className="text-blue-600" />
                            Statement of Applicability
                        </h1>
                        <p className="text-gray-500">ISO 27001 Clause 6.1.3d Implementation</p>
                    </div>
                    <div className="flex gap-3">
                        <button className="bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-lg font-bold flex items-center gap-2 hover:bg-gray-50">
                            <FileText size={16} />
                            Executive Summary (PDF)
                        </button>
                        <button
                            onClick={handleDownloadExcel}
                            disabled={generating}
                            className="bg-green-600 text-white px-4 py-2 rounded-lg font-bold flex items-center gap-2 hover:bg-green-700 shadow-lg disabled:opacity-70"
                        >
                            <FileSpreadsheet size={16} />
                            {generating ? "Generating..." : "Download SoA (.xlsx)"}
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
                    <SoAEditor />
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
                                        {controls.map((ctrl, i) => (
                                            <tr key={i} className={`hover:bg-gray-50 ${ctrl.is_applicable === false ? 'bg-red-50/30' : ''}`}>
                                                <td className="px-6 py-3 font-mono text-gray-500 font-bold">{ctrl.control_id}</td>
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
                                        ))}
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
