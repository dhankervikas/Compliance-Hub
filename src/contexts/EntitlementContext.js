import React, { createContext, useContext, useState, useEffect, useRef } from 'react';
import api from '../services/api';
import { useAuth } from './AuthContext';

const EntitlementContext = createContext(null);

export const EntitlementProvider = ({ children }) => {
    const { user, token } = useAuth();
    const [entitlements, setEntitlements] = useState(null);
    const [loading, setLoading] = useState(true);
    const fetchedRef = useRef(false);

    useEffect(() => {
        if (!token || !user) {
            setLoading(false);
            setEntitlements(null);
            fetchedRef.current = false;
            return;
        }

        if (fetchedRef.current) return;
        fetchedRef.current = true;

        const doFetch = async () => {
            try {
                const response = await api.get('/users/me/entitlements');
                setEntitlements(response.data);
            } catch (error) {
                console.warn("EntitlementContext: fetch failed, using fallback");
                setEntitlements({ frameworks: [], features: [], account_status: 'unknown' });
            } finally {
                setLoading(false);
            }
        };

        doFetch();
    }, [token, user]);

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

    const refreshEntitlements = async () => {
        fetchedRef.current = false;
        try {
            const response = await api.get('/users/me/entitlements');
            setEntitlements(response.data);
        } catch (error) {
            console.warn("EntitlementContext: refresh failed");
        }
    };

    return (
        <EntitlementContext.Provider value={{ entitlements, loading, hasFeature, hasFramework, isFrameworkActive, refreshEntitlements }}>
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