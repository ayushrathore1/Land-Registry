/**
 * Main Application Controller
 */

const App = {
    selectedPlotId: null,

    /**
     * Initialize the application
     */
    async init() {
        console.log('🚀 Initializing Land Record Digitization Tool...');

        try {
            // Initialize managers
            AuthManager.init();
            SearchManager.init();
            EditManager.init();
            ReportManager.init();
            await MapManager.init();

            // Set up callbacks
            this.setupCallbacks();

            // Load initial data
            await this.loadVillages();
            await this.loadStats();

            // Bind global events
            this.bindEvents();

            console.log('✅ Application initialized successfully');

        } catch (error) {
            console.error('❌ Failed to initialize application:', error);
            this.showToast('Failed to initialize application', 'error');
        }
    },

    /**
     * Set up manager callbacks
     */
    setupCallbacks() {
        // Map parcel selection
        MapManager.onParcelSelect = (plotId) => {
            this.showParcelDetails(plotId);
        };

        // Search result selection
        SearchManager.onResultSelect = (plotId) => {
            this.showParcelDetails(plotId);
        };

        // Auth change
        AuthManager.onAuthChange = () => {
            this.updateEditButtons();
        };
    },

    /**
     * Bind global UI events
     */
    bindEvents() {
        // Close detail panel
        document.getElementById('closeDetailBtn')?.addEventListener('click', () => {
            this.hideParcelDetails();
        });
    },

    /**
     * Load villages list
     */
    async loadVillages() {
        try {
            const response = await API.getVillages();
            const container = document.getElementById('villageList');

            // Get parcel counts per village
            const parcelsResponse = await API.getAllParcels(1, 500);
            const villageCounts = {};
            parcelsResponse.parcels.forEach(p => {
                const village = p.properties?.village;
                if (village) {
                    villageCounts[village] = (villageCounts[village] || 0) + 1;
                }
            });

            const html = response.villages.map(village => `
                <div class="village-item" data-village="${village}">
                    <span class="village-name">${village}</span>
                    <span class="parcel-count">${villageCounts[village] || 0}</span>
                </div>
            `).join('');

            container.innerHTML = html;

            // Bind click events
            container.querySelectorAll('.village-item').forEach(item => {
                item.addEventListener('click', () => {
                    const village = item.dataset.village;
                    this.selectVillage(village, item);
                });
            });

        } catch (error) {
            console.error('Error loading villages:', error);
        }
    },

    /**
     * Select a village
     */
    selectVillage(villageName, element) {
        // Update UI
        document.querySelectorAll('.village-item').forEach(item => {
            item.classList.remove('active');
        });
        element?.classList.add('active');

        // Zoom map to village
        MapManager.zoomToVillage(villageName);
    },

    /**
     * Load statistics
     */
    async loadStats() {
        try {
            // Get overall stats
            const stats = await API.getStats();
            document.getElementById('totalParcels').textContent = stats.total_parcels;

            // Get reconciliation stats
            const reconStats = await API.getReconciliationStats();
            document.getElementById('matchRate').textContent = reconStats.match_rate;
            document.getElementById('matchedCount').textContent = reconStats.matched;
            document.getElementById('partialCount').textContent = reconStats.partial_matches;
            document.getElementById('mismatchCount').textContent = reconStats.mismatches;

        } catch (error) {
            console.error('Error loading stats:', error);
        }
    },

    /**
     * Show parcel details in the detail panel
     */
    async showParcelDetails(plotId) {
        this.selectedPlotId = plotId;

        try {
            // Show panel
            document.getElementById('detailPanel').classList.add('active');

            // Show loading
            document.getElementById('detailContent').innerHTML = `
                <div class="loading">
                    <div class="spinner"></div>
                </div>
            `;

            // Fetch data
            const parcel = await API.getParcel(plotId);
            const comparison = await API.checkParcel(plotId);

            // Update title
            document.getElementById('detailTitle').textContent = plotId;

            // Render content
            this.renderParcelDetails(parcel, comparison);

        } catch (error) {
            console.error('Error loading parcel details:', error);
            document.getElementById('detailContent').innerHTML = `
                <div class="empty-state">
                    <p style="color: var(--danger);">Failed to load details</p>
                </div>
            `;
        }
    },

    /**
     * Render parcel details content
     */
    renderParcelDetails(parcel, comparison) {
        const textual = parcel.textual_record || {};
        const spatial = parcel.spatial_attributes || {};
        const props = parcel.properties || {};
        const nameAnalysis = comparison.comparison?.name_analysis || {};

        const scoreClass = nameAnalysis.similarity_score >= 85 ? 'high' :
                          nameAnalysis.similarity_score >= 60 ? 'medium' : 'low';

        const html = `
            <div class="detail-section">
                <h4>Basic Information</h4>
                <div class="detail-grid">
                    <div class="detail-item">
                        <label>Village</label>
                        <div class="value">${props.village || '-'}</div>
                    </div>
                    <div class="detail-item">
                        <label>Survey No.</label>
                        <div class="value">${props.survey_no || '-'}</div>
                    </div>
                    <div class="detail-item">
                        <label>Area</label>
                        <div class="value">${textual.area || props.area_sqm} sq.m</div>
                    </div>
                    <div class="detail-item">
                        <label>Land Type</label>
                        <div class="value">${textual.land_type || '-'}</div>
                    </div>
                </div>
            </div>

            <div class="detail-section">
                <h4>Owner Information (Textual Record)</h4>
                <div class="detail-grid">
                    <div class="detail-item full-width">
                        <label>Owner Name</label>
                        <div class="value highlight">${textual.owner_name || '-'}</div>
                    </div>
                    <div class="detail-item full-width">
                        <label>Father's Name</label>
                        <div class="value">${textual.father_name || '-'}</div>
                    </div>
                    <div class="detail-item full-width">
                        <label>Registration Date</label>
                        <div class="value">${textual.registration_date || '-'}</div>
                    </div>
                </div>
            </div>

            <div class="detail-section">
                <h4>Comparison Analysis</h4>
                <div class="comparison-box">
                    <div class="comparison-row">
                        <span class="comparison-label">Owner</span>
                        <div class="comparison-values">
                            <span class="comparison-value textual">${nameAnalysis.textual_name || '-'}</span>
                            <span class="comparison-value spatial">${nameAnalysis.spatial_name || '-'}</span>
                        </div>
                    </div>
                    <div class="similarity-meter">
                        <div class="meter-label">
                            <span>Similarity Score</span>
                            <span class="score-value">${nameAnalysis.similarity_score || 0}%</span>
                        </div>
                        <div class="meter-bar">
                            <div class="meter-fill ${scoreClass}" 
                                 style="width: ${nameAnalysis.similarity_score || 0}%"></div>
                        </div>
                    </div>
                </div>
                <div class="status-badge ${nameAnalysis.status || 'unknown'}">
                    ${nameAnalysis.status_label || 'No comparison data'}
                </div>
            </div>

            <div class="detail-actions">
                <button class="btn btn-primary" id="editRecordBtn" 
                        ${!AuthManager.hasRole('editor') ? 'disabled' : ''}>
                    Edit Record
                </button>
                <button class="btn btn-secondary" id="viewOnMapBtn">
                    Center on Map
                </button>
            </div>
        `;

        document.getElementById('detailContent').innerHTML = html;

        // Bind action buttons
        document.getElementById('editRecordBtn')?.addEventListener('click', () => {
            EditManager.showEditModal(this.selectedPlotId);
        });

        document.getElementById('viewOnMapBtn')?.addEventListener('click', () => {
            MapManager.highlightParcel(this.selectedPlotId);
        });
    },

    /**
     * Hide parcel details panel
     */
    hideParcelDetails() {
        document.getElementById('detailPanel').classList.remove('active');
        this.selectedPlotId = null;
    },

    /**
     * Update edit buttons based on auth state
     */
    updateEditButtons() {
        const editBtn = document.getElementById('editRecordBtn');
        if (editBtn) {
            editBtn.disabled = !AuthManager.hasRole('editor');
        }
    },

    /**
     * Show toast notification
     */
    showToast(message, type = 'success') {
        const container = document.getElementById('toastContainer');
        
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const icon = type === 'success' ? '✓' : type === 'error' ? '✕' : '!';
        
        toast.innerHTML = `
            <span class="toast-icon">${icon}</span>
            <span class="toast-message">${message}</span>
        `;

        container.appendChild(toast);

        // Auto remove after 4 seconds
        setTimeout(() => {
            toast.style.animation = 'toastSlideIn 0.3s ease reverse';
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    }
};

// Make App globally available
window.App = App;

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    App.init();
});
