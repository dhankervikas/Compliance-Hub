import React from 'react';
import { useParams, Navigate } from 'react-router-dom';
import { useEntitlements } from '../contexts/EntitlementContext';

const EntitlementGuard = ({ children, resource = 'framework', requiredId }) => {
    const { id } = useParams();
    const { hasFramework, hasFeature, loading } = useEntitlements();

    if (loading) {
        return <div className="p-8 text-center text-gray-500">Verifying access...</div>;
    }

    if (resource === 'framework') {
        const targetId = requiredId || id;
        const isAllowed = hasFramework(targetId);
        if (!isAllowed) {
            console.warn(`Access denied to framework ${targetId}. Redirecting to dashboard.`);
            return <Navigate to="../dashboard" replace />;
        }
    }

    if (resource === 'feature') {
        const isAllowed = hasFeature(requiredId);
        if (!isAllowed) {
            console.warn(`Access denied to feature ${requiredId}. Redirecting to dashboard.`);
            return <Navigate to="../dashboard" replace />;
        }
    }

    return children;
};

export default EntitlementGuard;
