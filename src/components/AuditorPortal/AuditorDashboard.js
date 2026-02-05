import React, { useState, useEffect } from 'react';
import axios from 'axios';
import config from '../../config';
import { auditService } from '../../services/auditService';
import { Shield, Layers, AlertTriangle, CheckCircle, Clock, ArrowRight, FileText, Lock, X, MessageSquare, BarChart2, Info, ChevronDown, Home, LogOut } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, PieChart, Pie, Legend } from 'recharts';
import { useAuth } from '../../contexts/AuthContext';

const mockBanner = (
    <div className="bg-amber-100 border-b border-amber-300 text-amber-900 px-6 py-2 flex items-center justify-center gap-2 text-sm font-bold shadow-inner">
        <AlertTriangle className="w-4 h-4" />
        SIMULATION MODE: DISPLAYING MOCK AUDIT EVIDENCE
    </div>
);


const AuditorDashboard = () => {
    const { user, logout } = useAuth(); // Get user for RBAC
    const [viewMode, setViewMode] = useState(null); // null (Selector), ISO_STRUCTURE, PROCESS, POLICIES, DOCUMENTS
    const [evidence, setEvidence] = useState([]);
    const [stats, setStats] = useState({
        total: 0,
        verified: 0,
        pending: 0,
        major_nc: 0,
        minor_nc: 0,
        observation: 0,
        ofi: 0,
        needs_clarification: 0,
        conformityData: [],
        weaknessData: [],
        detailedData: []
    });
    const [loading, setLoading] = useState(true);
    // eslint-disable-next-line
    const [filter, setFilter] = useState('ALL');
    const [selectedEvidence, setSelectedEvidence] = useState(null);
    const [reviewComment, setReviewComment] = useState('');
    const [selectedOutcome, setSelectedOutcome] = useState('VERIFIED'); // Default

    const [searchQuery, setSearchQuery] = useState('');

    const [scopeSettings, setScopeSettings] = useState(null);

    // Filter Frameworks based on Permissions
    const allowed = user?.allowed_frameworks || 'ALL';
    const canAccess = (fw) => allowed === 'ALL' || allowed.includes(fw);

    useEffect(() => {
        // AUTO-SELECT LOGIC
        if (allowed !== 'ALL') {
            const frameworks = allowed.split(',');
            if (frameworks.length === 1) {
                const fw = frameworks[0].trim();
                setSelectedFramework(fw);
                // Ensure ViewMode is set so dashboard renders immediately
                // For ISO, typically we might leave it null for sub-choice, but user likely wants to see content.
                // Based on UI buttons: SOC2/NIST set 'ISO_STRUCTURE', ISO sets nothing?
                // Actually, if ViewMode is null, the top bar "SWITCH" button thinks we are in dashboard mode but content is hidden?
                // No, looking at render: if (!viewMode) return (Preference Screen).
                // So for ISO, we must also set setViewMode('ISO_STRUCTURE') to skip the preference screen if desired.
                // Or leave it null to let them choose "Standard vs Process". 
                // Requirement: "bypass that screen".
                // I will set it to 'ISO_STRUCTURE' default for all to be safe.
                setViewMode('ISO_STRUCTURE');
            }
        }
        loadData();
    }, [allowed]);

    const loadData = async () => {
        try {
            // Fetch Evidence AND Scope Settings
            const token = localStorage.getItem('token');
            const headers = { Authorization: `Bearer ${token}` };

            const [evidenceData, settingsRes] = await Promise.all([
                auditService.getEvidence(),
                axios.get(`${config.API_BASE_URL}/settings/scope`, { headers }).catch(() => ({ data: { content: {} } }))
            ]);

            const scopeContent = settingsRes.data.content || {};
            const soc2Principles = scopeContent.soc2_selected_principles || ['Security']; // Default
            setScopeSettings(scopeContent);

            // SOA LOGIC: Filter out Non-Applicable items
            // 1. Standard Applicability
            let scopes_items = evidenceData.filter(e => e.is_applicable !== false && e.status !== 'NOT_APPLICABLE');

            // 2. SOC 2 Dynamic Scoping (Filter by Principle)
            scopes_items = scopes_items.filter(item => {
                const id = item.control_id;
                // Security is mandatory (CC)
                if (id.startsWith('CC')) return true;

                // Optional Principles
                if (id.startsWith('A') && !id.startsWith('A.')) return soc2Principles.includes('Availability'); // Avoid ISO 'A.' clash
                if (id.startsWith('C') && !id.startsWith('C1')) return soc2Principles.includes('Confidentiality'); // C1 is usually Confidentiality, verify structure
                if (id.startsWith('C') && !isNaN(parseInt(id[1])) && !id.startsWith('CC')) return soc2Principles.includes('Confidentiality');
                if (id.startsWith('PI')) return soc2Principles.includes('Processing Integrity');
                if (id.startsWith('P') && !isNaN(parseInt(id[1]))) return soc2Principles.includes('Privacy');

                return true; // Keep ISO and others by default
            });

            setEvidence(scopes_items);

            // 1. STATS FOR CARDS (Existing)
            const newStats = {
                total: scopes_items.length,
                verified: scopes_items.filter(e => ['VERIFIED', 'OBSERVATION', 'OFI'].includes(e.status)).length, // All "Blue/Green" states count as reviewed/conforming logic
                pending: scopes_items.filter(e => e.status === 'PENDING').length,
                major_nc: scopes_items.filter(e => e.status === 'MAJOR_NC').length,
                minor_nc: scopes_items.filter(e => e.status === 'MINOR_NC').length,
                observation: scopes_items.filter(e => e.status === 'OBSERVATION').length,
                ofi: scopes_items.filter(e => e.status === 'OFI').length,
                needs_clarification: scopes_items.filter(e => e.status === 'NEEDS_CLARIFICATION').length
            };
            // setStats(newStats); // This will be updated below

            // 2. CHART DATA PREPARATION

            // Chart A: Compliance Overview
            const conformityData = [
                { name: 'Conforms', value: newStats.verified, color: '#10B981' }, // Green
                { name: 'Non-Conforming', value: newStats.major_nc + newStats.minor_nc, color: '#EF4444' }, // Red
                { name: 'Pending Review', value: newStats.pending, color: '#9CA3AF' } // Gray
            ];

            // Chart B: Weak Areas (Breakdown of Issues)
            const weaknessData = [
                { name: 'Major NC', value: newStats.major_nc, color: '#DC2626' },
                { name: 'Minor NC', value: newStats.minor_nc, color: '#F87171' },
                { name: 'Observation', value: newStats.observation, color: '#F59E0B' },
                { name: 'OFI', value: newStats.ofi, color: '#3B82F6' }
            ].filter(d => d.value > 0); // Hide empty bars

            // Chart C: Detailed Breakdown by Control/Clause
            const detailedMap = {};
            scopes_items.forEach(item => {
                if (['MAJOR_NC', 'MINOR_NC', 'OBSERVATION', 'OFI'].includes(item.status)) {
                    // Use shortened ID for axis label (e.g. "A.5.1" or "4.1")
                    // Strip "Clause " prefix if present in ID logic (usually IDs are just "4.1")
                    const label = item.control_id.replace(/^Clause\s+/, '');

                    if (!detailedMap[label]) detailedMap[label] = { name: label, major: 0, minor: 0, obs: 0, ofi: 0 };

                    if (item.status === 'MAJOR_NC') detailedMap[label].major++;
                    if (item.status === 'MINOR_NC') detailedMap[label].minor++;
                    if (item.status === 'OBSERVATION') detailedMap[label].obs++;
                    if (item.status === 'OFI') detailedMap[label].ofi++;
                }
            });
            const detailedData = Object.values(detailedMap);

            // Store in state
            setStats({ ...newStats, conformityData, weaknessData, detailedData });

            setLoading(false);
        } catch (err) {
            console.error("Failed to load audit data", err);
            setLoading(false);
        }
    };

    const handleReviewSubmit = async () => {
        if (!selectedEvidence) return;

        // Validation - Require comment for any non-verified status
        if (selectedOutcome !== 'VERIFIED' && !reviewComment.trim()) {
            alert("Please provide a Finding/Note when marking an item as non-compliant or needing clarification.");
            return;
        }

        try {
            await auditService.reviewEvidence(selectedEvidence.id, {
                status: selectedOutcome,
                comment: reviewComment
            });

            // Refresh Data to reflect changes
            await loadData();

            // Close Modal & Reset Form
            setSelectedEvidence(null);
            setReviewComment('');

        } catch (error) {
            console.error("Failed to submit review:", error);
            alert("Failed to submit review. Please try again.");
        }
    };

    const [selectedFramework, setSelectedFramework] = useState(null); // 'ISO27001' or 'SOC2'

    // 0. Base Filter: Framework Only (Used for Stats)
    const frameworkEvidence = React.useMemo(() => {
        if (!selectedFramework) return [];

        // 1. Filter by Framework
        const filtered = evidence.filter(item => {
            if (selectedFramework === 'ISO27001') {
                return !!item.control_id.match(/^(\d|A\.)/);
            } else if (selectedFramework === 'SOC2') {
                // Precise Match for SOC 2 (Matches CC1, A1, P1, C1, PI1)
                // Use P\d to distinguish from NIST "PR" (Protect) which starts with P
                return !!item.control_id.match(/^(CC|A\d|P\d|C|PI)/);
            } else if (selectedFramework === 'NIST_CSF') {
                return !!item.control_id.match(/^(GV|ID|PR|DE|RS|RC)/);
            }
            return true;
        });

        // 2. Deduplicate by Control ID (Fix for 103 controls issue)
        // If multiple evidence items exist for one control, we just take the first one
        // to represent the "Control Requirement" in the dashboard list.
        const uniqueMap = new Map();
        filtered.forEach(item => {
            if (!uniqueMap.has(item.control_id)) {
                uniqueMap.set(item.control_id, item);
            }
        });

        return Array.from(uniqueMap.values());
    }, [evidence, selectedFramework]);

    // 1. Dynamic Stats Calculation (Based on Framework)
    const viewStats = React.useMemo(() => {
        if (!selectedFramework) return stats; // Return initial/global stats if no framework selected

        const items = frameworkEvidence;
        const newStats = {
            total: items.length,
            verified: items.filter(e => ['VERIFIED', 'OBSERVATION', 'OFI'].includes(e.status)).length,
            pending: items.filter(e => e.status === 'PENDING').length,
            major_nc: items.filter(e => e.status === 'MAJOR_NC').length,
            minor_nc: items.filter(e => e.status === 'MINOR_NC').length,
            observation: items.filter(e => e.status === 'OBSERVATION').length,
            ofi: items.filter(e => e.status === 'OFI').length,
            needs_clarification: items.filter(e => e.status === 'NEEDS_CLARIFICATION').length,
            detailedData: [],
            conformityData: [],
            weaknessData: []
        };

        // Charts
        newStats.conformityData = [
            { name: 'Conforms', value: newStats.verified, color: '#10B981' },
            { name: 'Non-Conforming', value: newStats.major_nc + newStats.minor_nc, color: '#EF4444' },
            { name: 'Pending Review', value: newStats.pending, color: '#9CA3AF' }
        ];

        newStats.weaknessData = [
            { name: 'Major NC', value: newStats.major_nc, color: '#DC2626' },
            { name: 'Minor NC', value: newStats.minor_nc, color: '#F87171' },
            { name: 'Observation', value: newStats.observation, color: '#F59E0B' },
            { name: 'OFI', value: newStats.ofi, color: '#3B82F6' }
        ].filter(d => d.value > 0);

        const detailedMap = {};
        items.forEach(item => {
            if (['MAJOR_NC', 'MINOR_NC', 'OBSERVATION', 'OFI'].includes(item.status)) {
                let label = item.control_id.replace(/^Clause\s+/, '');
                if (label.length > 8) label = label.substring(0, 8) + '...';

                if (!detailedMap[label]) detailedMap[label] = { name: label, major: 0, minor: 0, obs: 0, ofi: 0 };
                if (item.status === 'MAJOR_NC') detailedMap[label].major++;
                if (item.status === 'MINOR_NC') detailedMap[label].minor++;
                if (item.status === 'OBSERVATION') detailedMap[label].obs++;
                if (item.status === 'OFI') detailedMap[label].ofi++;
            }
        });
        newStats.detailedData = Object.values(detailedMap);

        return newStats;
    }, [frameworkEvidence, selectedFramework, stats]);


    // 2. View Filter: Status + Search (Used for Rendering List)
    const getGroupedData = () => {
        const filtered = frameworkEvidence.filter(item => {
            if (filter === 'PENDING' && item.status !== 'PENDING') return false;
            if (filter === 'ISSUES' && !['MAJOR_NC', 'MINOR_NC', 'NEEDS_CLARIFICATION'].includes(item.status)) return false;

            if (searchQuery) {
                const q = searchQuery.toLowerCase();
                const matchesId = item.control_id.toLowerCase().includes(q);
                const matchesName = item.control_name.toLowerCase().includes(q);
                const matchesDesc = (item.control_description || '').toLowerCase().includes(q);
                if (!matchesId && !matchesName && !matchesDesc) return false;
            }
            return true;
        });

        const groups = {};

        if (viewMode === 'ISO_STRUCTURE') {

            // SOC 2 GROUPING
            if (selectedFramework === 'SOC2') {
                filtered.forEach(item => {
                    let key = 'Other';
                    const id = item.control_id;

                    if (id.startsWith('CC1')) key = 'CC1: Control Environment (COSO)';
                    else if (id.startsWith('CC2')) key = 'CC2: Communication & Info (COSO)';
                    else if (id.startsWith('CC3')) key = 'CC3: Risk Assessment (COSO)';
                    else if (id.startsWith('CC4')) key = 'CC4: Monitoring Activities (COSO)';
                    else if (id.startsWith('CC5')) key = 'CC5: Control Activities (COSO)';
                    else if (id.startsWith('CC6')) key = 'CC6: Logical & Physical Access';
                    else if (id.startsWith('CC7')) key = 'CC7: System Operations';
                    else if (id.startsWith('CC8')) key = 'CC8: Change Management';
                    else if (id.startsWith('CC9')) key = 'CC9: Risk Mitigation';
                    else if (id.startsWith('A')) key = 'Availability Criteria';
                    else if (id.startsWith('PI')) key = 'Processing Integrity Criteria';
                    else if (id.startsWith('C')) key = 'Confidentiality Criteria';
                    else if (id.startsWith('P')) key = 'Privacy Criteria';

                    if (!groups[key]) groups[key] = [];
                    groups[key].push(item);
                });

                // SOC 2 Order
                const SOC_ORDER = [
                    'CC1: Control Environment (COSO)',
                    'CC2: Communication & Info (COSO)',
                    'CC3: Risk Assessment (COSO)',
                    'CC4: Monitoring Activities (COSO)',
                    'CC5: Control Activities (COSO)',
                    'CC6: Logical & Physical Access',
                    'CC7: System Operations',
                    'CC8: Change Management',
                    'CC9: Risk Mitigation',
                    'Availability Criteria',
                    'Confidentiality Criteria',
                    'Processing Integrity Criteria',
                    'Privacy Criteria',
                    'Other'
                ];
                const sortedKeys = Object.keys(groups).sort((a, b) => {
                    return SOC_ORDER.indexOf(a) - SOC_ORDER.indexOf(b);
                });

                const sortedGroups = {};
                sortedKeys.forEach(key => {
                    sortedGroups[key] = groups[key].sort((a, b) => a.control_id.localeCompare(b.control_id, undefined, { numeric: true }));
                });
                return sortedGroups;
            }

            // NIST CSF 2.0 GROUPING
            if (selectedFramework === 'NIST_CSF') {
                filtered.forEach(item => {
                    let key = 'Other';
                    const id = item.control_id;

                    // Group by Function Code (First 2 chars typically)
                    if (id.startsWith('GV')) key = 'GOVERN';
                    else if (id.startsWith('ID')) key = 'IDENTIFY';
                    else if (id.startsWith('PR')) key = 'PROTECT';
                    else if (id.startsWith('DE')) key = 'DETECT';
                    else if (id.startsWith('RS')) key = 'RESPOND';
                    else if (id.startsWith('RC')) key = 'RECOVER';

                    if (!groups[key]) groups[key] = [];
                    groups[key].push(item);
                });

                const NIST_ORDER = ['GOVERN', 'IDENTIFY', 'PROTECT', 'DETECT', 'RESPOND', 'RECOVER'];
                const sortedKeys = Object.keys(groups).sort((a, b) => {
                    return NIST_ORDER.indexOf(a) - NIST_ORDER.indexOf(b);
                });

                const sortedGroups = {};
                sortedKeys.forEach(key => {
                    sortedGroups[key] = groups[key].sort((a, b) => a.control_id.localeCompare(b.control_id, undefined, { numeric: true }));
                });
                return sortedGroups;
            }

            // ISO GROUPING (Original Logic)
            filtered.forEach(item => {
                let key = 'Other';

                // 1. Check for Clauses (Numeric start)
                const clauseMatch = item.control_id.match(/^(\d+)(\.\d+)?/);
                // Ensure it's not Annex A (which starts with A.)
                if (clauseMatch && !item.control_id.startsWith("A.")) {
                    const mainClause = clauseMatch[1];
                    // Explicit Title: "Clause 4: Context..."
                    key = `Clause ${mainClause}: ${item.domain || 'Requirement'}`;
                }
                // 2. Check for Annex A
                else if (item.control_id.startsWith('A.5')) key = 'Annex A.5: Organizational Controls';
                else if (item.control_id.startsWith('A.6')) key = 'Annex A.6: People Controls';
                else if (item.control_id.startsWith('A.7')) key = 'Annex A.7: Physical Controls';
                else if (item.control_id.startsWith('A.8')) key = 'Annex A.8: Technological Controls';

                if (!groups[key]) groups[key] = [];
                groups[key].push(item);
            });

            // Specific Sort Order
            const sortedKeys = Object.keys(groups).sort((a, b) => {
                const getScore = (str) => {
                    const s = str.trim();
                    if (s.startsWith("Clause 4")) return 4;
                    if (s.startsWith("Clause 5")) return 5;
                    if (s.startsWith("Clause 6")) return 6;
                    if (s.startsWith("Clause 7")) return 7;
                    if (s.startsWith("Clause 8")) return 8;
                    if (s.startsWith("Clause 9")) return 9;
                    if (s.startsWith("Clause 10")) return 10;

                    if (s.startsWith("Annex A.5")) return 500;
                    if (s.startsWith("Annex A.6")) return 600;
                    if (s.startsWith("Annex A.7")) return 700;
                    if (s.startsWith("Annex A.8")) return 800;

                    return 999;
                };
                return getScore(a) - getScore(b);
            });


            const sortedGroups = {};
            sortedKeys.forEach(key => {
                sortedGroups[key] = groups[key].sort((a, b) =>
                    a.control_id.localeCompare(b.control_id, 'en', { numeric: true })
                );
            });
            return sortedGroups;
        }
        else if (viewMode === 'PROCESS') {
            // Group by Process Tag
            filtered.forEach(item => {
                const process = item.process || 'Uncategorized';
                if (!groups[process]) groups[process] = [];
                groups[process].push(item);
            });

            const MASTER_PROCESS_ORDER = [
                "Governance & Policy",
                "HR Security",
                "Asset Management",
                "Access Control (IAM)",
                "Physical Security",
                "Operations (General)",
                "Configuration Management",
                "Cryptography",
                "Logging & Monitoring",
                "Clock Synchronization",
                "Vulnerability Management",
                "Capacity Management",
                "Backup Management",
                "Network Security",
                "SDLC (Development)",
                "Supplier Mgmt",
                "Incident & Resilience",
                "Threat Intel",
                "Legal & Compliance",
                "Risk Management",
                "Performance Evaluation",
                "Improvement"
            ];

            const sortedKeys = Object.keys(groups).sort((a, b) => {
                const idxA = MASTER_PROCESS_ORDER.indexOf(a);
                const idxB = MASTER_PROCESS_ORDER.indexOf(b);

                // If both are known, sort by index
                if (idxA !== -1 && idxB !== -1) return idxA - idxB;

                // Known items come first
                if (idxA !== -1) return -1;
                if (idxB !== -1) return 1;

                // Alphabetical fallback for unknown
                return a.localeCompare(b);
            });

            const sortedGroups = {};
            sortedKeys.forEach(key => {
                sortedGroups[key] = groups[key].sort((a, b) =>
                    a.control_id.localeCompare(b.control_id, undefined, { numeric: true, sensitivity: 'base' })
                );
            });
            return sortedGroups;
        }
        return groups;
    };

    const groupedEvidence = (viewMode === 'ISO_STRUCTURE' || viewMode === 'PROCESS') ? getGroupedData() : {};

    if (loading) return <div className="p-12 text-center text-gray-500">Loading Auditor Interface...</div>;

    // FRAMEWORK SELECTION SCREEN
    if (!selectedFramework) {
        return (
            <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-6">
                <div className="mb-10 text-center">
                    <h1 className="text-3xl font-bold text-gray-900 flex items-center justify-center gap-3">
                        <Shield className="w-10 h-10 text-blue-900" />
                        Select Audit Framework
                    </h1>
                    <p className="text-gray-500 mt-2">Choose the compliance framework standard for this audit session.</p>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl w-full">
                    {canAccess('ISO27001') && (
                        <button
                            onClick={() => setSelectedFramework('ISO27001')}
                            className="bg-white p-8 rounded-2xl shadow-sm border-2 border-transparent hover:border-blue-500 hover:shadow-xl transition-all group text-left relative overflow-hidden"
                        >
                            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                                <Shield className="w-32 h-32" />
                            </div>
                            <div className="w-16 h-16 bg-blue-50 rounded-2xl flex items-center justify-center mb-6 text-blue-600 group-hover:scale-110 transition-transform">
                                <Shield className="w-8 h-8" />
                            </div>
                            <h3 className="text-2xl font-bold text-gray-900 mb-2">ISO 27001:2022</h3>
                            <p className="text-gray-500 mb-6 font-medium">Information Security Management System</p>

                            <div className="space-y-2">
                                <div className="flex items-center gap-2 text-sm text-gray-600">
                                    <CheckCircle className="w-4 h-4 text-green-500" /> Clauses 4-10 (MSS)
                                </div>
                                <div className="flex items-center gap-2 text-sm text-gray-600">
                                    <CheckCircle className="w-4 h-4 text-green-500" /> Annex A Controls (93)
                                </div>
                            </div>

                            <div className="mt-8 flex items-center gap-2 text-blue-600 font-bold group-hover:translate-x-2 transition-transform">
                                Select Framework <ArrowRight className="w-5 h-5" />
                            </div>
                        </button>
                    )}

                    {canAccess('SOC2') && (
                        <button
                            onClick={() => { setSelectedFramework('SOC2'); setViewMode('ISO_STRUCTURE'); }}
                            className="bg-white p-8 rounded-2xl shadow-sm border-2 border-transparent hover:border-orange-500 hover:shadow-xl transition-all group text-left relative overflow-hidden"
                        >
                            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                                <Layers className="w-32 h-32" />
                            </div>
                            <div className="w-16 h-16 bg-orange-50 rounded-2xl flex items-center justify-center mb-6 text-orange-600 group-hover:scale-110 transition-transform">
                                <Layers className="w-8 h-8" />
                            </div>
                            <h3 className="text-2xl font-bold text-gray-900 mb-2">SOC 2 Type II</h3>
                            <p className="text-gray-500 mb-6 font-medium">Trust Services Criteria (COSO + CC Series)</p>

                            <div className="space-y-2">
                                <div className="flex items-center gap-2 text-sm text-gray-600">
                                    <CheckCircle className="w-4 h-4 text-green-500" /> Common Criteria (Security)
                                </div>
                                <div className="flex items-center gap-2 text-sm text-gray-600">
                                    <CheckCircle className="w-4 h-4 text-green-500" /> {scopeSettings?.soc2_selected_principles?.length > 1 ? `+ ${scopeSettings.soc2_selected_principles.length - 1} Selected Principles` : 'Optional Principles'}
                                </div>
                            </div>

                            <div className="mt-8 flex items-center gap-2 text-orange-600 font-bold group-hover:translate-x-2 transition-transform">
                                Select Framework <ArrowRight className="w-5 h-5" />
                            </div>
                        </button>
                    )}

                    {canAccess('NIST_CSF') && (
                        <button
                            onClick={() => { setSelectedFramework('NIST_CSF'); setViewMode('ISO_STRUCTURE'); }}
                            className="bg-white p-8 rounded-2xl shadow-sm border-2 border-transparent hover:border-cyan-500 hover:shadow-xl transition-all group text-left relative overflow-hidden"
                        >
                            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                                <Shield className="w-32 h-32" />
                            </div>
                            <div className="w-16 h-16 bg-cyan-50 rounded-2xl flex items-center justify-center mb-6 text-cyan-600 group-hover:scale-110 transition-transform">
                                <Shield className="w-8 h-8" />
                            </div>
                            <h3 className="text-2xl font-bold text-gray-900 mb-2">NIST CSF 2.0</h3>
                            <p className="text-gray-500 mb-6 font-medium">Cybersecurity Framework (Govern, Identify, Protect...)</p>

                            <div className="space-y-2">
                                <div className="flex items-center gap-2 text-sm text-gray-600">
                                    <CheckCircle className="w-4 h-4 text-green-500" /> Core Functions (6)
                                </div>
                                <div className="flex items-center gap-2 text-sm text-gray-600">
                                    <CheckCircle className="w-4 h-4 text-green-500" /> Cross-Mapped to ISO/SOC2
                                </div>
                            </div>

                            <div className="mt-8 flex items-center gap-2 text-cyan-600 font-bold group-hover:translate-x-2 transition-transform">
                                Select Framework <ArrowRight className="w-5 h-5" />
                            </div>
                        </button>
                    )}
                </div>
            </div>
        );
    }

    // VIEW PREFERENCE SCREEN
    if (!viewMode) {
        return (
            <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-6 animate-fade-in">
                <button
                    onClick={() => setSelectedFramework(null)}
                    className="absolute top-8 left-8 text-gray-500 hover:text-gray-800 flex items-center gap-2 font-medium"
                >
                    <ArrowRight className="w-4 h-4 rotate-180" /> Back to Frameworks
                </button>

                <div className="mb-10 text-center">
                    <h1 className="text-3xl font-bold text-gray-900 flex items-center justify-center gap-3">
                        {selectedFramework === 'ISO27001' ? <Shield className="w-10 h-10 text-blue-900" /> : selectedFramework === 'SOC2' ? <Layers className="w-10 h-10 text-orange-600" /> : <Shield className="w-10 h-10 text-cyan-600" />}
                        {selectedFramework === 'ISO27001' ? 'ISO 27001 Audit View' : selectedFramework === 'SOC2' ? 'SOC 2 Audit View' : 'NIST CSF 2.0 Audit View'}
                    </h1>
                    <p className="text-gray-500 mt-2">Select how you would like to structure the evidence review.</p>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-6xl w-full">
                    <button onClick={() => setViewMode('ISO_STRUCTURE')} className="bg-white p-6 rounded-xl shadow-sm border-2 border-transparent hover:border-blue-500 hover:shadow-md transition text-left group">
                        <div className="w-12 h-12 bg-indigo-50 rounded-lg flex items-center justify-center mb-4 text-indigo-600 group-hover:bg-indigo-600 group-hover:text-white transition-colors">
                            <FileText className="w-6 h-6" />
                        </div>
                        <h3 className="text-lg font-bold text-gray-900 mb-1">
                            {selectedFramework === 'ISO27001' ? 'Standard Structure' : 'Domain Structure'}
                        </h3>
                        <p className="text-xs text-gray-500 mb-4 h-10">
                            {selectedFramework === 'ISO27001' ? 'Clauses 4-10 followed by Annex A Controls.' : 'Grouped by Framework Domains (Functions/Criteria).'}
                        </p>
                        <span className="text-blue-600 font-medium flex items-center gap-2 text-xs group-hover:underline">Select View <ArrowRight className="w-3 h-3" /></span>
                    </button>

                    {selectedFramework === 'ISO27001' && (
                        <button onClick={() => setViewMode('PROCESS')} className="bg-white p-6 rounded-xl shadow-sm border-2 border-transparent hover:border-blue-500 hover:shadow-md transition text-left group">
                            <div className="w-12 h-12 bg-emerald-50 rounded-lg flex items-center justify-center mb-4 text-emerald-600 group-hover:bg-emerald-600 group-hover:text-white transition-colors">
                                <Layers className="w-6 h-6" />
                            </div>
                            <h3 className="text-lg font-bold text-gray-900 mb-1">Business Process</h3>
                            <p className="text-xs text-gray-500 mb-4 h-10">Audit by workflow: HR, Access Control, Physical Security, etc.</p>
                            <span className="text-blue-600 font-medium flex items-center gap-2 text-xs group-hover:underline">Select View <ArrowRight className="w-3 h-3" /></span>
                        </button>
                    )}


                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50 font-sans">
            {mockBanner}
            {/* TOP BAR */}
            <div className="bg-white border-b border-gray-200 sticky top-0 z-30 shadow-sm px-6 py-3 flex justify-between items-center h-16">
                <div className="flex items-center gap-4">
                    {/* BRAND LOGO */}
                    <div className="flex items-center gap-2 pr-4 border-r border-gray-200">
                        <div className="bg-blue-600 p-1.5 rounded-lg">
                            <Shield className="w-5 h-5 text-white" fill="currentColor" />
                        </div>
                        <span className="text-lg font-extrabold text-blue-900 tracking-tight">AssuRisk</span>
                    </div>

                    <div className="flex items-center gap-3">
                        <button
                            onClick={() => window.location.href = '/'} // Navigate to Home
                            className="p-2 hover:bg-gray-100 rounded-full text-gray-500 transition-colors"
                            title="Go to Home"
                        >
                            <Home className="w-5 h-5" />
                        </button>
                        <div>
                            <h1 className="text-xl font-bold text-gray-900 leading-none">Auditor Console</h1>
                            <div className="flex items-center gap-2 mt-1">
                                <p className="text-xs text-gray-500">
                                    {selectedFramework === 'ISO27001' ? 'ISO 27001:2022' : selectedFramework === 'SOC2' ? 'SOC 2 Type II' : 'NIST CSF 2.0'} • Audit Execution
                                </p>
                                <button
                                    onClick={() => { setViewMode(null); setSelectedFramework(null); }}
                                    className="text-[10px] font-bold text-blue-600 hover:underline bg-blue-50 px-1.5 py-0.5 rounded border border-blue-100"
                                >
                                    SWITCH
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="flex items-center gap-3">
                    {(viewMode === 'ISO_STRUCTURE' || viewMode === 'PROCESS') && (
                        <div className="relative">
                            <input
                                type="text"
                                placeholder="Search controls, clauses..."
                                className="pl-3 pr-4 py-1.5 border border-gray-200 rounded-lg text-sm w-64 focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-gray-50"
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                            />
                        </div>
                    )}

                    <div className="flex bg-gray-100 p-1 rounded-lg border border-gray-200">
                        <button
                            onClick={() => setViewMode('ISO_STRUCTURE')}
                            className={`px-3 py-1 text-xs font-bold rounded-md transition-all ${viewMode === 'ISO_STRUCTURE' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500 hover:text-gray-700'}`}
                        >
                            {selectedFramework === 'ISO27001' ? 'Clauses' : 'Domains'}
                        </button>
                        {selectedFramework === 'ISO27001' && (
                            <button
                                onClick={() => setViewMode('PROCESS')}
                                className={`px-3 py-1 text-xs font-bold rounded-md transition-all ${viewMode === 'PROCESS' ? 'bg-white text-blue-600 shadow-sm' : 'text-gray-500 hover:text-gray-700'}`}
                            >
                                Process
                            </button>
                        )}
                    </div>
                </div>

                <div className="ml-4 pl-4 border-l border-gray-200">
                    <button
                        onClick={() => {
                            if (window.confirm("Sign out?")) {
                                logout();
                                window.location.href = '/login';
                            }
                        }}
                        className="text-gray-400 hover:text-red-600 transition-colors flex items-center gap-2 text-sm font-medium"
                        title="Sign Out"
                    >
                        <LogOut className="w-5 h-5" />
                        <span className="hidden md:inline">Logout</span>
                    </button>
                </div>
            </div>

            {/* DASHBOARD CONTENT SWITCHER */}
            {(viewMode === 'ISO_STRUCTURE' || viewMode === 'PROCESS') && (
                <>
                    {/* SOC 2 EXCLUSIONS BANNER */}
                    {scopeSettings && scopeSettings.soc2_exclusions && Object.keys(scopeSettings.soc2_exclusions).length > 0 && (
                        <div className="bg-orange-50 border-b border-orange-100 px-6 py-4">
                            <h3 className="text-sm font-bold text-orange-800 flex items-center gap-2 mb-2">
                                <Info className="w-4 h-4" /> Scope Exclusions & Justifications
                            </h3>
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                {Object.entries(scopeSettings.soc2_exclusions).map(([principle, reason]) => (
                                    <div key={principle} className="bg-white p-3 rounded border border-orange-200 text-xs">
                                        <div className="font-bold text-gray-700 mb-1">{principle}</div>
                                        <div className="text-gray-600 italic">"{reason}"</div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* PROGRESS & FINDINGS */}
                    <div className="flex flex-col gap-4 p-4 border-b border-gray-200 bg-slate-50">
                        <div className="grid grid-cols-12 gap-4 h-40">

                            {/* COL 1: Compliance Overview (Pie) - 3/12 */}
                            <div className="col-span-3 bg-white rounded-xl shadow-sm border border-gray-200 p-2 flex flex-col items-center justify-center">
                                <div className="flex flex-col items-center mb-1">
                                    <h3 className="text-[10px] font-bold text-gray-400 uppercase tracking-wide">Compliance</h3>
                                    <span className="text-[10px] font-medium text-gray-500 bg-gray-100 px-1.5 rounded border border-gray-200 mt-0.5">
                                        {viewStats ? viewStats.total : 0} Controls in Scope
                                    </span>
                                </div>
                                <div className="h-28 w-full">
                                    <ResponsiveContainer width="100%" height="100%">
                                        <PieChart>
                                            <Pie
                                                data={viewStats.conformityData}
                                                cx="50%"
                                                cy="50%"
                                                innerRadius={25}
                                                outerRadius={40}
                                                paddingAngle={5}
                                                dataKey="value"
                                            >
                                                {viewStats.conformityData?.map((entry, index) => (
                                                    <Cell key={`cell-${index}`} fill={entry.color} />
                                                ))}
                                            </Pie>
                                            <Tooltip />
                                            <Legend iconSize={6} layout="vertical" verticalAlign="middle" align="right" wrapperStyle={{ fontSize: '9px' }} />
                                        </PieChart>
                                    </ResponsiveContainer>
                                </div>
                            </div>

                            {/* COL 2: Non-Conformance Info (Text Stats) - 3/12 */}
                            <div className="col-span-3 bg-white rounded-xl shadow-sm border border-gray-200 p-3 flex flex-col justify-center">
                                <h3 className="text-[10px] font-bold text-gray-400 uppercase mb-3 tracking-wide">Weakness Breakdown</h3>
                                <div className="space-y-2">
                                    {viewStats.weaknessData.length === 0 ? (
                                        <div className="text-xs text-gray-400 italic text-center py-4">No Issues Found</div>
                                    ) : (
                                        viewStats.weaknessData.map((item, idx) => (
                                            <div key={idx} className="flex justify-between items-center text-xs">
                                                <span className="flex items-center gap-1.5 font-medium text-gray-600">
                                                    <div className="w-2 h-2 rounded-full" style={{ backgroundColor: item.color }}></div>
                                                    {item.name}
                                                </span>
                                                <span className="font-bold text-gray-900 bg-gray-50 px-2 py-0.5 rounded border border-gray-100">{item.value}</span>
                                            </div>
                                        ))
                                    )}
                                </div>
                            </div>

                            {/* COL 3: Detailed Findings (Stacked Bar) - 6/12 */}
                            <div className="col-span-6 bg-white rounded-xl shadow-sm border border-gray-200 p-3">
                                <h3 className="text-[10px] font-bold text-gray-400 uppercase mb-1 tracking-wide">Findings by Control</h3>
                                <div className="h-32 w-full">
                                    {viewStats.detailedData && viewStats.detailedData.length > 0 ? (
                                        <ResponsiveContainer width="100%" height="100%">
                                            <BarChart
                                                data={viewStats.detailedData}
                                                margin={{ top: 5, right: 10, left: 0, bottom: 0 }}
                                                barSize={20}
                                            >
                                                <XAxis dataKey="name" tick={{ fontSize: 9 }} interval={0} />
                                                <YAxis tick={{ fontSize: 9 }} width={20} />
                                                <Tooltip cursor={{ fill: '#f9fafb' }} contentStyle={{ fontSize: '11px' }} />
                                                <Bar dataKey="major" stackId="a" fill="#DC2626" radius={[0, 0, 0, 0]} />
                                                <Bar dataKey="minor" stackId="a" fill="#F87171" radius={[0, 0, 0, 0]} />
                                                <Bar dataKey="obs" stackId="a" fill="#F59E0B" radius={[0, 0, 0, 0]} />
                                                <Bar dataKey="ofi" stackId="a" fill="#3B82F6" radius={[4, 4, 0, 0]} />
                                            </BarChart>
                                        </ResponsiveContainer>
                                    ) : (
                                        <div className="flex h-full items-center justify-center text-xs text-gray-300">
                                            No Detailed Findings to Display
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Main Content Area - Audit List */}
                    <div className="p-8">
                        <div className="space-y-8">
                            {Object.keys(groupedEvidence).map(groupKey => (
                                <div key={groupKey} className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                                    <div className="bg-gray-100 px-6 py-3 border-b border-gray-200 flex justify-between items-center">
                                        <h3 className="font-bold text-gray-800 flex items-center gap-2">
                                            <Layers className="w-4 h-4 text-blue-600" />
                                            {groupKey}
                                        </h3>
                                        <div className="text-xs font-mono text-gray-500 bg-white px-2 py-1 rounded border border-gray-200">
                                            {groupedEvidence[groupKey].length} in-scope
                                        </div>
                                    </div>

                                    <div className="divide-y divide-gray-100">
                                        {groupedEvidence[groupKey].map((item, index) => {
                                            const showHeader = viewMode === 'PROCESS' && (index === 0 || item.control_id !== groupedEvidence[groupKey][index - 1].control_id);

                                            return (
                                                <React.Fragment key={item.id}>
                                                    {/* Process View Sub-Header */}
                                                    {showHeader && (
                                                        <div className="bg-slate-50 border-y border-gray-200 px-6 py-2.5 sm:px-8 flex items-center gap-3">
                                                            <span className="font-mono bg-indigo-100 text-indigo-700 font-bold px-2 py-0.5 rounded text-xs border border-indigo-200">{item.control_id}</span>
                                                            <span className="font-semibold text-gray-800 text-sm">{item.control_name}</span>
                                                        </div>
                                                    )}

                                                    <div className="p-4 hover:bg-blue-50/40 w-full text-left transition flex items-center justify-between group pl-6 border-l-4 border-l-transparent hover:border-l-blue-400">
                                                        <div className="flex items-center gap-4">
                                                            {getStatusIcon(item.status)}
                                                            <div>
                                                                <h4 className="font-medium text-gray-900 text-sm flex items-center gap-2">
                                                                    <span className="font-mono font-bold text-blue-600 bg-blue-50 px-1.5 rounded border border-blue-100 text-xs">
                                                                        {item.control_id}
                                                                    </span>
                                                                    {item.control_name}
                                                                </h4>

                                                                <div className="flex items-center gap-2 mt-1">
                                                                    <span className="text-xs text-gray-500">{item.resource_name}</span>
                                                                    {item.badges && item.badges.map((badge, bIdx) => (
                                                                        <span key={bIdx} className="text-[10px] bg-gray-100 text-gray-600 px-1 rounded border border-gray-200">
                                                                            {badge}
                                                                        </span>
                                                                    ))}
                                                                </div>
                                                            </div>
                                                        </div>

                                                        <div className="flex items-center gap-4">
                                                            <span className="text-xs text-gray-400 font-mono">{new Date(item.submitted_at).toLocaleDateString()}</span>
                                                            <button
                                                                onClick={() => { setSelectedEvidence(item); setSelectedOutcome(item.status !== 'PENDING' ? item.status : 'VERIFIED'); }}
                                                                className="px-3 py-1.5 text-xs font-medium border border-gray-300 rounded text-gray-600 hover:bg-white hover:border-blue-500 hover:text-blue-600 transition bg-white shadow-sm opacity-0 group-hover:opacity-100"
                                                            >
                                                                Review
                                                            </button>
                                                        </div>
                                                    </div>
                                                </React.Fragment>
                                            );
                                        })}
                                    </div>
                                </div>
                            ))}
                            {Object.keys(groupedEvidence).length === 0 && (
                                <div className="text-center py-20 text-gray-400">
                                    No evidence found for this view.
                                </div>
                            )}
                        </div>
                    </div>
                </>
            )}



            {/* SECURE REVIEW MODAL (With Dropdown) */}
            {
                selectedEvidence && (
                    <div
                        className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4 backdrop-blur-sm"
                        onContextMenu={(e) => e.preventDefault()}
                    >
                        <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full flex flex-col max-h-[90vh] relative overflow-hidden select-none">

                            {/* WATERMARK */}
                            <div className="pointer-events-none absolute inset-0 flex items-center justify-center opacity-[0.03] z-0 rotate-[-12deg]">
                                <span className="text-9xl font-black text-gray-900">CONFIDENTIAL</span>
                            </div>

                            <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center z-10 bg-white">
                                <div>
                                    <h3 className="font-bold text-lg text-gray-900 flex items-center gap-2">
                                        <Lock className="w-5 h-5 text-red-600" />
                                        Secure Evidence Review
                                    </h3>
                                    <p className="text-xs text-red-500 font-mono">DO NOT DISTRIBUTE • AUTHORIZED AUDITOR EYES ONLY</p>
                                </div>
                                <button onClick={() => setSelectedEvidence(null)} className="p-2 hover:bg-gray-100 rounded-full">
                                    <X className="w-5 h-5 text-gray-500" />
                                </button>
                            </div>

                            <div className="p-6 flex-1 overflow-y-auto z-10 relative">
                                <div className="bg-slate-50 p-4 rounded-lg mb-6 border border-slate-200">
                                    <h4 className="font-bold text-gray-900 mb-1 text-lg flex items-center gap-2">
                                        <span className="bg-blue-600 text-white text-sm px-2 py-0.5 rounded">{selectedEvidence.control_id}</span>
                                        {selectedEvidence.control_name}
                                    </h4>
                                    <p className="text-sm text-gray-600 mb-2">{selectedEvidence.control_description}</p>
                                </div>

                                <div className="space-y-4">
                                    <div className="border-2 border-dashed border-gray-200 rounded-xl p-8 flex flex-col items-center justify-center bg-gray-50 min-h-[150px]">
                                        <FileText className="w-12 h-12 text-gray-300 mb-2" />
                                        <p className="font-medium text-gray-500">{selectedEvidence.resource_name}</p>
                                    </div>
                                    <div className="grid grid-cols-2 gap-4">
                                        {/* AUDITOR OUTCOME SELECTOR */}
                                        <div>
                                            <label className="block text-xs font-bold text-gray-700 uppercase mb-2">Review Outcome</label>
                                            <div className="relative">
                                                <select
                                                    value={selectedOutcome}
                                                    onChange={(e) => setSelectedOutcome(e.target.value)}
                                                    className="w-full appearance-none pl-3 pr-10 py-2 border border-gray-300 rounded-lg text-sm font-medium focus:ring-2 focus:ring-blue-500 outline-none bg-white"
                                                >
                                                    <option value="VERIFIED">Conforms</option>
                                                    <option value="MINOR_NC">Partially Conforms (Minor NC)</option>
                                                    <option value="MAJOR_NC">Needs Attention (Major NC)</option>
                                                    <option value="OBSERVATION">Observation</option>
                                                    <option value="OFI">Opportunity for Improvement (OFI)</option>
                                                </select>
                                                <ChevronDown className="absolute right-3 top-2.5 w-4 h-4 text-gray-500 pointer-events-none" />
                                            </div>
                                        </div>
                                        <div>
                                            <label className="block text-xs font-bold text-gray-700 uppercase mb-2">Findings / Notes</label>
                                            <input
                                                type="text"
                                                value={reviewComment}
                                                onChange={(e) => setReviewComment(e.target.value)}
                                                placeholder="Optional for Conformance..."
                                                className="w-full pl-3 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500"
                                            />
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div className="p-6 border-t border-gray-200 bg-gray-50 rounded-b-xl flex justify-end z-10">
                                <button onClick={handleReviewSubmit} className="bg-blue-600 text-white px-6 py-2 rounded-lg font-bold hover:bg-blue-700 shadow-sm flex items-center justify-center gap-2">
                                    <CheckCircle className="w-5 h-5" /> Submit Assessment
                                </button>
                            </div>
                        </div>
                    </div>
                )
            }
        </div >
    );
};

const getStatusIcon = (status) => {
    switch (status) {
        case 'VERIFIED': return <CheckCircle size={20} className="text-green-500" />;
        case 'MAJOR_NC': return <AlertTriangle size={20} className="text-red-600 fill-red-100" />;
        case 'MINOR_NC': return <AlertTriangle size={20} className="text-red-400" />;
        case 'OBSERVATION': return <Info size={20} className="text-amber-500" />;
        case 'OFI': return <BarChart2 size={20} className="text-blue-500" />;
        case 'NEEDS_CLARIFICATION': return <MessageSquare size={20} className="text-orange-500" />;
        default: return <Clock size={20} className="text-gray-300" />;
    }
};

export default AuditorDashboard;
