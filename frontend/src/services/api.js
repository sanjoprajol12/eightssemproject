/**
 * Centralized API Service for Django REST Framework
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';

async function request(endpoint, options = {}) {
    const token = localStorage.getItem('truthlens_token');
    
    const headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        ...(token ? { 'Authorization': `Token ${token}` } : {}),
        ...options.headers,
    };

    const config = {
        ...options,
        headers,
    };

    if (config.body && typeof config.body === 'object') {
        config.body = JSON.stringify(config.body);
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, config);

    if (response.status === 401) {
        localStorage.removeItem('truthlens_token');
        localStorage.removeItem('truthlens_user');
        if (!window.location.pathname.includes('/login')) {
            window.location.href = '/login';
        }
    }

    if (response.status === 204) {
        return null;
    }

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
        const error = new Error(data.message || data.detail || 'An error occurred');
        error.data = data;
        error.status = response.status;
        throw error;
    }

    return data;
}

export const api = {
    // Auth endpoints
    register: (data) => request('/auth/register/', { method: 'POST', body: data }),
    login: (credentials) => request('/auth/login/', { method: 'POST', body: credentials }),
    logout: () => request('/auth/logout/', { method: 'POST' }),
    getMe: () => request('/auth/me/'),
    updateMe: (data) => request('/auth/me/', { method: 'PUT', body: data }),

    // User endpoints
    getUsers: (params = '') => request(`/auth/users/${params ? `?${params}` : ''}`),
    createUser: (data) => request('/auth/users/', { method: 'POST', body: data }),
    updateUser: (id, data) => request(`/auth/users/${id}/`, { method: 'PUT', body: data }),
    deleteUser: (id) => request(`/auth/users/${id}/`, { method: 'DELETE' }),

    // CMS Stats
    getCmsStats: () => request('/cms/stats/'),

    // Generic CMS CRUD
    list: (resource, params = '') => request(`/cms/${resource}/${params ? `?${params}` : ''}`),
    get: (resource, id) => request(`/cms/${resource}/${id}/`),
    create: (resource, data) => request(`/cms/${resource}/`, { method: 'POST', body: data }),
    update: (resource, id, data) => request(`/cms/${resource}/${id}/`, { method: 'PUT', body: data }),
    patch: (resource, id, data) => request(`/cms/${resource}/${id}/`, { method: 'PATCH', body: data }),
    delete: (resource, id) => request(`/cms/${resource}/${id}/`, { method: 'DELETE' }),
};
