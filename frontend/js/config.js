/**
 * API Configuration
 * Set the API URL based on environment
 */

const CONFIG = {
    // Change this to your Render backend URL after deployment
    // Example: 'https://land-records-api.onrender.com/api'
    API_URL: window.location.hostname === 'localhost' 
        ? 'http://localhost:8000/api'
        : 'https://your-render-backend-url.onrender.com/api'
};

// Export for use
window.CONFIG = CONFIG;
