import React, { useEffect, useState, useRef } from 'react';
import { useParams } from 'react-router-dom';
import axios from '../services/api';
import { Previewer } from 'pagedjs';
import { marked } from 'marked';
import { asBlob } from 'html-docx-js/dist/html-docx';
import { saveAs } from 'file-saver';

const PrintLayout = () => {
    const { id } = useParams();
    const [policy, setPolicy] = useState(null);
    const [loading, setLoading] = useState(true);

    const previewRef = useRef(null);

    useEffect(() => {
        const fetchPolicy = async () => {
            try {
                const res = await axios.get(`/policies/${id}`);
                setPolicy(res.data);
            } catch (error) {
                console.error("Failed to load policy for printing", error);
            } finally {
                setLoading(false);
            }
        };
        fetchPolicy();
    }, [id]);

    const handleDownloadWord = () => {
        if (!policy) return;

        // Simple HTML structure for Word
        // html-docx-js understands basic HTML/CSS
        const htmlString = `
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>${policy.name}</title>
                <style>
                    body { font-family: 'Times New Roman', serif; font-size: 11pt; }
                    h1 { font-size: 24pt; font-weight: bold; text-align: center; margin-top: 50pt; }
                    .meta { text-align: center; color: #555; margin-bottom: 50pt; }
                    table { width: 100%; border-collapse: collapse; margin-top: 20pt; }
                    td, th { border: 1px solid #000; padding: 5pt; }
                </style>
            </head>
            <body>
                <h1>${policy.name}</h1>
                <div class="meta">
                    <p>Version: ${policy.version}</p>
                    <p>Owner: ${policy.owner}</p>
                    <p>Date: ${new Date(policy.updated_at).toLocaleDateString()}</p>
                </div>
                <!-- Page Break for Word -->
                <br style="page-break-before: always" />
                ${marked.parse(policy.content)}
            </body>
            </html>
        `;

        const blob = asBlob(htmlString);
        saveAs(blob, `${policy.name}.docx`);
    };

    useEffect(() => {
        if (!policy || !previewRef.current) return;

        // Convert Markdown to HTML
        marked.use({ gfm: true, breaks: true });
        const htmlContent = marked.parse(policy.content);

        // Construct the full document content
        const cleanContent = `
            <div class="print-content">
                <div class="cover-page">
                    <h1 class="main-title">${policy.name}</h1>
                    <div class="meta">
                        <p><strong>Version:</strong> ${policy.version}</p>
                        <p><strong>Owner:</strong> ${policy.owner}</p>
                        <p><strong>Date:</strong> ${new Date(policy.updated_at).toLocaleDateString()}</p>
                    </div>
                    <div class="logo">AssuRisk</div>
                </div>
                <div class="policy-body">
                    ${htmlContent}
                </div>
            </div>
        `;



        // CSS for Paged.js
        const styles = `
            @page {
                size: A4;
                margin: 20mm 20mm 20mm 20mm;
                @top-center {
                    content: "AssuRisk Confidential";
                    font-size: 9pt;
                    color: #888;
                }
                @bottom-right {
                    content: "Page " counter(page) " of " counter(pages);
                    font-size: 9pt;
                }
                @bottom-left {
                    content: "${policy.name} - v${policy.version}";
                    font-size: 9pt;
                    color: #888;
                }
            }

            .cover-page {
                page-break-after: always;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                height: 100%;
                text-align: center;
            }

            .main-title {
                font-size: 32pt;
                font-weight: bold;
                margin-bottom: 2rem;
            }

            .meta {
                font-size: 14pt;
                color: #555;
            }

            .logo {
                margin-top: 4rem;
                font-size: 20pt;
                font-weight: bold;
                letter-spacing: 2px;
            }

            /* Table Handling */
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 1rem 0;
            }
            th, td {
                border: 1px solid #ccc;
                padding: 8px;
                font-size: 10pt;
            }
            th {
                background-color: #f3f4f6;
            }

            /* Typography */
            body {
                font-family: 'Times New Roman', Times, serif;
                line-height: 1.5;
                font-size: 11pt;
            }
            h1 { font-size: 18pt; margin-top: 2em; }
            h2 { font-size: 14pt; margin-top: 1.5em; border-bottom: 1px solid #eee; padding-bottom: 5px; }
            h3 { font-size: 12pt; font-weight: bold; margin-top: 1em; }
            
            /* Print Specific Overrides to ensure breaking */
            p { margin-bottom: 1em; }
            .policy-body { font-size: 11pt; }
        `;

        // We need to render the content into a temporary element first, OR pass it as string
        // Paged.js Previewer expects content, stylesheets, container

        // Create a temporary container for the source content
        const sourceContainer = document.createElement('div');
        sourceContainer.innerHTML = cleanContent;
        sourceContainer.style.position = 'absolute';
        sourceContainer.style.left = '-10000px';
        sourceContainer.style.top = '0';
        document.body.appendChild(sourceContainer);

        // Clear previous output
        if (previewRef.current) {
            previewRef.current.innerHTML = '';
        }

        // CSS blob
        const styleSheet = document.createElement('style');
        styleSheet.id = 'print-styles';
        styleSheet.innerHTML = styles;
        document.head.appendChild(styleSheet);

        // Run Paged.js
        const previewer = new Previewer();

        previewer.preview(sourceContainer, [], previewRef.current).then((flow) => {
            console.log("Paged.js rendering complete", flow);
            // Cleanup source after render
            if (document.body.contains(sourceContainer)) {
                document.body.removeChild(sourceContainer);
            }
        }).catch(err => {
            console.error("Paged.js rendering failed", err);
            // Cleanup on error too
            if (document.body.contains(sourceContainer)) {
                document.body.removeChild(sourceContainer);
            }
        });

        // Cleanup function for effect
        return () => {
            const existingStyle = document.getElementById('print-styles');
            if (existingStyle) existingStyle.remove();

            // Safety check for source container
            if (document.body.contains(sourceContainer)) {
                document.body.removeChild(sourceContainer);
            }
        };

    }, [policy]);

    if (loading) return <div>Generating PDF Preview...</div>;
    if (!policy) return <div>Policy not found</div>;

    return (
        <div className="bg-gray-200 min-h-screen p-8">
            {/* Toolbar */}
            <div className="fixed top-0 left-0 right-0 bg-white shadow-md p-4 flex justify-between z-50 screen-only">
                <h1 className="font-bold">PDF Preview: {policy.name}</h1>
                <div className="flex gap-2">
                    <button
                        onClick={handleDownloadWord}
                        className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 font-medium"
                    >
                        Download Word
                    </button>
                    <button
                        onClick={() => window.print()}
                        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 font-medium"
                    >
                        Save as PDF
                    </button>
                </div>
            </div>

            {/* Paged.js Container */}
            <div className="mt-16 mx-auto bg-white shadow-2xl" ref={previewRef}>
                {/* Paged.js will render here */}
            </div>

            {/* Print Hiding CSS */}
            <style>{`
                @media print {
                    .screen-only { display: none !important; }
                    body { background: white; }
                    .bg-gray-200 { background: white; }
                    /* Ensure Pagedjs pages take over */
                    .pagedjs_pages { width: 100%; transform: none !important; }
                }
                /* Screen Preview Styling */
                .pagedjs_pages {
                    margin: 0 auto;
                    box-shadow: 0 0 10px rgba(0,0,0,0.1);
                }
                /* FIX: Hide overflow in preview to respect page boundaries visibly */
                .pagedjs_page {
                    background: white;
                    box-shadow: 0 0 5px rgba(0,0,0,0.1);
                    margin-bottom: 2rem;
                    overflow: hidden; /* Vital to hide content that didn't fit (though it shouldn't be there if fragmented correctly) */
                }
            `}</style>
        </div>
    );
};

export default PrintLayout;
