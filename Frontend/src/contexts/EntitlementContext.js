import React, { createContext, useContext, useState, useEffect, useCallback, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import api from '../services/api';
import { useAuth } from './AuthContext';

const EntitlementContext = createContext(null);

export const EntitlementProvider = ({ children }) => {
    const { user, token } = useAuth();
    const [entitlements, setEntitlements] = useState(null);
    const [loading, setLoading] = useState(true);
    const location = useLocation();
    const hasFetched = useRef(false);
    const retryCount = useRef(0);

    const fetchEntitlements = useCallback(async () => {
        if (!user || !token) {
            setLoading(false);
            return;
        }

        // Prevent infinite retries
        if (retryCount.current >= 2) {
            console.warn("EntitlementContext: Max retries reached, using fallback");
            setEntitlements({ frameworks: [], features: [], account_status: 'unknown' });
            setLoading(false);
            return;
        }

        try {
            const match = location.pathname.match(/\/t\/([^/]+)/);
            const tenantId = match ? match[1] : null;

            let headers = {};
            if (tenantId && user && user.tenant_id !== tenantId) {
                headers['X-Target-Tenant-ID'] = tenantId;
            }

            const response = await api.get('/users/me/entitlements', { headers });
            setEntitlements(response.data);
            hasFetched.current = true;
            retryCount.current = 0;
        } catch (error) {
            console.error("Failed to fetch entitlements:", error);
            retryCount.current += 1;
            setEntitlements({ frameworks: [], features: [], account_status: 'unknown' });
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
            hasFetched.current = false;
            retryCount.current = 0;
        }
    }, [token, fetchEntitlements]);

    const hasFeature = (featureKey) => {
        if (!entitlements) return false;
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
    };

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