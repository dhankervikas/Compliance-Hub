import axios from 'axios';
import config from '../config';

const API_URL = `${config.API_BASE_URL}`;

export const auditService = {
    // --- EVIDENCE API ---
    getEvidence: async () => {
        const token = localStorage.getItem('token');
        const tenantId = localStorage.getItem('tenant_id'); // Ensure Context
        const headers = { Authorization: `Bearer ${token}` };
        if (tenantId) headers['X-Target-Tenant-ID'] = tenantId;

        const res = await axios.get(`${API_URL}/evidence`, { headers });
        return res.data;
    },

    reviewEvidence: async (evidenceId, reviewData) => {
        const token = localStorage.getItem('token');
        const res = await axios.put(`${API_URL}/evidence/${evidenceId}/review`, reviewData, {
            headers: { Authorization: `Bearer ${token}` }
        });
        return res.data;
    },

    initiateAudit: async (auditData) => {
        const token = localStorage.getItem('token');
        const res = await axios.post(`${API_URL}/audits/initiate`, auditData, {
            headers: { Authorization: `Bearer ${token}` }
        });
        return res.data;
    },

    // --- SCOPE JUSTIFICATION API (Strict Isolation) ---
    getScopeJustifications: async (standard) => {
        try {
            const token = localStorage.getItem('token');
            const res = await axios.get(`${API_URL}/scope/justifications`, {
                headers: { Authorization: `Bearer ${token}` },
                params: { standard_type: standard } // Strict Server-Side Filter
            });
            return res.data;
        } catch (error) {
            console.error("Failed to fetch scope justifications:", error);
            // Fallback to empty list to prevent crash
            return [];
        }
    },

    saveScopeJustification: async (data) => {
        // data = { standard_type, criteria_id, reason_code, justification_text }
        const token = localStorage.getItem('token');
        const res = await axios.post(`${API_URL}/scope/justifications`, data, {
            headers: { Authorization: `Bearer ${token}` }
        });
        return res.data;
    },

    // --- LEGACY SETTINGS API ---
    getSettings: async (section) => {
        const token = localStorage.getItem('token');
        const res = await axios.get(`${API_URL}/settings/${section}`, {
            headers: { Authorization: `Bearer ${token}` }
        });
        return res.data;
    }
};
