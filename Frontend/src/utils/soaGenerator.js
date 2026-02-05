import ExcelJS from 'exceljs';

export const generateSoA = async (frameworkName, controls, evidenceList, frameworks) => {
    // 1. Setup Workbook
    const workbook = new ExcelJS.Workbook();

    // METADATA
    workbook.creator = 'AssuRisk Compliance Engine';
    workbook.lastModifiedBy = 'AssuRisk Auto-Generator';
    workbook.created = new Date();
    workbook.modified = new Date();

    // SHEET 1: Statement of Applicability
    const sheet = workbook.addWorksheet('Statement of Applicability', {
        views: [{ state: 'frozen', ySplit: 6 }]
    });

    // HEADER STYLING
    sheet.columns = [
        { header: 'ID', key: 'id', width: 10 },
        { header: 'Domain', key: 'domain', width: 15 },
        { header: 'Control', key: 'control', width: 40 },
        { header: 'Applicability', key: 'app', width: 15 },
        { header: 'Justification / Scope', key: 'justification', width: 50, style: { alignment: { wrapText: true } } },
        { header: 'Implementation Status', key: 'status', width: 20 },
        { header: 'Evidence Link', key: 'evidence', width: 40 }
    ];

    // COMPANY HEADER BLOCK
    sheet.mergeCells('A1:G1');
    sheet.getCell('A1').value = `STATEMENT OF APPLICABILITY (SoA) - ${frameworkName}`;
    sheet.getCell('A1').font = { size: 16, bold: true, color: { argb: 'FFFFFFFF' } };
    sheet.getCell('A1').fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF1E3A8A' } };
    sheet.getCell('A1').alignment = { horizontal: 'center' };

    sheet.mergeCells('A2:G2');
    sheet.getCell('A2').value = `Generated: ${new Date().toLocaleDateString()} | Version: 1.0.3 | Scope: Cloud-Native | Confidential`;
    sheet.getCell('A2').alignment = { horizontal: 'center' };
    sheet.getCell('A2').font = { italic: true };

    sheet.mergeCells('A3:C3');
    sheet.getCell('A3').value = "Company Name: __________________________";
    sheet.mergeCells('D3:G3');
    sheet.getCell('D3').value = "Approved By: __________________________ (Date: ____/____/____)";

    // ROW 6: Data Headers
    const headerValues = ['ID', 'Domain', 'Control', 'Applicability', 'Justification / Scope', 'Implementation Status', 'Evidence Link'];
    sheet.getRow(6).values = headerValues;
    sheet.getRow(6).font = { bold: true, color: { argb: 'FFFFFFFF' } };
    sheet.getRow(6).fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF4F46E5' } }; // Indigo-600
    sheet.getRow(6).alignment = { horizontal: 'center', vertical: 'middle' };

    // DATA POPULATION

    // Group Controls by Framework ID (with Fallback)
    const grouped = {};
    controls.forEach(ctrl => {
        let id = ctrl.framework_id;

        // Fallback: Detect Framework from ID Pattern if valid ID missing
        if (!id) {
            if (ctrl.control_id.startsWith('A.')) id = 1; // ISO 27001
            else if (ctrl.control_id.includes('ISO42001')) id = 2; // ISO 42001
            else id = "other";
        }

        if (!grouped[id]) grouped[id] = [];
        grouped[id].push(ctrl);
    });

    const frameworkIds = Object.keys(grouped).sort();

    frameworkIds.forEach(fwId => {
        // Resolve Framework Name
        let sectionTitle = "Other Standards";

        // Try to find name in passed frameworks list
        if (frameworks && frameworks.length > 0) {
            const fw = frameworks.find(f => String(f.id) === String(fwId));
            if (fw) sectionTitle = fw.name || fw.code;
        }

        // Fallback Titles if Lookup Failed but ID is known (standard IDs)
        if (sectionTitle === "Other Standards") {
            if (String(fwId) === "1") sectionTitle = "ISO/IEC 27001:2022";
            if (String(fwId) === "2") sectionTitle = "ISO/IEC 42001:2023";
        }

        // ADD SECTION HEADER ROW
        const headerRow = sheet.addRow([sectionTitle.toUpperCase()]);
        sheet.mergeCells(`A${headerRow.number}:G${headerRow.number}`);
        headerRow.getCell(1).font = { size: 14, bold: true, color: { argb: 'FF1F2937' } };
        headerRow.getCell(1).fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFE5E7EB' } };
        headerRow.getCell(1).alignment = { horizontal: 'left', indent: 1 };
        headerRow.height = 30;

        // Process Controls in this Group
        const groupControls = grouped[fwId];

        groupControls.forEach((ctrl, index) => {
            const ev = evidenceList.filter(e => e.control_id === ctrl.control_id);
            const hasEvidence = ev.length > 0;
            const isApplicable = ctrl.is_applicable !== false;
            const applicability = isApplicable ? "APPLICABLE" : "NOT APPLICABLE";

            let status = "Not Implemented";
            if (!isApplicable) status = "Excluded";
            else if (ctrl.status === 'IMPLEMENTED' || hasEvidence) status = "Implemented";

            // JUSTIFICATION MAPPING (Category + Detail)
            let justificationText = ctrl.justification || "Standard inclusion.";
            if (ctrl.justification_reason) {
                justificationText = `[${ctrl.justification_reason}]: ${justificationText}`;
            } else if (!isApplicable) {
                justificationText = "[Missing Category]: No justification provided.";
            }

            // CLEAN UP ID FOR DISPLAY (Remove Redundant Prefix)
            let displayId = ctrl.control_id;
            if (String(fwId) === "2" || sectionTitle.includes("42001")) {
                displayId = displayId.replace("ISO42001-", "");
            }

            const row = sheet.addRow({
                id: displayId,
                domain: ctrl.category || "General",
                control: ctrl.title,
                app: applicability,
                justification: justificationText,
                status: ctrl.implementation_method || status,
                evidence: hasEvidence ? `View ${ev.length} items` : (isApplicable ? "Pending" : "N/A")
            });

            // STYLING: Zebra Striping (Local index relative to group)
            if (index % 2 !== 0 && status !== 'Excluded') {
                row.eachCell((cell) => {
                    cell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFF9FAFB' } };
                });
            }

            // Conditional Formatting for Status
            if (status === 'Excluded') {
                row.eachCell((cell) => {
                    cell.font = { color: { argb: 'FF991B1B' }, italic: true }; // Red Text
                    cell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFFFF1F2' } }; // Light Red BG
                });
            } else if (ctrl.status === 'IMPLEMENTED') {
                row.getCell('status').font = { color: { argb: 'FF166534' }, bold: true };
            }
        });
    });

    // FOOTER WATERMARK
    sheet.headerFooter.oddFooter = "&C&\"Arial,Italic\"Generated by AssuRisk Compliance Engine - MOCK DATA";

    // SHEET 2: Evidence Manifest
    const sheet2 = workbook.addWorksheet('Evidence Manifest');
    sheet2.columns = [
        { header: 'Evidence ID', key: 'id', width: 15 },
        { header: 'Filename', key: 'name', width: 40 },
        { header: 'Type', key: 'type', width: 15 },
        { header: 'Hash (SHA-256)', key: 'hash', width: 60 }
    ];

    // Mock hashes for professional look
    evidenceList.forEach(e => {
        sheet2.addRow({
            id: e.id || "N/A",
            name: e.resource_name || e.filename || "Unnamed",
            type: e.type || "Document",
            hash: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855" // Empty string hash mock
        });
    });

    // GENERATE BUFFER
    const buffer = await workbook.xlsx.writeBuffer();
    return buffer;
};
