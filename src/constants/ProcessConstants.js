// MASTER LIST OF 21 BUSINESS PROCESSES
// This is the Single Source of Truth for "Business View" grouping.
export const BUSINESS_PROCESSES = [
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

// Helper to normalize backend values if needed
export const normalizeProcessName = (name) => {
    if (!name) return "Governance & Policy"; // AUTOMATIC DEFAULT (Nuclear Option)

    // Check for exact match first
    const match = BUSINESS_PROCESSES.find(p => p === name);
    if (match) return match;

    // Fuzzy mapping for legacy/variation (Prevent "Risk Mgmt" vs "Risk Management")
    const lower = name.toLowerCase();

    if (lower.includes("risk")) return "Risk Management";
    if (lower.includes("hr") || lower.includes("human")) return "HR Security";
    if (lower.includes("asset")) return "Asset Management";
    if (lower.includes("access") || lower.includes("identity")) return "Access Control (IAM)";
    if (lower.includes("incident")) return "Incident & Resilience";
    if (lower.includes("supplier") || lower.includes("vendor")) return "Supplier Mgmt";
    if (lower.includes("physical")) return "Physical Security";
    if (lower.includes("logging") || lower.includes("monitor")) return "Logging & Monitoring";
    if (lower.includes("change")) return "Governance & Policy"; // Specifically requested for Change Mgmt

    // Fallback: Force Governance & Policy instead of Uncategorized
    return "Governance & Policy";
};
