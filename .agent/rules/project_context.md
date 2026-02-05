# Project Context: AssuRisk - Compliance Platform

## Goal
Building a multi-tenant, Vanta-like compliance tool that scans cloud metadata (AWS/GitHub) to assess security posture without accessing sensitive user data.

## Core Tech Stack
- Frontend: React 18, TailwindCSS
- Backend: Python 3.12, FastAPI
- Database: SQLite (Local file `app.db`)

## Critical Security Guardrails (Refined Core Logic)

### 1. Mandatory Tenant Isolation
- **Middleware:** Every API route must implement a `TenantResolver`. If `tenant_id` is missing from the JWT/Header, return `401 Unauthorized`.
- **DB Queries:** All database operations MUST include a `tenant_id` filter. Prioritize PostgreSQL Row-Level Security (RLS) over manual application-level filtering.
- **Data Leakage:** Any code that potentially allows cross-tenant data access is a critical failure.

### 2. Metadata Scrubber Engine
- **Pattern:** Follow the flow: `External API Fetch` -> `In-Memory Scrub` -> `Encrypted Storage`.
- **Content Ban:** Strictly prohibited from storing raw file contents, PII, or code snippets from client environments.
- **Compliance Mapping:** Tag every successful scan or check with its corresponding ISO 42001:2023 Control ID (e.g., A.6.2.4).

### 3. Least Privilege Integrations
- **Read-Only Scopes:** Always use the most restrictive API scopes (e.g., `ReadOnlyAccess` in AWS or `repo:status` in GitHub).
- **Credential Safety:** Never store plain-text secrets; use AWS Secrets Manager or a similar vault, bound by `tenant_id`.

## Current Phase
- We are currently validating **ISO 27001 Framework** enhancements and fixing **Reports Module** data gaps.
- Next task: Resolve "AI Framework to ISO 42001 Mapping" report issues (missing AI Governance module).
