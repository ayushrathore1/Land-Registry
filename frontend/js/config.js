/**
 * API Configuration
 * Set the API URL based on environment
 */

const CONFIG = {
    // Production: Render backend URL
    // Local: localhost for development
    API_URL: window.location.hostname === 'localhost' 
        ? 'http://localhost:8000/api'
        : 'https://land-records-api.onrender.com/api'
};

// Export for use
window.CONFIG = CONFIG;
