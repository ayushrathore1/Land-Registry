/**
 * API Client - Handles all HTTP requests to the backend
 */

const API = {
    // Use CONFIG if available, fallback to localhost
    baseURL: (window.CONFIG && window.CONFIG.API_URL) || 'http://localhost:8000/api',
    token: null,

    /**
     * Set authentication token
     */
    setToken(token) {
        this.token = token;
        localStorage.setItem('auth_token', token);
    },

    /**
     * Get stored token
     */
    getToken() {
        if (!this.token) {
            this.token = localStorage.getItem('auth_token');
        }
        return this.token;
    },

    /**
     * Clear authentication
     */
    clearAuth() {
        this.token = null;
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user_data');
    },

    /**
     * Make HTTP request
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        // Add auth header if token exists
        const token = this.getToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        try {
            const response = await fetch(url, {
                ...options,
                headers
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Request failed');
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },

    /**
     * GET request
     */
    async get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    },

    /**
     * POST request
     */
    async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    /**
     * PUT request
     */
    async put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },

    // ========================================
    // Authentication
    // ========================================

    async login(username, password) {
        const data = await this.post('/auth/login', { username, password });
        this.setToken(data.access_token);
        localStorage.setItem('user_data', JSON.stringify(data.user));
        return data;
    },

    async verifyToken() {
        return this.get('/auth/verify');
    },

    async logout() {
        this.clearAuth();
        return { success: true };
    },

    // ========================================
    // Search
    // ========================================

    async searchByPlotId(query, limit = 20) {
        return this.get(`/search/plot?q=${encodeURIComponent(query)}&limit=${limit}`);
    },

    async searchByOwnerName(query, limit = 20) {
        return this.get(`/search/owner?q=${encodeURIComponent(query)}&limit=${limit}`);
    },

    async getParcelByPlotId(plotId) {
        return this.get(`/search/plot/${encodeURIComponent(plotId)}`);
    },

    async getVillages() {
        return this.get('/search/villages');
    },

    async getParcelsByVillage(villageName) {
        return this.get(`/search/village/${encodeURIComponent(villageName)}`);
    },

    // ========================================
    // Parcels
    // ========================================

    async getAllParcels(page = 1, perPage = 50) {
        return this.get(`/parcels?page=${page}&per_page=${perPage}`);
    },

    async getGeoJSON() {
        return this.get('/parcels/geojson');
    },

    async getVillageGeoJSON(village) {
        return this.get(`/parcels/geojson/${encodeURIComponent(village)}`);
    },

    async getParcel(plotId) {
        return this.get(`/parcels/${encodeURIComponent(plotId)}`);
    },

    async updateParcel(plotId, updates) {
        return this.put(`/parcels/${encodeURIComponent(plotId)}`, updates);
    },

    // ========================================
    // Reconciliation
    // ========================================

    async getReconciliationStats() {
        return this.get('/reconciliation/stats');
    },

    async getMismatches(threshold = 85, village = null) {
        let url = `/reconciliation/mismatches?threshold=${threshold}`;
        if (village) {
            url += `&village=${encodeURIComponent(village)}`;
        }
        return this.get(url);
    },

    async getComparisons(status = null, village = null) {
        let url = '/reconciliation/compare?';
        const params = [];
        if (status) params.push(`status=${status}`);
        if (village) params.push(`village=${encodeURIComponent(village)}`);
        return this.get(url + params.join('&'));
    },

    async getReconciliationReport() {
        return this.get('/reconciliation/report');
    },

    async checkParcel(plotId) {
        return this.get(`/reconciliation/check/${encodeURIComponent(plotId)}`);
    },

    async exportReport() {
        return this.get('/reconciliation/report/export');
    },

    // ========================================
    // Statistics
    // ========================================

    async getStats() {
        return this.get('/stats');
    }
};

// Export for use in other modules
window.API = API;
