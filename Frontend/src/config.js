
// Centralized configuration for the application
// Usage: import config from '../config'; const url = config.API_BASE_URL;

const config = {
    // Look for Full URL first, then fall back to Proxy
    API_BASE_URL: process.env.REACT_APP_API_BASE_URL
        ? `${process.env.REACT_APP_API_BASE_URL}/api/v1`
        : '/api/v1'
};

export default config;
