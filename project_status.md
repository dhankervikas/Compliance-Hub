# Project Status: AssuRisk / Compliance Hub

**Date:** 2026-01-18
**Version:** 0.2.0-beta
**Status:** **Compliance Engine Architecture Implemented**

## 1. Project Overview
**AssuRisk** (aka Compliance Hub) is a comprehensive GRC (Governance, Risk, and Compliance) platform designed to streamline audit readiness for frameworks like ISO 27001, SOC 2, HIPAA, and GDPR. It leverages AI to automate policy generation, evidence collection, and gap analysis.

## 2. Technical Stack
*   **Frontend:** React (Create React App), Tailwind CSS, Lucide Icons, **TipTap (Rich Text)**.
*   **Backend:** Python FastAPI, SQLAlchemy, Uvicorn, **Mammoth (.docx pipeline)**.
*   **AI Engine:** Simulation Mode (Default) / Anthropic Claude (Configurable).
*   **Database:** SQLite (Development) / PostgreSQL (Production ready).

## 3. Current Implementation Status

### ✅ **NEW: Compliance Engine Architecture** (Source of Truth)
- **Immutable Master Templates**: "Gold Standard" policies are stored as read-only assets, preventing accidental degradation of compliance standards.
- **Word-to-DB Pipeline**: Automated ingestion of `.docx` templates into the database using `mammoth`.
- **Policy Lifecycle**:
    - **Clone**: Users create editable drafts from Gold Standards.
    - **Restore**: Users can revert drafts back to the Gold Standard at any time.
    - **Split View**: Auditors/Users can view the Master Template side-by-side with the Draft.

### Core Features
- [x] **ISO 27001:2022 ISMS**:
    - **Clause 4 Context**: Registers for Internal/External Issues, Interested Parties, and Scope.
    - **Annex A Controls**: Full mapping and Grouping.
- [x] **Multi-Framework Support**: SOC 2 Type II, HIPAA, GDPR, NIST CSF 2.0.
- [x] **Framework Setup Wizard**: Scope definition and framework selection.
- [x] **Dashboard**: Real-time compliance scoring and Health Widgets.

### Evidence & Automation
- [x] **Automated Evidence Mapping**: Artifacts linked to specific controls.
- [x] **Auditor Perspective**: Detail drawers with "Points of Focus" and examples.

### AI Capabilities
- [x] **Policy Generation**: Template-based generation with variable injection.
- [x] **Evidence Suggestion**: Context-aware artifact recommendations.
- [x] **Text Rewriting**: Simplify/Formalize text using AI.

## 4. Recent Milestones
1.  **Compliance Engine**: Implemented the `master_templates` backend and data architecture.
2.  **Context Registers**: Delivered full CRUD for ISO 27001 Clause 4 requirements.
3.  **SOC 2 Implementation**: Full COSO mapping and evidence requirements.

## 5. Known Issues & Next Steps
*   **Frontend Split View**: The UI for the "Split View" editor in `PolicyEditor.js` is partially implemented and requires final layout adjustments.
*   **PDF Generation**: Library dependencies need finalization for production deployment.

## 6. How to Run
### Backend
```bash
cd Backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd Frontend
npm start
```
*(Runs on `http://localhost:3000`)*
