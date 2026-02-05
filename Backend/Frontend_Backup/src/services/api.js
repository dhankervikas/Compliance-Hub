// src/services/api.js
import axios from 'axios';

// Base API URL - your backend server
const API_BASE_URL = 'http://localhost:8000/api/v1';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - Add auth token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - Handle errors globally
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid - clear auth and redirect to login
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ==================== AUTH API ====================

export const authAPI = {
  // Register new user
  register: async (username, email, password) => {
    const response = await api.post('/auth/register', {
      username,
      email,
      password,
    });
    return response.data;
  },

  // Login user
  login: async (username, password) => {
    // FastAPI OAuth2 expects form data for login
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    const response = await axios.post(
      `${API_BASE_URL}/auth/login`,
      formData,
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      }
    );

    // Store token
    const { access_token } = response.data;
    localStorage.setItem('access_token', access_token);

    // Fetch user info with the token
    const userResponse = await api.get('/auth/me');
    localStorage.setItem('user', JSON.stringify(userResponse.data));

    return { access_token, user: userResponse.data };
  },

  // Get current user
  getCurrentUser: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },

  // Logout
  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
  },

  // Check if user is authenticated
  isAuthenticated: () => {
    return !!localStorage.getItem('access_token');
  },

  // Get stored user
  getStoredUser: () => {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  },
};

// ==================== FRAMEWORKS API ====================

export const frameworksAPI = {
  // Get all frameworks
  getAll: async () => {
    const response = await api.get('/frameworks/');
    return response.data;
  },

  // Get framework by ID
  getById: async (id) => {
    const response = await api.get(`/frameworks/${id}`);
    return response.data;
  },

  // Get framework statistics
  getStats: async (id) => {
    const response = await api.get(`/frameworks/${id}/stats`);
    return response.data;
  },
};

// ==================== CONTROLS API ====================

export const controlsAPI = {
  // Get all controls with optional filters
  getAll: async (params = {}) => {
    const response = await api.get('/controls/', { params });
    return response.data;
  },

  // Get control by ID
  getById: async (id) => {
    const response = await api.get(`/controls/${id}`);
    return response.data;
  },

  // Update control
  update: async (id, data) => {
    const response = await api.put(`/controls/${id}`, data);
    return response.data;
  },

  // Get controls by framework
  getByFramework: async (frameworkId) => {
    const response = await api.get('/controls/', {
      params: { framework_id: frameworkId },
    });
    return response.data;
  },

  // Search controls
  search: async (query) => {
    const response = await api.get('/controls/', {
      params: { search: query },
    });
    return response.data;
  },

  // Get controls by status
  getByStatus: async (status) => {
    const response = await api.get('/controls/', {
      params: { status: status },
    });
    return response.data;
  },
};

// ==================== EVIDENCE API ====================

export const evidenceAPI = {
  // Get all evidence
  getAll: async (params = {}) => {
    const response = await api.get('/evidence/', { params });
    return response.data;
  },

  // Get evidence by control ID
  getByControl: async (controlId) => {
    const response = await api.get('/evidence/', {
      params: { control_id: controlId },
    });
    return response.data;
  },

  // Create evidence (without file upload for now)
  create: async (data) => {
    const response = await api.post('/evidence/', data);
    return response.data;
  },

  // Delete evidence
  delete: async (id) => {
    const response = await api.delete(`/evidence/${id}`);
    return response.data;
  },

  // Upload file (to be implemented with multipart/form-data)
  uploadFile: async (controlId, file, description = '') => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('control_id', controlId);
    formData.append('description', description);

    const response = await api.post('/evidence/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
};

// ==================== AUTOMATED TESTS API ====================

export const automationAPI = {
  // Run all automated tests
  runAll: async () => {
    const response = await api.post('/automated-tests/run-all');
    return response.data;
  },

  // Get list of available tests
  getAvailable: async () => {
    const response = await api.get('/automated-tests/available-tests');
    return response.data;
  },

  // Check specific control
  checkControl: async (controlId) => {
    const response = await api.get(`/automated-tests/control/${controlId}/has-test`);
    return response.data;
  },
};

// ==================== DASHBOARD API ====================

export const dashboardAPI = {
  // Get overall statistics
  getOverallStats: async () => {
    try {
      // Fetch both frameworks' stats
      const [iso27001Stats, iso27001ISMSStats] = await Promise.all([
        frameworksAPI.getStats(1), // ISO 27001 Annex A
        frameworksAPI.getStats(3), // ISO 27001 ISMS
      ]);

      // Calculate combined statistics
      const totalControls = (iso27001Stats.total_controls || 0) + (iso27001ISMSStats.total_controls || 0);
      const implementedControls = (iso27001Stats.implemented_controls || 0) + (iso27001ISMSStats.implemented_controls || 0);
      const inProgressControls = (iso27001Stats.in_progress_controls || 0) + (iso27001ISMSStats.in_progress_controls || 0);
      const notStartedControls = (iso27001Stats.not_started_controls || 0) + (iso27001ISMSStats.not_started_controls || 0);

      const overallCompletion = Math.round((implementedControls / totalControls) * 100);

      return {
        totalControls,
        implementedControls,
        inProgressControls,
        notStartedControls,
        overallCompletion,
        frameworks: {
          iso27001: {
            ...iso27001Stats,
            status_counts: {
              implemented: iso27001Stats.implemented_controls || 0,
              in_progress: iso27001Stats.in_progress_controls || 0,
              not_started: iso27001Stats.not_started_controls || 0,
            }
          },
          iso27001ISMS: {
            ...iso27001ISMSStats,
            status_counts: {
              implemented: iso27001ISMSStats.implemented_controls || 0,
              in_progress: iso27001ISMSStats.in_progress_controls || 0,
              not_started: iso27001ISMSStats.not_started_controls || 0,
            }
          },
        },
      };
    } catch (error) {
      console.error('Error fetching dashboard stats:', error);
      throw error;
    }
  },

  // Get recent evidence uploads
  getRecentEvidence: async (limit = 10) => {
    const evidence = await evidenceAPI.getAll();
    // Sort by creation date (most recent first) and limit
    return evidence
      .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
      .slice(0, limit);
  },
};

// Export the axios instance for custom requests
export default api;