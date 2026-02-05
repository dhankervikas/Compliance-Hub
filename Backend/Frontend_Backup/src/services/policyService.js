import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1';

const getPolicies = async () => {
    const response = await axios.get(`${API_URL}/policies/`);
    return response.data;
};

const getPolicy = async (id) => {
    const response = await axios.get(`${API_URL}/policies/${id}`);
    return response.data;
};

const analyzeControl = async (controlId) => {
    const response = await axios.post(`${API_URL}/assessments/analyze/${controlId}`);
    return response.data;
};

export default {
    getPolicies,
    getPolicy,
    analyzeControl
};
