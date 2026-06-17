const API_BASE = '/api';

class ApiClient {
    constructor() {
        this.token = localStorage.getItem('jnhs_token');
    }

    setToken(token) {
        this.token = token;
        localStorage.setItem('jnhs_token', token);
    }

    clearToken() {
        this.token = null;
        localStorage.removeItem('jnhs_token');
        localStorage.removeItem('jnhs_user');
    }

    getHeaders() {
        const headers = { 'Content-Type': 'application/json' };
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }
        return headers;
    }

    async request(method, endpoint, data = null) {
        const options = {
            method,
            headers: this.getHeaders(),
        };
        if (data && (method === 'POST' || method === 'PUT')) {
            options.body = JSON.stringify(data);
        }
        const response = await fetch(`${API_BASE}${endpoint}`, options);
        if (response.status === 401) {
            this.clearToken();
            window.location.href = '/login.html';
            return null;
        }
        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: 'Request failed' }));
            throw new Error(error.detail || 'Request failed');
        }
        return response.json();
    }

    get(endpoint) { return this.request('GET', endpoint); }
    post(endpoint, data) { return this.request('POST', endpoint, data); }
    put(endpoint, data) { return this.request('PUT', endpoint, data); }
    delete(endpoint) { return this.request('DELETE', endpoint); }
}

const api = new ApiClient();
