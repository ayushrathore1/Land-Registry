/**
 * Search Manager - Handles search functionality
 */

const SearchManager = {
    currentTab: 'plot',
    debounceTimer: null,
    onResultSelect: null,

    /**
     * Initialize search manager
     */
    init() {
        this.bindEvents();
    },

    /**
     * Bind UI events
     */
    bindEvents() {
        // Tab switching
        document.querySelectorAll('.search-tabs .tab').forEach(tab => {
            tab.addEventListener('click', () => {
                this.switchTab(tab.dataset.tab);
            });
        });

        // Search input
        const searchInput = document.getElementById('searchInput');
        searchInput?.addEventListener('input', () => {
            this.debounceSearch();
        });

        searchInput?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.executeSearch();
            }
        });

        // Search button
        document.getElementById('searchBtn')?.addEventListener('click', () => {
            this.executeSearch();
        });
    },

    /**
     * Switch between search tabs
     */
    switchTab(tab) {
        this.currentTab = tab;
        
        // Update UI
        document.querySelectorAll('.search-tabs .tab').forEach(t => {
            t.classList.toggle('active', t.dataset.tab === tab);
        });

        // Update placeholder
        const input = document.getElementById('searchInput');
        if (tab === 'plot') {
            input.placeholder = 'Enter plot ID (e.g., RAM-001)';
        } else {
            input.placeholder = 'Enter owner name';
        }

        // Clear results
        this.clearResults();
    },

    /**
     * Debounce search for real-time results
     */
    debounceSearch() {
        clearTimeout(this.debounceTimer);
        this.debounceTimer = setTimeout(() => {
            this.executeSearch();
        }, 300);
    },

    /**
     * Execute search
     */
    async executeSearch() {
        const query = document.getElementById('searchInput').value.trim();
        
        if (query.length < 2) {
            this.clearResults();
            return;
        }

        try {
            this.showLoading();

            let response;
            if (this.currentTab === 'plot') {
                response = await API.searchByPlotId(query);
            } else {
                response = await API.searchByOwnerName(query);
            }

            this.displayResults(response.results);

        } catch (error) {
            console.error('Search error:', error);
            this.showError('Search failed. Please try again.');
        }
    },

    /**
     * Display search results
     */
    displayResults(results) {
        const container = document.getElementById('searchResults');

        if (!results || results.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <p>No results found</p>
                </div>
            `;
            return;
        }

        const html = results.map(result => {
            const scoreClass = result.match_score >= 80 ? 'high' : 
                              result.match_score >= 60 ? 'medium' : 'low';
            
            const ownerName = result.textual_record?.owner_name || 
                             result.matched_name || 'Unknown';

            return `
                <div class="search-result-item" data-plot-id="${result.plot_id}">
                    <div class="plot-id">${result.plot_id}</div>
                    <div class="owner-name">${ownerName}</div>
                    <span class="match-score ${scoreClass}">
                        ${result.match_score}% match
                    </span>
                </div>
            `;
        }).join('');

        container.innerHTML = html;

        // Bind click events
        container.querySelectorAll('.search-result-item').forEach(item => {
            item.addEventListener('click', () => {
                const plotId = item.dataset.plotId;
                this.selectResult(plotId);
            });
        });
    },

    /**
     * Select a search result
     */
    selectResult(plotId) {
        // Highlight on map
        MapManager.highlightParcel(plotId);

        // Callback
        if (this.onResultSelect) {
            this.onResultSelect(plotId);
        }
    },

    /**
     * Show loading state
     */
    showLoading() {
        document.getElementById('searchResults').innerHTML = `
            <div class="loading">
                <div class="spinner"></div>
            </div>
        `;
    },

    /**
     * Show error message
     */
    showError(message) {
        document.getElementById('searchResults').innerHTML = `
            <div class="empty-state">
                <p style="color: var(--danger);">${message}</p>
            </div>
        `;
    },

    /**
     * Clear search results
     */
    clearResults() {
        document.getElementById('searchResults').innerHTML = `
            <div class="empty-state">
                <p>Search for a plot by ID or owner name</p>
            </div>
        `;
    }
};

window.SearchManager = SearchManager;
