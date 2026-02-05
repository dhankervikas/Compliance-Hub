# Project Bible: AssuRisk Compliance Hub

## 1. Project Overview
AssuRisk is an AI-powered Compliance Management System (ISMS) designed to automate the lifecycle of ISO 27001:2022 and SOC 2 audits. The system minimizes manual effort by linking policies, controls, evidence, and automated tests into a single source of truth.

### Tech Stack
- **Backend**: FastAPI (Python), SQLAlchemy (SQLite/PostgreSQL).
- **Frontend**: React (Create React App), Tailwind CSS, Lucide Icons.
- **AI**: Google Gemini 1.5 Flash (for content generation & audit logic).
- **Reporting**: Paged.js (PDF Generation), Recharts (Analytics).

---

## 2. Modules & Completed Work

### A. Governance & Frameworks
- **Multi-Framework Support**: Database seeded with **ISO 27001:2022** (93 Controls) and **SOC 2** (Common Criteria).
- **Control Library**: Full browser for controls with "Implementation Status" (Implemented, In Progress, Not Started).
- **Automated Mapping**: Controls are cross-mapped (e.g., ISO A.5.1 maps to SOC 2 CC1.1).

### B. Statement of Applicability (SoA)
- **Interactive SoA**: A dedicated interface to toggle controls as "Applicable" or "Not Applicable".
- **AI Justifications**: The AI automatically suggests justifications for exclusions (e.g., "Excluded: Physical security N/A for cloud-only scope").
- **Reporting**: Generates the formal SoA document required for Stage 1 audits.

### C. Policy Management (Current Active Focus)
- **Lifecycle Management**: 
    - **Drafting**: AI-assisted writing using a strict 10-section auditor-grade structure.
    - **Review**: Editor with "Rewrite" capabilities.
    - **Approval**: Workflow moves text from "Policies" (Drafts) to "Documents" (Locked/published).
- **Documents Repository**: A separate read-only library for approved, version-controlled docs.
- **Intent-Based Generation**: 
    - We have mapped 72 specific policies to their ISO controls.
    - specialized "Intents" (e.g., ISMS Scope must mention "Clause 4.1") are hardcoded to ensure compliance.

### D. Evidence & Automation
- **Evidence Collector**: Drag-and-drop file upload linked to specific controls.
- **Automated Tests**:
    - **Mock Collectors**: Simulates fetching data from AWS, Azure, Jira, and GitHub.
    - **Validation**: Scripts verify if evidence (e.g., `backup_logs.pdf`) satisfies the control.
    - **Badging**: Controls get a "Pass/Fail" badge based on the latest test run.

### E. Auditor Portal
- **External View**: A stripped-down, read-only dashboard for External Auditors.
- **Features**: View-only access to Policies, Evidence files, and the SoA. No edit rights.
- **Login**: Separate role-based access for "Auditor" users.

### F. Integrations
- **Adapter Architecture**: `data_adapter.py` enables plug-and-play connections to external APIs.
- **Current Status**: Simulated data for testing (AWS Instance checks, Jira Ticket closure rates).

## 3. Current Active Task: Policy Content Generation

We are currently in the process of generating the full content for the ~72 seeded policies.
**Goal**: Populate the `content` field for all policies with high-quality, ISO-compliant text.

### Key Context for Claude
We have set up the `POLICY_INTENTS` dictionary in `app/api/policies.py`. This dictionary contains the *exact* bullet points (from standard screenshots) that the AI *must* include in the text.
*   **Input**: `POLICY_CONTROL_MAP` (The list of 72 policies).
*   **Constraint**: Use the 10-section Markdown format defined in `ai_service.py`.
*   **Immediate Action**: The user needs to run the generation for "ISMS Scope" and "Context" documents using these intents.

## 4. Configuration & Secrets
**CRITICAL**: This project relies on environment variables for API access.
*   **Location**: `Backend/.env`
*   **Key Variable**: `GEMINI_API_KEY` (Required for Policy Generation & Audit Logic).
    *   *Note*: The system currently uses `gemini-1.5-flash-001`.
*   **Database URL**: `DATABASE_URL` (Defaults to `sqlite:///./sql_app.db` if unset).

## 5. Detailed File Inventory
**Project Root**: `C:\Projects\Compliance_Product\`

### Backend (`/Backend`)
*   **AI Logic**: `app/services/ai_service.py` (Contains the Prompt Engineering & Gemini Client).
*   **Policy Logic**: `app/api/policies.py` (Contains `POLICY_CONTROL_MAP` & `POLICY_INTENTS`).
*   **Database Models**: `app/models/` (Schema definitions).
*   **Seeding Scripts**: 
    *   `seed_full_suite.py` (The list of 72 policies).
    *   `auto_generate_drafts.py` (The script to bulk-run the AI).

### Frontend (`/Frontend`)
*   **Policy Editor**: `src/components/PolicyEditor.js` (The Wysiwyg/Markdown editor).
*   **Document Library**: `src/components/Documents.js` (The Approved Docs view).
*   **SoA Interface**: `src/components/SoA.js` (Statement of Applicability).
*   **Auditor View**: `src/components/AuditorPortal/AuditorDashboard.js`.
*   **API Client**: `src/services/api.js` (Axios configuration).
