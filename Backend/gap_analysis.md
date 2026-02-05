# Feature Gap Analysis & Roadmap

This document outlines the current state of each major feature, its limitations ("The Gap"), and the concrete next steps to bring it to full "Commercial Grade" functionality.

## 1. Evidence Management
*   **Current State**: 
    *   Files upload to local `uploads/` folder.
    *   Metadata (filename, size) stored in DB.
    *   Linked to controls manually.
*   **The Gap**: 
    *   Local storage doesn't scale (will vanish if deployed to cloud).
    *   No content verification (user can upload a cat photo as "Security Policy").
    *   No version control or expiration handling.
*   **Next Steps**:
    1.  **Cloud Storage**: Migrate from local disk to **AWS S3** or **Google Cloud Storage**.
    2.  **AI Verification**: Connect Gemini API to read the PDF text and verify it matches the Control description (Auto-Approvals).
    3.  **Expiry Alerts**: Add "Expiration Date" field and email owners 30 days before evidence expires (e.g., yearly pentest).

## 2. Automated Tests (Integrations)
*   **Current State**: 
    *   UI shows "Integration Health" (Mock Data).
    *   "Run Test" buttons exist but trigger mock logic or simple DB checks.
*   **The Gap**:
    *   No real connection to external tools (AWS, GitHub, Google Workspace, Okta).
    *   The platform knows *what* to check, but can't *actually* check it yet.
*   **Next Steps**:
    1.  **Integration Engine**: Build the backend module to handle OAuth connections (e.g., "Connect GitHub").
    2.  **Collectors**: Write Python scripts to query APIs (e.g., `boto3` for AWS, `PyGithub` for GitHub).
    3.  **Mapper**: Map specific API checks (e.g., "MFA Enabled") to specific Control IDs.

## 3. Risk Register
*   **Current State**:
    *   Basic CRUD table (Create, Read, Update, Delete).
    *   Stores Title, Likelihood, Impact.
*   **The Gap**:
    *   No **Inherent vs. Residual** logic (Risk before vs. after controls).
    *   No "Treatment Plan" workflow (Assigning a control to mitigate a risk).
*   **Next Steps**:
    1.  **Logic Update**: Add formula: `Risk Score = Likelihood * Impact`.
    2.  **Mitigation Linking**: Allow users to select *existing* Controls that mitigate a specific risk.
    3.  **Recalculation**: Show "Residual Risk" dropping when the linked control is "Implemented".

## 4. Access Reviews
*   **Current State**:
    *   UI table showing a list of users (Mock or Seeded).
    *   Buttons to "Keep" or "Revoke".
*   **The Gap**:
    *   List of users is manual. It doesn't know who *actually* has access to your system.
*   **Next Steps**:
    1.  **Identity Import**: Pull user list from **Google Workspace** or **Active Directory**.
    2.  **Snapshotting**: Freeze the list on the 1st of every quarter.
    3.  **Audit Log**: When "Revoke" is clicked, generate a ticket (JIRA) or email IT to actually remove access.

## 5. Policies
*   **Current State**:
    *   Placeholder page / Basic list.
*   **The Gap**:
    *   Policies are just static text or uploads.
    *   Employees are not acknowledging them.
*   **Next Steps**:
    1.  **Policy Editor**: Embed a Rich Text Editor (e.g., Quill/TinyMCE) to write policies in-app.
    2.  **Employee Portal**: A separate "readonly" view for all employees to log in and click "I Accept".
    3.  **Tracking**: Dashboard showing "% of employees who signed the Acceptable Use Policy".

## 6. Dashboard & Reporting
*   **Current State**:
    *   Aggregates live DB stats (Real).
    *   Charts are functional.
*   **The Gap**:
    *   No historical trend (can't see "Security Posture improved by 10% this month").
    *   No PDF Export for auditors.
*   **Next Steps**:
    1.  **Snapshots**: Nightly job to save current stats to a `stats_history` table.
    2.  **PDF Generator**: Use `WeasyPrint` or similar to generate a "Compliance Certificate" PDF.

---

## Recommended Execution Order

1.  **Storage & Integrations** (Foundational) - Enable S3 and GitHub/AWS connections.
2.  **Policy Editor** (Low Effort, High Value) - Get policies written.
3.  **Access Reviews** (Compliance Critical) - Connect to an Identity Provider.
4.  **AI Verification** (The "Wow" Factor) - Automate evidence review.
