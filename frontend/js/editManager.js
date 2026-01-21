/**
 * Edit Manager - Handles editing of land records
 */

const EditManager = {
    currentPlotId: null,

    /**
     * Initialize edit manager
     */
    init() {
        this.bindEvents();
    },

    /**
     * Bind UI events
     */
    bindEvents() {
        // Close edit modal
        document.getElementById('closeEditBtn')?.addEventListener('click', () => {
            this.hideEditModal();
        });

        // Edit form submit
        document.getElementById('editForm')?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleSave();
        });

        // Close modal on backdrop click
        document.getElementById('editModal')?.addEventListener('click', (e) => {
            if (e.target.id === 'editModal') {
                this.hideEditModal();
            }
        });
    },

    /**
     * Show edit modal for a parcel
     */
    async showEditModal(plotId) {
        // Check permission
        if (!AuthManager.hasRole('editor')) {
            App.showToast('Editor access required to edit records', 'error');
            return;
        }

        try {
            // Fetch current parcel data
            const parcel = await API.getParcel(plotId);
            this.currentPlotId = plotId;

            // Populate form
            document.getElementById('editPlotId').value = plotId;
            document.getElementById('editOwnerName').value = 
                parcel.textual_record?.owner_name || '';
            document.getElementById('editArea').value = 
                parcel.textual_record?.area || '';
            document.getElementById('editFatherName').value = 
                parcel.textual_record?.father_name || '';
            document.getElementById('editLandType').value = 
                parcel.textual_record?.land_type || 'Agricultural';

            // Show modal
            document.getElementById('editModal').classList.add('active');
            document.getElementById('editOwnerName').focus();

        } catch (error) {
            console.error('Error loading parcel:', error);
            App.showToast('Failed to load parcel data', 'error');
        }
    },

    /**
     * Hide edit modal
     */
    hideEditModal() {
        document.getElementById('editModal').classList.remove('active');
        document.getElementById('editForm').reset();
        document.getElementById('editError').classList.remove('active');
        this.currentPlotId = null;
    },

    /**
     * Handle form save
     */
    async handleSave() {
        const errorEl = document.getElementById('editError');

        const updates = {
            owner_name: document.getElementById('editOwnerName').value,
            area: parseInt(document.getElementById('editArea').value),
            father_name: document.getElementById('editFatherName').value,
            land_type: document.getElementById('editLandType').value
        };

        try {
            await API.updateParcel(this.currentPlotId, updates);
            
            this.hideEditModal();
            App.showToast(`Parcel ${this.currentPlotId} updated successfully`, 'success');

            // Refresh data
            await MapManager.refresh();
            await App.loadStats();

            // Refresh detail panel if open
            if (App.selectedPlotId === this.currentPlotId) {
                App.showParcelDetails(this.currentPlotId);
            }

        } catch (error) {
            console.error('Error saving parcel:', error);
            errorEl.textContent = error.message;
            errorEl.classList.add('active');
        }
    }
};

window.EditManager = EditManager;
