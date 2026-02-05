
import React, { useState, useEffect } from 'react';
import axios from '../services/api';
import {
    Save,
    X,
    Wand2,
    CheckCircle,
    Loader2
} from 'lucide-react';
import { useEditor, EditorContent, BubbleMenu } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import { Table } from '@tiptap/extension-table';
import { TableRow } from '@tiptap/extension-table-row';
import { TableCell } from '@tiptap/extension-table-cell';
import { TableHeader } from '@tiptap/extension-table-header';
import { Image } from '@tiptap/extension-image';
import { TextAlign } from '@tiptap/extension-text-align';
import { Underline } from '@tiptap/extension-underline';
import EditorToolbar from './EditorToolbar';
import { marked } from 'marked';
import TurndownService from 'turndown';
import { gfm } from 'turndown-plugin-gfm';

// Initialize Markdown Parsers
const turndownService = new TurndownService({
    headingStyle: 'atx',
    codeBlockStyle: 'fenced'
});
turndownService.use(gfm); // Use GitHub Flavored Markdown for Tables

const PolicyEditor = ({ policy, masterContent, onRestore, onClose, onSave, readOnly = false }) => {
    const [isSaving, setIsSaving] = useState(false);
    const [isGenerating, setIsGenerating] = useState(false);
    const [rewriteLoading, setRewriteLoading] = useState(false);
    const [companyName, setCompanyName] = useState("AssuRisk");
    const [showSplitView, setShowSplitView] = useState(!!masterContent); // Default to Split if master exists

    // ... (rest of imports and setup)

    // Fetch Company Name
    useEffect(() => {
        const fetchSettings = async () => {
            try {
                const res = await axios.get('/settings/org_profile');
                if (res.data?.content?.legal_name) {
                    setCompanyName(res.data.content.legal_name);
                }
            } catch (err) {
                console.warn("Could not fetch company settings", err);
            }
        };
        fetchSettings();
    }, []);

    // TipTap Editor Setup
    const editor = useEditor({
        extensions: [
            StarterKit,
            Table.configure({
                resizable: true,
                HTMLAttributes: {
                    class: 'border-collapse table-auto w-full border border-black mb-4',
                },
            }),
            TableRow,
            TableHeader.configure({
                HTMLAttributes: {
                    class: 'border border-black bg-gray-100 p-2 font-bold text-left',
                },
            }),
            TableCell.configure({
                HTMLAttributes: {
                    class: 'border border-black p-2',
                },
            }),
            Image,
            Underline,
            TextAlign.configure({
                types: ['heading', 'paragraph'],
            }),
        ],
        editorProps: {
            attributes: {
                class: 'prose max-w-none focus:outline-none min-h-[250mm] font-serif',
            },
        },
        content: '', // Initial content loaded via useEffect
        editable: !readOnly,
    });

    // Load Content (Markdown -> HTML)
    useEffect(() => {
        if (editor && policy.content) {
            marked.use({ gfm: true, breaks: true });
            try {
                const html = marked.parse(policy.content);
                editor.commands.setContent(html);
            } catch (e) {
                console.error("Markdown parsing error:", e);
                editor.commands.setContent(`< p > ${policy.content}</p > `);
            }
        }
    }, [editor, policy.content]);

    const handleSave = async (status = null) => {
        if (!editor || readOnly) return;
        setIsSaving(true);
        try {
            const html = editor.getHTML();
            const markdown = turndownService.turndown(html);

            const updates = {
                content: markdown,
                ...(status && { status })
            };

            await axios.put(`/ policies / ${policy.id} `, updates);

            if (status === 'Approved') {
                await axios.post(`/ policies / ${policy.id}/approve`);
            }

            onSave();
        } catch (error) {
            console.error("Failed to save policy", error);
            alert("Failed to save changes.");
        } finally {
            setIsSaving(false);
        }
    };

    const handleAiGenerate = async () => {
        if (readOnly) return;
        setIsGenerating(true);
        try {
            const res = await axios.post(`/policies/${policy.id}/generate`, {
                title: policy.name,
                context: policy.description || "Standard ISO 27001 Policy"
            });
            editor.commands.setContent(marked.parse(res.data.content));
        } catch (error) {
            console.error("AI Generation failed", error);
            alert("AI Generation failed. Please try again.");
        } finally {
            setIsGenerating(false);
        }
    };

    const handleAiRewrite = async (instruction) => {
        if (!editor) return;
        const { from, to } = editor.state.selection;
        const text = editor.state.doc.textBetween(from, to, ' ');

        if (!text || text.length < 5) {
            alert("Please select at least 5 characters to rewrite.");
            return;
        }

        setRewriteLoading(true);
        try {
            const res = await axios.post(`/policies/${policy.id}/rewrite`, {
                text: text,
                instruction: instruction
            });

            const newText = res.data.content;
            editor.commands.insertContent(newText);
        } catch (error) {
            console.error("Rewrite failed", error);
            alert("AI Rewrite failed.");
        } finally {
            setRewriteLoading(false);
        }
    };

    // Style cleanup for printing
    useEffect(() => {
        const style = document.createElement('style');
        style.innerHTML = `
            .ProseMirror table { border-collapse: collapse; width: 100%; margin: 1em 0; }
            .ProseMirror td, .ProseMirror th { border: 1px solid #000; padding: 8px; vertical-align: top; }
            .ProseMirror th { background-color: #f3f4f6; font-weight: bold; }
            @media print {
                @page { margin: 2cm; }
                .policy-toolbar, .policy-sidebar, .policy-header, .master-ref-pane { display: none !important; }
                .policy-page { box-shadow: none !important; border: none !important; width: 100% !important; margin: 0 !important; }
            }
        `;
        document.head.appendChild(style);
        return () => document.head.removeChild(style);
    }, []);

    // Compliance Check Logic
    const [complianceStatus, setComplianceStatus] = useState({});

    useEffect(() => {
        if (!editor) return;
        const checkCompliance = () => {
            const content = editor.getText();
            const checks = {
                "Purpose": content.includes("Purpose"),
                "Scope": content.includes("Scope"),
                "Roles": content.includes("Roles"),
                "Policy Statements": content.includes("Policy Statements"),
            };
            setComplianceStatus(checks);
        };
        checkCompliance();
        editor.on('update', checkCompliance);
        return () => { editor.off('update', checkCompliance); };
    }, [editor]);

    return (
        <div className="fixed inset-0 bg-gray-100 z-50 flex flex-col font-sans animate-in fade-in duration-200">
            {/* Top Navigation */}
            <div className="policy-header border-b border-gray-200 px-6 py-4 flex items-center justify-between bg-white shadow-sm z-20">
                <div className="flex items-center gap-4">
                    <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-full text-gray-500 transition-colors">
                        <X className="w-6 h-6" />
                    </button>
                    <div>
                        <h1 className="text-xl font-bold text-gray-900 flex items-center gap-2 font-serif">
                            {policy.name}
                            <span className={`text-xs px-2 py-0.5 rounded-full border ${policy.status === 'Approved' ? 'bg-green-50 border-green-200 text-green-700' :
                                policy.status === 'Draft' ? 'bg-gray-100 border-gray-200 text-gray-600' : 'bg-amber-50 border-amber-200 text-amber-700'
                                }`}>{policy.status}</span>
                        </h1>
                        <p className="text-sm text-gray-500">ver {policy.version} | Last Updated: {new Date(policy.updated_at || Date.now()).toLocaleDateString()}</p>
                    </div>
                </div>

                <div className="flex items-center gap-3">
                    {/* Split View Toggle */}
                    {masterContent && (
                        <div className="flex bg-gray-100 rounded-lg p-1 mr-4">
                            <button
                                onClick={() => setShowSplitView(false)}
                                className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${!showSplitView ? 'bg-white shadow text-gray-900' : 'text-gray-500 hover:text-gray-900'}`}
                            >
                                Editor Only
                            </button>
                            <button
                                onClick={() => setShowSplitView(true)}
                                className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${showSplitView ? 'bg-white shadow text-gray-900' : 'text-gray-500 hover:text-gray-900'}`}
                            >
                                Split View
                            </button>
                        </div>
                    )}

                    {!readOnly && (
                        <>
                            {/* Restore Button */}
                            {masterContent && onRestore && (
                                <button
                                    onClick={onRestore}
                                    className="px-3 py-2 text-indigo-700 bg-indigo-50 border border-indigo-100 hover:bg-indigo-100 rounded-lg font-medium text-sm flex items-center gap-2 mr-2"
                                >
                                    <span className="text-xs">Revert to Standard</span>
                                </button>
                            )}

                            {/* Improvise Button (AI) */}
                            <button
                                onClick={handleAiGenerate}
                                disabled={isGenerating}
                                className="px-3 py-2 text-purple-700 bg-purple-50 border border-purple-100 hover:bg-purple-100 rounded-lg font-medium text-sm flex items-center gap-2 mr-2"
                            >
                                {isGenerating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Wand2 className="w-4 h-4" />}
                                <span className="text-xs">Improvise (AI)</span>
                            </button>

                            <button onClick={() => handleSave()} disabled={isSaving || policy.status === 'Approved'} className="px-4 py-2 text-gray-700 bg-white border border-gray-300 hover:bg-gray-50 rounded-lg font-medium text-sm flex items-center gap-2 shadow-sm">
                                <Save className="w-4 h-4" /> Save
                            </button>
                            <button onClick={handleAiGenerate} disabled={isGenerating || readOnly} className="px-4 py-2 bg-purple-50 text-purple-700 border border-purple-200 hover:bg-purple-100 rounded-lg font-medium text-sm flex items-center gap-2 shadow-sm mr-2">
                                {isGenerating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Wand2 className="w-4 h-4" />}
                                Improvise
                            </button>
                            {policy.status !== 'Approved' && (
                                <button onClick={() => handleSave('Approved')} disabled={isSaving} className="px-6 py-2 bg-blue-600 text-white hover:bg-blue-700 rounded-lg font-bold text-sm shadow-sm flex items-center gap-2">
                                    <CheckCircle className="w-4 h-4" /> Approve
                                </button>
                            )}
                        </>
                    )}
                </div>
            </div>

            {/* Main Workspace */}
            <div className="flex-1 flex overflow-hidden">

                {/* Master Reference Pane (Left) */}
                {showSplitView && masterContent && (
                    <div className="master-ref-pane w-1/2 border-r border-gray-200 bg-gray-50 overflow-y-auto px-12 py-8">
                        <div className="mb-6 flex items-center justify-between">
                            <span className="text-xs font-bold text-gray-400 uppercase tracking-widest">Master Template (Gold Standard)</span>
                            <span className="px-2 py-0.5 bg-gray-200 text-gray-600 text-[10px] rounded uppercase font-bold">Read Only</span>
                        </div>
                        <div
                            className="prose prose-sm max-w-none prose-headings:text-gray-700 prose-p:text-gray-600 font-serif opacity-80 pointer-events-none select-none"
                            dangerouslySetInnerHTML={{ __html: masterContent }} // HTML from simple mammoth convert or marked
                        />
                    </div>
                )}

                {/* Editor Area (Right) */}
                <div className={`flex-1 flex flex-col items-center bg-gray-100 overflow-y-auto py-8 ${showSplitView ? 'border-l border-gray-200' : ''}`}>
                    {!readOnly && (
                        <div className="policy-toolbar sticky top-0 z-30 mb-4 transition-all w-[210mm]">
                            <EditorToolbar editor={editor} />
                        </div>
                    )}
                    <div
                        className="policy-page bg-white shadow-xl flex flex-col relative transition-all mx-auto mb-10 w-[210mm]"
                        style={{ padding: '25mm', minHeight: '297mm', height: 'auto', transform: showSplitView ? 'scale(0.9)' : 'scale(1)', transformOrigin: 'top center' }}
                    >
                        {/* Company Header */}
                        <div className="absolute top-[10mm] left-[25mm] right-[25mm] flex justify-between items-end border-b-2 border-gray-800 pb-2 mb-8 opacity-90 pointer-events-none select-none">
                            <div className="flex items-center gap-3">
                                <div className="w-10 h-10 bg-black text-white flex items-center justify-center font-bold text-xl rounded-sm">{companyName.charAt(0)}</div>
                                <div>
                                    <div className="text-xl font-bold text-black leading-none font-serif tracking-wide">{companyName}</div>
                                    <div className="text-xs text-gray-600 uppercase tracking-widest mt-0.5">Security & Compliance</div>
                                </div>
                            </div>
                            <div className="text-right">
                                <div className="text-xs text-gray-500 font-bold uppercase">Internal</div>
                            </div>
                        </div>

                        <div className="mt-8 flex-1 mb-[20mm]">
                            {editor && (
                                <BubbleMenu editor={editor} tippyOptions={{ duration: 100 }}>
                                    <div className="bg-white shadow-xl border border-gray-200 rounded-lg p-1 flex gap-1 transform scale-90 origin-bottom">
                                        <button onClick={() => handleAiRewrite('simplify')} disabled={rewriteLoading} className="px-2 py-1 hover:bg-purple-50 text-purple-700 text-xs font-bold rounded flex disabled:opacity-50">
                                            {rewriteLoading ? <Loader2 className="w-3 h-3 mr-1 animate-spin" /> : <Wand2 className="w-3 h-3 mr-1" />}
                                            Simplify
                                        </button>
                                        <button onClick={() => handleAiRewrite('expand')} disabled={rewriteLoading} className="px-2 py-1 hover:bg-blue-50 text-blue-700 text-xs font-bold rounded disabled:opacity-50">
                                            {rewriteLoading ? <Loader2 className="w-3 h-3 mr-1 animate-spin" /> : null}
                                            Expand
                                        </button>
                                    </div>
                                </BubbleMenu>
                            )}
                            <EditorContent editor={editor} />
                        </div>

                        {/* Footer */}
                        <div className="absolute bottom-[10mm] left-[25mm] right-[25mm] border-t border-gray-300 pt-2 flex justify-between text-xs text-gray-400 font-serif">
                            <span>{policy.name}</span>
                            <span className="hidden print:block">Page 1 of 1</span>
                        </div>
                    </div>
                </div>

                {/* Right Compliance Sidebar */}
                {!readOnly && !showSplitView && (
                    <div className="policy-sidebar w-80 bg-white border-l border-gray-200 shadow-lg z-30 flex flex-col overflow-y-auto">
                        <div className="p-4 border-b border-gray-100 bg-gray-50">
                            <h3 className="text-xs font-bold text-gray-500 uppercase tracking-widest">Compliance Check</h3>
                            <div className="mt-2 text-sm font-medium text-gray-900">ISO 27001:2022 Mapping</div>
                        </div>
                        <div className="p-4 space-y-3">
                            {Object.entries(complianceStatus).map(([section, passed]) => (
                                <div key={section} className={`flex items-center justify-between p-3 rounded-md border ${passed ? 'bg-green-50 border-green-100' : 'bg-red-50 border-red-100'}`}>
                                    <span className={`text-sm font-medium ${passed ? 'text-green-700' : 'text-red-700'}`}>{section}</span>
                                    {passed ? <CheckCircle className="w-5 h-5 text-green-500" /> : <X className="w-5 h-5 text-red-500" />}
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default PolicyEditor;
