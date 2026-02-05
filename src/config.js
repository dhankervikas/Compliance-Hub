
// Centralized configuration for the application
// Usage: import config from '../config'; const url = config.API_BASE_URL;

const config = {
    // Check for environment variable first, callback to localhost for dev
    API_BASE_URL: (process.env.REACT_APP_API_URL || 'http://localhost:8000') + '/api/v1'
};

export default config;
