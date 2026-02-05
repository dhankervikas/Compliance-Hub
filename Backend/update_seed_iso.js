
const fs = require('fs');
const path = require('path');

const csvPath = 'C:\\Users\\dhank\\OneDrive\\Documents\\Compliance_Product\\Backend\\iso27001_intent_library.csv';
const seedPath = 'C:\\Users\\dhank\\OneDrive\\Documents\\Compliance_Product\\Frontend\\src\\data\\seedData.js';

// 1. Read existing seedData to get Titles map
const seedContent = fs.readFileSync(seedPath, 'utf8');
const titleMap = {};

// Regex to find existing controls: { control_id: "4.1", title: "Context...", ... }
const regex = /{ control_id: "([^"]+)", title: "([^"]+)"/g;
let match;
while ((match = regex.exec(seedContent)) !== null) {
    const id = match[1];
    const title = match[2];
    if (!titleMap[id]) {
        titleMap[id] = title;
    }
}
// Add manual titles for any missing ones (just in case)
titleMap["6.1.1"] = "General Risk Planning";
titleMap["6.1.2"] = "Information security risk assessment";
titleMap["6.1.3"] = "Information security risk treatment";
titleMap["8.1"] = "Operational planning and control";
titleMap["8.2"] = "Information security risk assessment (Execution)";
titleMap["8.3"] = "Information security risk treatment (Execution)";
titleMap["9.1"] = "Monitoring, measurement, analysis and evaluation";
titleMap["9.2"] = "Internal Audit";
titleMap["9.3"] = "Management Review";
titleMap["10.1"] = "Nonconformity and corrective action";
titleMap["10.2"] = "Continual Improvement";

// 2. Read CSV
const csvContent = fs.readFileSync(csvPath, 'utf8');
const lines = csvContent.split(/\r?\n/);
const controls = [];

// Helper to parse CSV line correctly handling quotes
function parseCsvLine(line) {
    const result = [];
    let start = 0;
    let inQuotes = false;
    for (let i = 0; i < line.length; i++) {
        if (line[i] === '"') {
            inQuotes = !inQuotes;
        } else if (line[i] === ',' && !inQuotes) {
            let field = line.substring(start, i);
            // Remove surrounding quotes
            if (field.startsWith('"') && field.endsWith('"')) {
                field = field.substring(1, field.length - 1);
            }
            // Unescape double quotes
            field = field.replace(/""/g, '"');
            result.push(field.trim());
            start = i + 1;
        }
    }
    // Last field
    let lastField = line.substring(start);
    if (lastField.startsWith('"') && lastField.endsWith('"')) {
        lastField = lastField.substring(1, lastField.length - 1);
    }
    result.push(lastField.trim());
    return result;
}

// Category Mapping based on ID prefix or Type
function getCategory(id, type) {
    if (id.startsWith("4.") || id.startsWith("5.")) return "Governance & Policy";
    if (id.startsWith("6.") || id.startsWith("8.")) return "Risk Management"; // Clauses 6 & 8
    if (id.startsWith("7.1") || id.startsWith("7.5")) return "Governance & Policy";
    if (id.startsWith("7.2") || id.startsWith("7.3") || id.startsWith("A.6.")) return "HR Security";
    if (id.startsWith("7.4")) return "Incident & Resilience";
    if (id.startsWith("A.5.")) { // Governance / Supplier / Legal etc. - default to Governance or verify
        // Specific mapping for A.5
        if (["A.5.9", "A.5.10", "A.5.11", "A.5.12", "A.5.13"].includes(id)) return "Asset Management";
        if (["A.5.15", "A.5.16", "A.5.17", "A.5.18"].includes(id)) return "Access Control (IAM)";
        if (["A.5.19", "A.5.20", "A.5.21", "A.5.22", "A.5.23"].includes(id)) return "Supplier Mgmt";
        if (["A.5.24", "A.5.25", "A.5.26", "A.5.27", "A.5.28", "A.5.29", "A.5.30"].includes(id)) return "Incident & Resilience";
        if (["A.5.31", "A.5.32", "A.5.33", "A.5.34", "A.5.36"].includes(id)) return "Legal & Compliance";
        if (["A.5.35"].includes(id)) return "Performance Evaluation";
        if (["A.5.7"].includes(id)) return "Threat Intel";
        return "Governance & Policy";
    }
    if (id.startsWith("A.7.")) return "Physical Security";
    if (id.startsWith("A.8.")) {
        // Break down A.8
        if (["A.8.1", "A.8.2", "A.8.3", "A.8.4", "A.8.5"].includes(id)) return "Access Control (IAM)"; // Wait, user had Asset for 8.1??
        // Checking seedData for existing consistency
        if (id === "A.8.1") return "Asset Management";
        if (["A.8.2", "A.8.3", "A.8.4", "A.8.5"].includes(id)) return "Access Control (IAM)";
        if (["A.8.6"].includes(id)) return "Capacity Management";
        if (["A.8.7", "A.8.10", "A.8.11", "A.8.12", "A.8.18"].includes(id)) return "Operations (General)";
        if (["A.8.8"].includes(id)) return "Vulnerability Management";
        if (["A.8.9"].includes(id)) return "Configuration Management";
        if (["A.8.13"].includes(id)) return "Backup Management";
        if (["A.8.14"].includes(id)) return "Incident & Resilience"; // Redundancy
        if (["A.8.15", "A.8.16"].includes(id)) return "Logging & Monitoring";
        if (["A.8.17"].includes(id)) return "Clock Synchronization";
        if (["A.8.19"].includes(id)) return "Threat Intel"; // Install software?
        if (["A.8.20", "A.8.21", "A.8.22", "A.8.23"].includes(id)) return "Network Security";
        if (["A.8.24"].includes(id)) return "Cryptography";
        if (parseInt(id.split('.')[2]) >= 25 && parseInt(id.split('.')[2]) <= 33) return "SDLC (Development)";
        if (id === "A.8.34") return "Legal & Compliance";
        if (id === "A.8.35") return "Performance Evaluation";
        return "Operations (General)";
    }
    if (id.startsWith("9.")) return "Performance Evaluation";
    if (id.startsWith("10.")) return "Improvement";

    return "General";
}

lines.forEach(line => {
    if (!line.trim()) return;
    // Skip Header Row
    if (line.includes("Clause_or_control") || line.includes("Intent ID")) return;

    const cols = parseCsvLine(line);
    // CSV Columns: ID, Framework, Control_ID, Type, Requirement, Evidence, Strength, Active, Empty
    // Expect at least 5 columns
    if (cols.length < 5) return;

    const intentId = cols[0]; // INT-04-01 (Unique Key)
    const standardId = cols[2]; // 4.1 (Standard Clause)
    const description = cols[4];
    if (!description) return;

    // Use INTENT ID as the unique control_id for DB uniqueness
    // Use Standard ID as the TITLE so it shows up in the "Standard Control" column on UI
    const title = standardId;

    // Use Column D (Intent_type) for Display Column
    const rawIntentType = cols[3] || "General";
    const intentType = rawIntentType.charAt(0).toUpperCase() + rawIntentType.slice(1).toLowerCase();

    // Use Helper for Process Grouping (Category)
    const processGroup = getCategory(standardId, cols[3]);

    // COMPOUND STRATEGY: Process Group | Intent Type
    const compoundCategory = `${processGroup}|${intentType}`;

    controls.push({
        control_id: intentId,
        title: title,
        description: description,
        category: compoundCategory
    });
});

console.log(`Parsed ${controls.length} controls.`);

// 3. Construct new array string
const newArrayStr = "export const ISO_CONTROLS = [\n" +
    controls.map(c => `    { control_id: "${c.control_id}", title: "${c.title}", description: "${c.description.replace(/"/g, '\\"')}", category: "${c.category}" }`).join(",\n") +
    "\n];";

// 4. Update seedData.js
// Find the start and end of ISO_CONTROLS array
const startMarker = "export const ISO_CONTROLS = [";
const endMarker = "];";

const startIndex = seedContent.indexOf(startMarker);
if (startIndex === -1) {
    console.error("Could not find ISO_CONTROLS array start");
    process.exit(1);
}

// Find the corresponding closing bracket for this array
// We can just find the NEXT ]; after start index? No, strictly there might be nested arrays? No, seedData is simple.
// We'll search for "];" followed by new content or EOF, but specifically the one closing this block.
// Assuming the file structure is standard. 
// We will look for "\n];" after the start.
// Better: Regex replace.
const filePart1 = seedContent.substring(0, startIndex);
// We need to find where the array ends. 
// It usually ends before "export const SOC2_CONTROLS".
const nextExportIndex = seedContent.indexOf("export const SOC2_CONTROLS", startIndex);
let endIndex = -1;
if (nextExportIndex !== -1) {
    endIndex = seedContent.lastIndexOf("];", nextExportIndex);
} else {
    // If it's the last one
    endIndex = seedContent.lastIndexOf("];");
}

if (endIndex === -1) {
    console.error("Could not find ISO_CONTROLS array end");
    process.exit(1);
}

const filePart2 = seedContent.substring(endIndex + 2); // Skip ];

const newFileContent = filePart1 + newArrayStr + filePart2;

fs.writeFileSync(seedPath, newFileContent, 'utf8');
console.log("Updated seedData.js successfully.");
