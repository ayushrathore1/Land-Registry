/**
 * Map Manager - Handles Leaflet map interactions
 */

const MapManager = {
    map: null,
    parcelsLayer: null,
    selectedLayer: null,
    comparisonData: {},
    onParcelSelect: null,

    // Style configuration
    styles: {
        match: {
            color: '#10b981',
            fillColor: '#10b981',
            fillOpacity: 0.3,
            weight: 2
        },
        partial: {
            color: '#f59e0b',
            fillColor: '#f59e0b',
            fillOpacity: 0.3,
            weight: 2
        },
        mismatch: {
            color: '#ef4444',
            fillColor: '#ef4444',
            fillOpacity: 0.3,
            weight: 2
        },
        default: {
            color: '#3b82f6',
            fillColor: '#3b82f6',
            fillOpacity: 0.2,
            weight: 1
        },
        selected: {
            color: '#8b5cf6',
            fillColor: '#8b5cf6',
            fillOpacity: 0.5,
            weight: 3
        },
        hover: {
            fillOpacity: 0.5,
            weight: 3
        }
    },

    /**
     * Initialize the map
     */
    async init() {
        // Create map centered on data region (Jharkhand, India area)
        this.map = L.map('map', {
            center: [23.37, 85.35],
            zoom: 13,
            zoomControl: false
        });

        // Add zoom control to bottom right
        L.control.zoom({ position: 'bottomright' }).addTo(this.map);

        // Add tile layer (OpenStreetMap)
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 19
        }).addTo(this.map);

        // Initialize parcels layer group
        this.parcelsLayer = L.layerGroup().addTo(this.map);

        // Bind control events
        this.bindEvents();

        // Load data
        await this.loadData();
    },

    /**
     * Bind UI events
     */
    bindEvents() {
        document.getElementById('zoomAllBtn')?.addEventListener('click', () => {
            this.zoomToAll();
        });

        document.getElementById('toggleLayersBtn')?.addEventListener('click', () => {
            this.toggleParcelsVisibility();
        });
    },

    /**
     * Load parcel data and comparison data
     */
    async loadData() {
        try {
            // Load GeoJSON
            const geojson = await API.getGeoJSON();
            
            // Load comparison data
            const comparisons = await API.getComparisons();
            
            // Index comparison data by plot_id
            this.comparisonData = {};
            comparisons.comparisons.forEach(c => {
                this.comparisonData[c.plot_id] = c;
            });

            // Render parcels
            this.renderParcels(geojson);
            
            // Zoom to fit all parcels
            this.zoomToAll();

        } catch (error) {
            console.error('Error loading map data:', error);
            App.showToast('Failed to load map data', 'error');
        }
    },

    /**
     * Render parcels on the map
     */
    renderParcels(geojson) {
        this.parcelsLayer.clearLayers();

        const layer = L.geoJSON(geojson, {
            style: (feature) => this.getFeatureStyle(feature),
            onEachFeature: (feature, layer) => this.onEachFeature(feature, layer)
        });

        this.parcelsLayer.addLayer(layer);
    },

    /**
     * Get style for a feature based on comparison status
     */
    getFeatureStyle(feature) {
        const plotId = feature.properties.plot_id;
        const comparison = this.comparisonData[plotId];

        if (!comparison) {
            return this.styles.default;
        }

        const status = comparison.name_analysis?.status;
        
        switch (status) {
            case 'match':
                return this.styles.match;
            case 'partial':
                return this.styles.partial;
            case 'mismatch':
                return this.styles.mismatch;
            default:
                return this.styles.default;
        }
    },

    /**
     * Configure each feature with events and popups
     */
    onEachFeature(feature, layer) {
        const plotId = feature.properties.plot_id;
        const comparison = this.comparisonData[plotId];

        // Create popup content
        const popupContent = this.createPopupContent(feature.properties, comparison);
        layer.bindPopup(popupContent);

        // Store original style
        const originalStyle = this.getFeatureStyle(feature);

        // Hover effects
        layer.on('mouseover', () => {
            layer.setStyle({
                ...originalStyle,
                ...this.styles.hover
            });
        });

        layer.on('mouseout', () => {
            if (this.selectedLayer !== layer) {
                layer.setStyle(originalStyle);
            }
        });

        // Click to select
        layer.on('click', () => {
            this.selectParcel(plotId, layer);
        });
    },

    /**
     * Create popup HTML content
     */
    createPopupContent(properties, comparison) {
        const status = comparison?.name_analysis?.status || 'unknown';
        const statusLabel = comparison?.name_analysis?.status_label || 'No data';
        const score = comparison?.name_analysis?.similarity_score || '-';

        let statusClass = '';
        if (status === 'match') statusClass = 'match';
        else if (status === 'partial') statusClass = 'partial';
        else if (status === 'mismatch') statusClass = 'mismatch';

        return `
            <div class="popup-content">
                <h4>${properties.plot_id}</h4>
                <div class="info-row">
                    <span class="info-label">Village</span>
                    <span class="info-value">${properties.village}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Area</span>
                    <span class="info-value">${properties.area_sqm} sq.m</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Survey No</span>
                    <span class="info-value">${properties.survey_no}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Match Score</span>
                    <span class="info-value">${score}%</span>
                </div>
                <span class="status-badge ${statusClass}">${statusLabel}</span>
            </div>
        `;
    },

    /**
     * Select a parcel and show details
     */
    selectParcel(plotId, layer = null) {
        // Reset previous selection
        if (this.selectedLayer) {
            const prevFeature = this.selectedLayer.feature;
            this.selectedLayer.setStyle(this.getFeatureStyle(prevFeature));
        }

        // Find layer if not provided
        if (!layer) {
            this.parcelsLayer.eachLayer(l => {
                if (l.eachLayer) {
                    l.eachLayer(subLayer => {
                        if (subLayer.feature?.properties?.plot_id === plotId) {
                            layer = subLayer;
                        }
                    });
                }
            });
        }

        if (layer) {
            this.selectedLayer = layer;
            layer.setStyle(this.styles.selected);
            
            // Pan to selected parcel
            const bounds = layer.getBounds();
            this.map.fitBounds(bounds, { padding: [50, 50], maxZoom: 16 });
        }

        // Callback to show details
        if (this.onParcelSelect) {
            this.onParcelSelect(plotId);
        }
    },

    /**
     * Highlight a parcel without selecting
     */
    highlightParcel(plotId) {
        this.selectParcel(plotId);
    },

    /**
     * Zoom to fit all parcels
     */
    zoomToAll() {
        if (this.parcelsLayer.getLayers().length > 0) {
            const bounds = this.parcelsLayer.getBounds();
            this.map.fitBounds(bounds, { padding: [30, 30] });
        }
    },

    /**
     * Zoom to a specific village
     */
    async zoomToVillage(villageName) {
        try {
            const geojson = await API.getVillageGeoJSON(villageName);
            const layer = L.geoJSON(geojson);
            const bounds = layer.getBounds();
            this.map.fitBounds(bounds, { padding: [30, 30] });
        } catch (error) {
            console.error('Error zooming to village:', error);
        }
    },

    /**
     * Toggle parcels layer visibility
     */
    toggleParcelsVisibility() {
        if (this.map.hasLayer(this.parcelsLayer)) {
            this.map.removeLayer(this.parcelsLayer);
        } else {
            this.map.addLayer(this.parcelsLayer);
        }
    },

    /**
     * Filter parcels by status
     */
    filterByStatus(status) {
        this.parcelsLayer.eachLayer(l => {
            if (l.eachLayer) {
                l.eachLayer(subLayer => {
                    const plotId = subLayer.feature?.properties?.plot_id;
                    const comparison = this.comparisonData[plotId];
                    const parcelStatus = comparison?.name_analysis?.status;

                    if (status === 'all' || parcelStatus === status) {
                        subLayer.setStyle({ opacity: 1, fillOpacity: 0.3 });
                    } else {
                        subLayer.setStyle({ opacity: 0.2, fillOpacity: 0.05 });
                    }
                });
            }
        });
    },

    /**
     * Refresh map data
     */
    async refresh() {
        await this.loadData();
    }
};

window.MapManager = MapManager;
