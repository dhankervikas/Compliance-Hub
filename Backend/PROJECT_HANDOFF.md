# AssuRisk Project Handoff

**Last Updated:** January 11, 2026
**Status:** Alpha / Internal Testing
**Tech Stack:** React (Frontend) + FastAPI (Backend) + PostgreSQL

---

## 🚀 Executive Summary
AssuRisk is a compliance automation platform (similar to Vanta/Drata) designed to help companies achieve ISO 27001 and SOC 2 compliance. 
The project has moved past the prototype phase. The Frontend and Backend are **fully integrated**, the database is **seeded** with real frameworks, and core modules (Evidence, Risk, Access Reviews) are **functional**.

---

## 🏗️ Architecture

### **Backend (`/Backend/AssuRisk`)**
*   **Framework:** FastAPI (Python 3.11+)
*   **Database:** PostgreSQL (`compliance_hub`)
*   **ORM:** SQLAlchemy with Pydantic schemas
*   **Auth:** OAuth2 with Password Flow (JWT)
*   **Key Modules:**
    *   `app/api/`: Endpoints (Auth, Frameworks, Controls, Evidence, Processes, Risk, Access)
    *   `app/models/`: Database Tables
    *   `app/services/`: Logic layer (AI Assessment, Process Mapping)

### **Frontend (`/Frontend`)**
*   **Framework:** React 18
*   **Routing:** React Router DOM v6
*   **Styling:** Tailwind CSS + Lucide Icons
*   **Charts:** Recharts
*   **Key Components:**
    *   `App.js`: Main Router & Protected Layout
    *   `Sidebar.js`: Navigation
    *   `Dashboard.js`: Overview & Stats
    *   `FrameworkDetail.js`: Control implementations
    *   `Evidence.js`: File management
    *   `RiskRegister.js`: Risk management table

---

## ✅ Completed Features (Phase 8 Status)

### 1. **Core Frameworks**
*   **ISO 27001:2022**: Fully seeded (Clauses 4-10 + Annex A merged).
*   **SOC 2**: Seeded (Trust Services Criteria).
*   **Progress Tracking**: Automated calculation of % completion based on control status.

### 2. **Authentication & Security**
*   **Login Flow**: Functional (`/login` -> Dashboard).
*   **Protected Routes**: Middleware redirects unauthenticated users.
*   **Role Based**: Admin user seeded (`admin` / `admin123`).

### 3. **Evidence Management**
*   **Upload**: Drag-and-drop or file selection works.
*   **Linking**: Evidence can be linked to specific Controls.
*   **Validation**: Backend validates file types and metadata. 
*   **Bug Fix**: Resolved recent API mismatch for uploads.

### 4. **New Modules**
*   **Risk Register**: Table to track risks, likelihood, impact, and treatment plans.
*   **Access Reviews**: Interface to review user access (Keep/Revoke).
*   **Policies**: Policy management and approval workflow.
*   **Automated Tests**: Placeholder UI for running system checks.

---

## 🛠️ Setup & Run Instructions

### **1. Database**
Ensure PostgreSQL is running.
Credentials: `postgres` / `postgres123` (Local dev default).

### **2. Backend**
```powershell
cd Backend/AssuRisk
# Activate Virtual Env (if not active)
.\venv\Scripts\activate
# Run Server
uvicorn app.main:app --reload
```
*   Server: `http://localhost:8000`
*   Docs: `http://localhost:8000/docs`

### **3. Frontend**
```powershell
cd Frontend
# Install dependencies (only if new)
npm install
# Run Client
npm start
```
*   Client: `http://localhost:3000`

---

## 🐛 Known Issues / Recent Fixes
*   **Fix**: `Evidence Upload` 500 Error -> Resolved by fixing API Form Data handling.
*   **Fix**: `Framework Not Found` -> Resolved by using strict IDs in routing.
*   **Fix**: `Login Loop` -> Resolved by adding `AuthProvider` and `ProtectedLayout`.
*   **Cleanup**: Removed duplicate "ISMS" framework; condensed into main ISO 27001.

---

## 📋 Next Steps (Roadmap)

1.  **Trust Center**:
    *   Build public-facing page to showcase compliance status.
    *   Endpoint: `/trust-center` (currently placeholder).

2.  **AI Integration (Real)**:
    *   Replace `MockAIService` with real Gemini API calls.
    *   Analyze uploaded Evidence PDFs for content validation.

3.  **Questionnaires**:
    *   Implement Vendor Risk Assessment forms.

4.  **Deployment**:
    *   Dockerize the application (Dockerfile + docker-compose).
    *   Deploy to AWS/Vercel.

---

**Handover Note:**
The codebase is clean. The `Backend/AssuRisk` folder is the source of truth for the Python code. The `Frontend` folder contains the React app.
Ensure you run **both** servers to test full functionality.
