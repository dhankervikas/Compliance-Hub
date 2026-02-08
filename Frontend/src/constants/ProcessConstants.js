// MASTER LIST OF 21 BUSINESS PROCESSES
// This is the Single Source of Truth for "Business View" grouping.
export const BUSINESS_PROCESSES = [
    "Governance",
    "Human Resources Management",
    "Asset Management",
    "Access Management",
    "Physical Security",
    "IT Operations",
    "Configuration Management",
    "Cryptography",
    "Logging & Monitoring",
    "Clock Synchronization",
    "Vulnerability Management",
    "Capacity Management",
    "Backup Management",
    "Network Security",
    "Secure Software Development Life Cycle (SSDLC)",
    "Third Party Risk Management",
    "Incident & Resilience",
    "Threat Intelligence",
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
    if (lower.includes("hr") || lower.includes("human")) return "Human Resources Management";
    if (lower.includes("asset")) return "Asset Management";
    if (lower.includes("access") || lower.includes("identity")) return "Access Management";
    if (lower.includes("incident")) return "Incident & Resilience";
    if (lower.includes("supplier") || lower.includes("vendor") || lower.includes("third")) return "Third Party Risk Management";
    if (lower.includes("physical")) return "Physical Security";
    if (lower.includes("logging") || lower.includes("monitor")) return "Logging & Monitoring";
    if (lower.includes("operations")) return "IT Operations"; // Fix: Map legacy "Operations" to "IT Operations"
    if (lower.includes("sdlc") || lower.includes("development") || lower.includes("software")) return "Secure Software Development Life Cycle (SSDLC)"; // Fix: New Name
    if (lower.includes("change")) return "Governance"; // Specifically requested for Change Mgmt

    // Fallback: Force Governance instead of Uncategorized
    return "Governance";
};
