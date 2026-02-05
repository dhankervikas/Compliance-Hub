
import React from 'react';
import {
    X, CheckCircle, AlertTriangle,
    Terminal, ArrowRight, Shield, Download
} from 'lucide-react';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';

const LogDetailModal = ({ log, onClose }) => {
    if (!log) return null;

    const exportToPDF = () => {
        const doc = new jsPDF();

        // Header
        doc.setFillColor(15, 23, 42); // Slate 900
        doc.rect(0, 0, 210, 40, 'F');
        doc.setTextColor(255, 255, 255);
        doc.setFontSize(22);
        doc.text("Compliance Evidence Record", 14, 25);
        doc.setFontSize(10);
        doc.text(`Generated: ${new Date().toLocaleString()}`, 14, 35);

        // Metadata
        doc.setTextColor(0, 0, 0);
        doc.setFontSize(14);
        doc.text("1. Verification Metadata", 14, 50);

        autoTable(doc, {
            startY: 55,
            head: [['Field', 'Value']],
            body: [
                ['Execution ID', log.execution_id || 'N/A'],
                ['Control Mapping', log.control],
                ['Resource', log.resource],
                ['Status', log.status],
                ['Source', log.context?.source || 'Unknown']
            ],
            theme: 'grid',
            headStyles: { fillColor: [51, 65, 85] }
        });

        // Raw Evidence
        let currentY = doc.lastAutoTable.finalY + 15;
        doc.setFontSize(14);
        doc.text("2. Raw Evidence Payload", 14, currentY);

        const rawJson = JSON.stringify(log.raw_data || {}, null, 2);
        const splitText = doc.splitTextToSize(rawJson, 180);

        doc.setFont("courier", "normal");
        doc.setFontSize(10);
        doc.setFillColor(248, 250, 252); // Slate 50
        doc.rect(14, currentY + 5, 182, splitText.length * 5 + 10, 'F');
        doc.text(splitText, 18, currentY + 12);

        // Verification Signature based on Status
        currentY += splitText.length * 5 + 30;
        doc.setFont("helvetica", "bold");
        doc.setFontSize(12);
        doc.text("System Verification Signature:", 14, currentY);
        doc.setFont("helvetica", "normal");
        doc.text(
            log.status === 'PASS'
                ? "VERIFIED: System confirms configuration matches policy requirements."
                : "FAILED: Configuration deviate from expected state. Remediation required.",
            14, currentY + 8
        );

        doc.save(`evidence_${log.control}_${log.status}.pdf`);
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm animate-fade-in p-4">
            <div className="bg-white w-full max-w-4xl rounded-2xl shadow-2xl overflow-hidden max-h-[90vh] flex flex-col">

                {/* HEADER */}
                <div className="bg-slate-900 p-6 flex items-start justify-between">
                    <div className="flex items-center gap-4">
                        <div className={`p-3 rounded-xl ${log.status === 'PASS' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                            {log.status === 'PASS' ? <CheckCircle size={32} /> : <AlertTriangle size={32} />}
                        </div>
                        <div>
                            <div className="flex items-center gap-2 mb-1">
                                <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${log.status === 'PASS' ? 'bg-green-900 text-green-400' : 'bg-red-900 text-red-400'}`}>
                                    {log.status}
                                </span>
                                <span className="text-slate-400 text-xs font-mono">{log.execution_id}</span>
                            </div>
                            <h2 className="text-xl font-bold text-white">{log.title || log.details}</h2>
                            <p className="text-slate-400 text-sm mt-1">Mapped to Control: <span className="text-white font-mono">{log.control}</span></p>
                        </div>
                    </div>
                    <button onClick={onClose} className="text-slate-400 hover:text-white transition-colors">
                        <X size={24} />
                    </button>
                </div>

                {/* SCROLLABLE BODY */}
                <div className="flex-1 overflow-y-auto bg-slate-50 p-6 space-y-6">

                    {/* SECTION A: CONTEXT */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        {log.context && Object.entries(log.context).map(([key, value]) => (
                            <div key={key} className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                                <label className="text-xs font-bold text-slate-400 uppercase tracking-wider block mb-1">{key.replace('_', ' ')}</label>
                                <span className="text-slate-700 font-medium break-all">{value}</span>
                            </div>
                        ))}
                    </div>

                    {/* SECTION B: RAW EVIDENCE */}
                    <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
                        <div className="bg-slate-100 px-6 py-3 border-b border-slate-200 flex justify-between items-center">
                            <h3 className="flex items-center gap-2 font-bold text-slate-700">
                                <Terminal size={18} /> Raw API Result
                            </h3>
                            <button
                                onClick={exportToPDF}
                                className="text-xs font-bold flex items-center gap-1.5 bg-blue-600 text-white px-3 py-1.5 rounded-lg hover:bg-blue-700 transition-colors"
                            >
                                <Download size={14} /> Export Evidence
                            </button>
                        </div>
                        <div className="p-0 overflow-x-auto">
                            <pre className="text-xs font-mono text-slate-600 p-6 language-json">
                                {JSON.stringify(log.raw_data, null, 2) || "// No raw data available"}
                            </pre>
                        </div>
                    </div>

                    {/* SECTION C: REMEDIATION (Only if FAIL) */}
                    {log.status === 'FAIL' && log.remediation && (
                        <div className="bg-red-50 rounded-xl border border-red-100 shadow-sm overflow-hidden p-6">
                            <h3 className="flex items-center gap-2 font-bold text-red-800 mb-4">
                                <Shield size={18} /> Remediation Steps
                            </h3>
                            <div className="prose prose-sm text-red-900/80">
                                <pre className="whitespace-pre-wrap font-sans text-sm">
                                    {log.remediation}
                                </pre>
                            </div>
                            <div className="mt-6 flex justify-end">
                                <button className="flex items-center gap-2 text-red-700 font-bold text-sm bg-white px-4 py-2 rounded-lg border border-red-200 hover:bg-red-100 transition-colors shadow-sm">
                                    Review Docs <ArrowRight size={16} />
                                </button>
                            </div>
                        </div>
                    )}

                </div>
            </div>
        </div>
    );
};

export default LogDetailModal;
