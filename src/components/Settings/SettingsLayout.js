import React from 'react';
import { NavLink, Outlet, useLocation, Navigate } from 'react-router-dom';
import {
    Building, Globe, Server, Shield, Lock, Users,
    Briefcase, Activity, RefreshCw, FileText
} from 'lucide-react';

const SettingsLayout = () => {
    const location = useLocation();

    // The 10 Sections defined in Architecture
    const sections = [
        { id: 'org_profile', label: 'Organization Profile', icon: Building },
        { id: 'scope', label: 'Framework Scope', icon: Globe },
        { id: 'tech_stack', label: 'Technology & Hosting', icon: Server },
        { id: 'data_privacy', label: 'Data & Privacy', icon: Shield },
        { id: 'access_identity', label: 'Access & Identity', icon: Lock },
        { id: 'hr_security', label: 'People & HR Security', icon: Users },
        { id: 'vendors', label: 'Suppliers (Vendors)', icon: Briefcase },
        { id: 'sec_ops', label: 'Security Operations', icon: Activity },
        { id: 'bcp_dr', label: 'Business Continuity', icon: RefreshCw },
        { id: 'doc_preferences', label: 'Document Preferences', icon: FileText },
    ];

    // Redirect to first section if at root /settings
    if (location.pathname === '/settings' || location.pathname === '/settings/') {
        return <Navigate to="/settings/org_profile" replace />;
    }

    return (
        <div className="flex h-[calc(100vh-64px)] overflow-hidden bg-gray-50">
            {/* Left Settings Nav */}
            <div className="w-64 bg-white border-r border-gray-200 overflow-y-auto">
                <div className="p-4 border-b border-gray-100">
                    <h2 className="text-sm font-bold text-gray-900 uppercase tracking-wider">
                        Compliance Profile
                    </h2>
                    <p className="text-xs text-gray-500 mt-1">
                        Single source of truth for generation
                    </p>
                </div>
                <nav className="p-2 space-y-1">
                    {sections.map((section) => (
                        <NavLink
                            key={section.id}
                            to={`/settings/${section.id}`}
                            className={({ isActive }) =>
                                `flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md transition-colors ${isActive
                                    ? 'bg-blue-50 text-blue-700'
                                    : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900'
                                }`
                            }
                        >
                            <section.icon className={`w-4 h-4 ${location.pathname.includes(section.id) ? 'text-blue-600' : 'text-gray-400'}`} />
                            {section.label}
                        </NavLink>
                    ))}
                </nav>
            </div>

            {/* Main Content Area */}
            <div className="flex-1 overflow-auto p-8">
                <div className="max-w-4xl mx-auto">
                    <Outlet />
                </div>
            </div>
        </div>
    );
};

export default SettingsLayout;
