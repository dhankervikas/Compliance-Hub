import axios from 'axios';
import config from '../config';

const API_URL = config.API_BASE_URL + '/ai'; // Correctly append /ai path


const OPENAI_API_URL = 'https://api.openai.com/v1/chat/completions';

export const AIService = {
    /**
     * Generates a policy document based on the control details.
     * @param {string} controlTitle - e.g. "A.5.15 - Access Control"
     * @param {string} description - e.g. "Rules to control physical and logical access..."
     * @returns {Promise<string>} - The generated markdown policy.
     */
    generatePolicy: async (controlTitle, description) => {
        const apiKey = process.env.REACT_APP_OPENAI_API_KEY;

        if (!apiKey) {
            throw new Error("Missing API Key. Please add REACT_APP_OPENAI_API_KEY to your .env file.");
        }

        try {
            const prompt = `
            You are a Chief Information Security Officer (CISO) writing a formal compliance policy.
            
            Write a detailed, professional policy section for the following control:
            Control: "${controlTitle}"
            Description: "${description}"
            
            Format: Markdown
            Structure:
            1. Purpose
            2. Scope
            3. Policy Statement (Detailed rules)
            4. Enforcement
            
            Keep it concise but compliant with ISO 27001 / SOC 2 standards.
            `;

            const response = await axios.post(
                OPENAI_API_URL,
                {
                    model: "gpt-4o", // or gpt-3.5-turbo if preferred
                    messages: [{ role: "user", content: prompt }],
                    temperature: 0.7,
                },
                {
                    headers: {
                        'Authorization': `Bearer ${apiKey}`,
                        'Content-Type': 'application/json',
                    },
                }
            );

            return response.data.choices[0].message.content;
        } catch (error) {
            console.error("AI Generation Failed:", error);
            if (error.response?.status === 401) {
                throw new Error("Invalid OpenAI API Key.");
            }
            throw new Error("Failed to generate policy. Please try again.");
        }
    },

    /**
     * Analyzes a control to determine specifically what evidence is required.
     * Uses Backend Proxy to avoid exposing API Key.
     * @returns {Promise<Object>} - { requirements: [{ name, type, reasoning }] }
     */
    analyzeControlRequirements: async (controlTitle, description, category = "General", controlId = null) => {
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
                    control_id: controlId
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
