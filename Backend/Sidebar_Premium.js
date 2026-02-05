
import React, { useState } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import {
    Home, Shield, FileText, AlertTriangle, Users,
    Settings, LogOut, ChevronDown, ChevronRight,
    BarChart2, Lock, Monitor, Briefcase, File,
    Layers, CheckSquare, HardDrive, Wifi
} from 'lucide-react';

const Sidebar = () => {
    const { user, logout } = useAuth();
    const location = useLocation();

    // Group State (Open/Close) - Default all open
    const [groups, setGroups] = useState({
        overview: true,
        document: true,
        report: true,
        manage: true
    });

    const toggleGroup = (key) => {
        setGroups(prev => ({ ...prev, [key]: !prev[key] }));
    };

    const handleLogout = () => {
        if (window.confirm("Are you sure you want to logout?")) {
            logout();
            window.location.href = '/login';
        }
    };

    // Helper to determine if a group contains the active route
    const isActive = (path) => location.pathname.startsWith(path);

    const navGroups = [
        {
            key: 'overview',
            label: 'OVERVIEW',
            items: [
                { label: 'Dashboard', path: '/dashboard', icon: Home },
                { label: 'Controls', path: '/controls', icon: Shield },
                { label: 'Monitors', path: '/monitors', icon: Monitor },
                { label: 'Get started', path: '/get-started', icon: CheckSquare, badge: '16 of 17' }
            ]
        },
        {
            key: 'document',
            label: 'DOCUMENT',
            items: [
                { label: 'Documents', path: '/documents', icon: File },
                { label: 'Policies', path: '/policies', icon: FileText },
                { label: 'Risk management', path: '/risk', icon: AlertTriangle },
                { label: 'Vendors', path: '/vendors', icon: Briefcase } // Requested by user
            ]
        },
        {
            key: 'report',
            label: 'REPORT',
            items: [
                { label: 'Frameworks', path: '/frameworks', icon: Layers }, // Go to Dashboard/List?
                { label: 'Trust Report', path: '/trust-report', icon: Lock }
            ]
        },
        {
            key: 'manage',
            label: 'MANAGE',
            items: [
                { label: 'People', path: '/people', icon: Users },
                { label: 'Groups', path: '/groups', icon: Users }, // Different icon maybe?
                { label: 'Computers', path: '/computers', icon: HardDrive },
                { label: 'Checklists', path: '/checklists', icon: CheckSquare },
                { label: 'Access', path: '/access', icon: Wifi },
                { label: 'Access reviews', path: '/access-reviews', icon: checkCircleIconOrSimilar() },
                { label: 'Settings', path: '/settings', icon: Settings }
            ]
        }
    ];

    function checkCircleIconOrSimilar() { return CheckSquare; } // fallback

    return (
        <div className="w-64 bg-[#0F172A] text-gray-400 h-screen flex flex-col fixed left-0 top-0 z-[50] overflow-y-auto border-r border-[#1E293B] font-sans text-sm">
            {/* Header */}
            <div className="p-6">
                <div className="flex items-center gap-2 text-white font-bold text-lg">
                    <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                        <Shield className="w-5 h-5 text-white" />
                    </div>
                    AssuRisk
                </div>
            </div>

            {/* Navigation */}
            <div className="flex-1 px-4 space-y-6">
                {navGroups.map(group => (
                    <div key={group.key}>
                        <button
                            onClick={() => toggleGroup(group.key)}
                            className="flex items-center gap-2 w-full text-xs font-bold text-gray-500 uppercase tracking-wider mb-2 hover:text-gray-300"
                        >
                            {groups[group.key] ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
                            {group.label}
                        </button>

                        {groups[group.key] && (
                            <div className="space-y-0.5 ml-2 border-l border-[#1E293B] pl-2">
                                {group.items.map(item => (
                                    <NavLink
                                        key={item.path}
                                        to={item.path}
                                        className={({ isActive }) =>
                                            `flex items-center justify-between px-3 py-2 rounded-md transition-all ${isActive
                                                ? 'bg-blue-600/10 text-blue-400 font-medium'
                                                : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800/50'
                                            }`
                                        }
                                    >
                                        <div className="flex items-center gap-3">
                                            {/* <item.icon size={16} />  -- Minimalist style sometimes omits icons in list? Screenshot has strings. Let's keep icons for polish but small */}
                                            <span>{item.label}</span>
                                        </div>
                                        {item.badge && (
                                            <span className="text-[10px] bg-gray-800 px-1.5 py-0.5 rounded-full text-gray-400">{item.badge}</span>
                                        )}
                                    </NavLink>
                                ))}
                            </div>
                        )}
                    </div>
                ))}
            </div>

            {/* Footer / Profile */}
            <div className="p-4 bg-[#0B1120] border-t border-[#1E293B]">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-blue-500 to-purple-500 flex items-center justify-center text-white text-xs font-bold">
                            {user?.username?.substring(0, 2).toUpperCase() || 'AD'}
                        </div>
                        <div className="flex flex-col">
                            <span className="text-white text-xs font-medium">{user?.username || 'Admin'}</span>
                            <span className="text-gray-500 text-[10px]">Workspace Owner</span>
                        </div>
                    </div>
                    <button onClick={handleLogout} className="text-gray-500 hover:text-white transition-colors">
                        <LogOut size={16} />
                    </button>
                </div>
            </div>
        </div>
    );
};

export default Sidebar;
