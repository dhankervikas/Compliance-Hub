
import axios from 'axios';

import config from '../config';

const API_URL = config.API_BASE_URL;

const getAuthHeaders = () => {
    const token = localStorage.getItem('token');
    return { Authorization: `Bearer ${token}` };
};

export const auditService = {
    initiateAudit: async (data) => {
        const response = await axios.post(`${API_URL}/audits/initiate`, data, { headers: getAuthHeaders() });
        return response.data;
    },

    getEvidence: async () => {
        const response = await axios.get(`${API_URL}/audits/evidence`, { headers: getAuthHeaders() });
        return response.data;
    },

    reviewEvidence: async (evidenceId, payload) => {
        const response = await axios.post(
            `${API_URL}/audits/evidence/${evidenceId}/review`,
            payload,
            { headers: getAuthHeaders() }
        );
        return response.data;
    },

    getStats: async () => {
        const response = await axios.get(`${API_URL}/audits/stats`, { headers: getAuthHeaders() });
        return response.data;
    }
};
