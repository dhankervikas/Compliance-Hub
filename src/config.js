// Centralized configuration for the application
// Usage: import config from '../config'; const url = config.API_BASE_URL;
const getBaseUrl = () => {
    let url = process.env.REACT_APP_API_BASE_URL;

    // 1. If env var is set, sanitize it
    if (url) {
        url = url.replace(/\/+$/, ''); // Remove trailing slashes
        // Avoid double /api/v1 if user accidentally included it
        if (url.endsWith('/api/v1')) {
            return url;
        }
        return `${url}/api/v1`;
    }

    // 2. Fallback for Localhost
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        return '/api/v1';
    }

    // 3. Fallback for Production (Hardcoded AWS)
    return 'https://w7rnfgfmhu.us-east-1.awsapprunner.com/api/v1';
};

const config = {
    API_BASE_URL: getBaseUrl()
};
export default config;