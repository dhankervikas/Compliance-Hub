import React from 'react';
import api from './services/api';
import { BrowserRouter as Router, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { EntitlementProvider } from './contexts/EntitlementContext';
import EntitlementGuard from './components/EntitlementGuard';
import Unauthorized from './components/Unauthorized';
import Login from './components/Login';
import TenantLogin from './components/TenantLogin';
import Workspaces from './components/Workspaces';
import ComplianceDashboard from './components/ComplianceDashboard';
import Dashboard from './components/Dashboard';
import Sidebar from './components/Sidebar';
import FrameworkDetail from './components/FrameworkDetail';
import SystemEffectiveness from './components/SystemEffectiveness';
import ReportsDashboard from './components/ReportsDashboard';
// import Settings from './components/Settings'; // REMOVED: Unused and causes folder collision
import StatementOfApplicability from './components/StatementOfApplicability';
import InitiationWizard from './components/AuditorPortal/InitiationWizard';
import AuditorDashboard from './components/AuditorPortal/AuditorDashboard';
import PoliciesDashboard from './components/PoliciesDashboard';
import Policies from './components/Policies';
import PolicyDetail from './components/PolicyDetail';
import PrintLayout from './components/PrintLayout';
import Evidence from './components/Evidence';
import SettingsLayout from './components/Settings/SettingsLayout';
import SettingsForm from './components/Settings/SettingsForm';
import ContextPage from './components/ContextPage';
import UserManagement from './components/UserManagement';
import Documents from './components/Documents';
import AdminInbox from './components/AdminInbox';

import TenantOnboardingWizard from './components/TenantOnboardingWizard';
import PeopleDirectory from './components/PeopleDirectory';
import IdentityRiskDashboard from './components/IdentityRiskDashboard';
import ErrorBoundary from './components/ErrorBoundary'; // Import ErrorBoundary

// --- PLACEHOLDER COMPONENT FOR NEW ROUTES ---
const PlaceholderPage = ({ title }) => (
    <div className="p-8 animate-fade-in">
        <h1 className="text-2xl font-bold text-gray-900 mb-4">{title}</h1>
        <div className="bg-white p-16 rounded-xl border border-gray-200 shadow-sm text-center">
            <div className="mx-auto w-16 h-16 bg-blue-50 rounded-full flex items-center justify-center mb-6">
                <span className="text-3xl">🚧</span>
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">Under Construction</h3>
            <p className="text-gray-500 max-w-md mx-auto">
                The <b>{title}</b> module is linked and ready for development.
                Detailed views for this section will be implemented in the next phase.
            </p>
        </div>
    </div>
);

const ProtectedRoute = ({ children, allowedRoles = [] }) => {
    const { token, user, loading } = useAuth();
    // Use location to determine where to redirect
    const tenantMatch = window.location.pathname.match(/\/t\/([^/]+)/);
    const tenantId = tenantMatch ? tenantMatch[1] : null;

    if (loading) {
        return <div className="flex h-screen items-center justify-center text-gray-500">Loading verification...</div>;
    }

    if (!token) {
        // Context-Aware Redirect
        if (tenantId) {
            return <Navigate to={`/t/${tenantId}/login`} replace />;
        }
        return <Navigate to="/login" replace />;
    }

    // Role-Based Access Control
    if (user) {
        const role = user.role || 'admin'; // Default to admin if missing

        // 1. Auditors attempting to access non-auditor pages
        if (role === 'auditor' && !window.location.pathname.startsWith('/auditor-portal')) {
            return <Navigate to="/auditor-portal/dashboard" replace />;
        }

        // 2. Strict Role Check (if allowedRoles prop provided)
        if (allowedRoles.length > 0 && !allowedRoles.includes(role)) {
            // Context aware return for unauthorized might be needed, but for now simple:
            return <Navigate to="/unauthorized" replace />;
        }
    }

    return children;
};

const ProtectedLayout = () => {
    // Session Integrity Check
    const { token } = useAuth();
    // We need to extract tenantId from URL to verify against token
    // Since this layout is inside /t/:tenantId, we can use window location or hook
    // But useParams might not work if the Route defining params is the parent? 
    // Actually the parent Route is `/t/:tenantId`. So useParams should work in Outlet or here.
    // Let's force check via URL regex to be robust.const match = window.location.pathname.match(/\/t\/([^/]+)/);
    const tenantId = window.location.pathname.match(/\/t\/([^/]+)/)?.[1];

    React.useEffect(() => {
        const checkSession = async () => {
            if (!tenantId || !token) return;

            try {
                // Call Health Check
                await api.get('/health/session-check', {
                    params: { tenant_id: tenantId },
                    headers: { 'X-Target-Tenant-ID': tenantId }
                });
            } catch (err) {
                console.error("Session integrity failed:", err);
                // If 403 or 500, force logout from this tenant context
                // Redirect to login
                window.location.href = `/t/${tenantId}/login`;
            }
        };

        checkSession();
        // Optional: Interval check? 
        // const interval = setInterval(checkSession, 60000); return () => clearInterval(interval);
    }, [tenantId, token]);

    // CLEANUP: Removed console log after debugging

    return (
        <div className="flex h-screen bg-gray-50">
            <Sidebar />
            <div className="flex-1 overflow-auto ml-64">
                {/* Standard Router Outlet - Listeners in Components handle updates */}
                <Outlet />
            </div>
        </div>
    );
};

function App() {
    return (
        <ErrorBoundary>
            <AuthProvider>
                <Router>
                    <EntitlementProvider>
                        <Routes>
                            <Route path="/login" element={<Login />} />

                            <Route path="/login" element={<Login />} />

                            {/* MAGIC LINK LOGIN */}
                            <Route path="/t/:tenantId/login" element={<TenantLogin />} />



                            {/* SUPER ADMIN WORKSPACES */}
                            <Route
                                path="/super-admin"
                                element={
                                    <ProtectedRoute allowedRoles={['admin']}>
                                        <Workspaces />
                                    </ProtectedRoute>
                                }
                            />
                            <Route
                                path="/super-admin/onboarding"
                                element={
                                    <ProtectedRoute allowedRoles={['admin']}>
                                        <TenantOnboardingWizard />
                                    </ProtectedRoute>
                                }
                            />

                            {/* TENANT CONTEXT LAYOUT */}
                            <Route
                                path="/t/:tenantId"
                                element={
                                    <ProtectedRoute>
                                        <ProtectedLayout />
                                    </ProtectedRoute>
                                }
                            >
                                {/* DASHBOARD */}
                                <Route path="dashboard" element={<Dashboard />} />

                                {/* COMPLIANCE DASHBOARD */}
                                <Route path="compliance-dashboard" element={<ComplianceDashboard />} />

                                {/* EFFECTIVENESS */}
                                <Route path="effectiveness" element={<SystemEffectiveness />} />

                                {/* FRAMEWORKS */}
                                <Route path="frameworks" element={<Navigate to="../dashboard" replace />} />
                                <Route path="frameworks/:id" element={
                                    <EntitlementGuard>
                                        <FrameworkDetail />
                                    </EntitlementGuard>
                                } />

                                {/* OVERVIEW */}
                                <Route path="controls" element={<PlaceholderPage title="Controls" />} />
                                <Route path="monitors" element={
                                    <EntitlementGuard resource="feature" requiredId="aws_scanner">
                                        <PlaceholderPage title="Monitors" />
                                    </EntitlementGuard>
                                } />
                                <Route path="get-started" element={<PlaceholderPage title="Get Started" />} />


                                {/* DOCUMENTS */}
                                <Route path="documents" element={<Documents />} />
                                <Route path="evidence" element={<Evidence />} />
                                <Route path="policies" element={
                                    <EntitlementGuard resource="feature" requiredId="policy_management">
                                        <PoliciesDashboard />
                                    </EntitlementGuard>
                                } />
                                <Route path="policies/:id" element={<PolicyDetail />} />
                                <Route path="risk" element={
                                    <EntitlementGuard resource="feature" requiredId="risk_management">
                                        <PlaceholderPage title="Risk Management" />
                                    </EntitlementGuard>
                                } />
                                <Route path="vendors" element={
                                    <EntitlementGuard resource="feature" requiredId="vendor_management">
                                        <PlaceholderPage title="Vendors" />
                                    </EntitlementGuard>
                                } />

                                {/* GOVERNANCE */}
                                <Route path="governance/context" element={<ContextPage />} />

                                {/* SETTINGS MODULE */}
                                <Route path="settings" element={<SettingsLayout />}>
                                    <Route path=":section" element={<SettingsForm />} />
                                </Route>

                                {/* REPORTS */}
                                <Route path="reports" element={<ReportsDashboard />} />
                                <Route path="trust-report" element={<ReportsDashboard />} />

                                {/* MANAGE */}
                                <Route path="people" element={
                                    <EntitlementGuard resource="feature" requiredId="people_management">
                                        <PeopleDirectory />
                                    </EntitlementGuard>
                                } />
                                <Route path="people/risks" element={<IdentityRiskDashboard />} />
                                <Route path="groups" element={<PlaceholderPage title="Groups" />} />
                                <Route path="computers" element={<PlaceholderPage title="Computers" />} />
                                <Route path="checklists" element={<PlaceholderPage title="Checklists" />} />
                                <Route path="access" element={<PlaceholderPage title="Access" />} />
                                <Route path="access-reviews" element={<PlaceholderPage title="Access Reviews" />} />

                                {/* SOA PREVIEW */}
                                <Route path="soa-preview" element={<StatementOfApplicability />} />

                                {/* AUDITOR PORTAL (Waitlist link in Sidebar) */}
                                <Route path="auditor-portal" element={<InitiationWizard />} />
                                <Route path="auditor-portal/dashboard" element={<AuditorDashboard />} />

                                {/* ADMIN USER MANAGEMENT */}
                                <Route path="admin/users" element={<UserManagement />} />

                                {/* ADMIN INBOX */}
                                <Route path="admin/inbox" element={<AdminInbox />} />
                            </Route>

                            {/* PRINT LAYOUT (No Sidebar) */}
                            <Route
                                path="/print/policy/:id"
                                element={
                                    <ProtectedRoute>
                                        <PrintLayout />
                                    </ProtectedRoute>
                                }
                            />

                            {/* AUDITOR PORTAL (No Sidebar) */}
                            <Route
                                path="/auditor-portal"
                                element={
                                    <ProtectedRoute>
                                        <InitiationWizard />
                                    </ProtectedRoute>
                                }
                            />
                            <Route
                                path="/auditor-portal/dashboard"
                                element={
                                    <ProtectedRoute>
                                        <AuditorDashboard />
                                    </ProtectedRoute>
                                }
                            />

                            {/* UNAUTHORIZED PAGE */}
                            <Route path="/unauthorized" element={<Unauthorized />} />

                            {/* FALLBACK */}
                            <Route path="/" element={<Navigate to="/login" replace />} />
                            <Route path="*" element={<Navigate to="/login" replace />} />
                        </Routes>
                    </EntitlementProvider>
                </Router>
            </AuthProvider>
        </ErrorBoundary >
    );
}

export default App;
