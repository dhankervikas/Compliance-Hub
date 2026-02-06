import axios from 'axios';
import config from '../config';

const API_URL = config.API_BASE_URL + '/ai'; // Correctly append /ai path


// const OPENAI_API_URL = 'https://api.openai.com/v1/chat/completions'; // comment it out

export const AIService = {
    /**
     * Generates a policy document based on the control details.
     * @param {string} controlTitle - e.g. "A.5.15 - Access Control"
     * @param {string} description - e.g. "Rules to control physical and logical access..."
     * @returns {Promise<string>} - The generated markdown policy.
     */
    generatePolicy: async (controlTitle, description) => {
        try {
            const token = localStorage.getItem('token');
            const headers = token ? { 'Authorization': `Bearer ${token}` } : {};

            const response = await axios.post(
                `${API_URL}/generate-policy`,
                {
                    title: controlTitle,
                    description: description
                },
                { headers }
            );

            return response.data.content;
        } catch (error) {
            console.error("AI Generation Failed:", error);
            throw new Error("Failed to generate policy. Please try again.");
        }
    },

    /**
     * Analyzes a control to determine specifically what evidence is required.
     * Uses Backend Proxy to avoid exposing API Key.
     * @returns {Promise<Object>} - { requirements: [{ name, type, reasoning }] }
     */
    analyzeControlRequirements: async (controlTitle, description, category = "General", controlId = null, regenerate = false) => {
        try {
            const token = localStorage.getItem('token');
            // Allow public access or use token if available
            const headers = token ? { 'Authorization': `Bearer ${token}` } : {};

            const response = await axios.post(
                `${API_URL}/suggest-evidence`,
                {
                    title: controlTitle,
                    description: description,
                    category: category,
                    control_id: controlId,
                    regenerate: regenerate
                },
                { headers }
            );

            return response.data;
        } catch (error) {
            console.error("AI Analysis Failed:", error);
            return null;
        }
    },

    /**
     * Compares required evidence vs uploaded files to determine status.
     */
    evaluateGapAnalysis: async (controlTitle, requirements, uploadedFiles) => {
        try {
            const token = localStorage.getItem('token');
            const headers = token ? { 'Authorization': `Bearer ${token}` } : {};

            const response = await axios.post(
                `${API_URL}/gap-analysis`,
                {
                    control_title: controlTitle,
                    requirements: requirements,
                    uploaded_files: uploadedFiles.map(f => f.title || f.name)
                },
                { headers }
            );

            return response.data;
        } catch (error) {
            console.error("Gap Analysis Failed:", error);
            return null;
        }
    },

    /**
     * Generates a specific artifact (Policy, Report, etc.) for a requirement.
     */
    generateArtifact: async (controlTitle, artifactName, context) => {
        try {
            const token = localStorage.getItem('token');
            const headers = token ? { 'Authorization': `Bearer ${token}` } : {};

            const response = await axios.post(
                `${API_URL}/generate-artifact`,
                {
                    control_title: controlTitle,
                    artifact_name: artifactName,
                    context: context
                },
                { headers }
            );

            return response.data.content;
        } catch (error) {
            console.error("Artifact Generation Failed:", error);
            throw error;
        }
    },

    /**
     * Reviews a specific document against control requirements.
     */
    reviewDocument: async (controlId, evidenceId) => {
        try {
            const token = localStorage.getItem('token');
            const headers = token ? { 'Authorization': `Bearer ${token}` } : {};

            const response = await axios.post(
                `${API_URL}/review-document`,
                {
                    control_id: controlId,
                    evidence_id: evidenceId
                },
                { headers }
            );

            return response.data;
        } catch (error) {
            console.error("Document Review Failed:", error);
            throw error;
        }
    }
};
