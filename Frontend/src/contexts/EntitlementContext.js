import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { useLocation } from 'react-router-dom';
import api from '../services/api';
import { useAuth } from './AuthContext';

const EntitlementContext = createContext(null);

export const EntitlementProvider = ({ children }) => {
    const { user, token } = useAuth();
    const [entitlements, setEntitlements] = useState(null);
    const [loading, setLoading] = useState(true);

    const location = useLocation();

    const fetchEntitlements = useCallback(async () => {
        if (!user || !token) {
            setLoading(false);
            return;
        }

        try {
            // Determine Context from URL
            const match = location.pathname.match(/\/t\/([^/]+)/);
            const tenantId = match ? match[1] : null;

            console.log("EntitlementContext: Debug", { path: location.pathname, tenantId, userRole: user?.role, userTenant: user?.tenant_id });

            let headers = {};
            // If Admin is viewing a specific tenant, inject the header to switch context
            // Relaxed check: logic if tenantId exists and differs from user's tenant
            if (tenantId && user && user.tenant_id !== tenantId) {
                headers['X-Target-Tenant-ID'] = tenantId;
                console.log("EntitlementContext: INJECTING HEADER", headers);
            }

            // Always fetch strictly from /me/entitlements. 
            // The backend verify_tenant dependency handles the context switch via the header.
            const response = await api.get('/users/me/entitlements', { headers });

            console.log("EntitlementContext: Response Data", response.data);

            setEntitlements(response.data);
        } catch (error) {
            console.error("Failed to fetch entitlements:", error);
            // Fallback
            setEntitlements({
                frameworks: [],
                features: [],
                account_status: 'unknown'
            });
        } finally {
            setLoading(false);
        }
    }, [user, token, location.pathname]);

    useEffect(() => {
        if (token) {
            fetchEntitlements();
        } else {
            setLoading(false);
            setEntitlements(null);
        }
    }, [token, fetchEntitlements]);

    // Helpers
    const hasFeature = (featureKey) => {
        if (!entitlements) return false;
        // If Super Admin view? Maybe checking role?
        // But entitlements are tenant-scoped. 
        const feature = entitlements.features.find(f => f.key === featureKey);
        return feature ? feature.is_active : false;
    };

    const hasFramework = (frameworkId) => {
        if (!entitlements) return false;
        const framework = entitlements.frameworks.find(f => f.id === parseInt(frameworkId));
        return framework ? framework.is_active : false;
    };

    const isFrameworkActive = (code) => {
        if (!entitlements) return false;
        const framework = entitlements.frameworks.find(f => f.code === code);
        return framework ? framework.is_active : false;
    }

    const value = {
        entitlements,
        loading,
        hasFeature,
        hasFramework,
        isFrameworkActive,
        refreshEntitlements: fetchEntitlements
    };

    return (
        <EntitlementContext.Provider value={value}>
            {children}
        </EntitlementContext.Provider>
    );
};

export const useEntitlements = () => {
    const context = useContext(EntitlementContext);
    if (!context) {
        throw new Error('useEntitlements must be used within an EntitlementProvider');
    }
    return context;
};
