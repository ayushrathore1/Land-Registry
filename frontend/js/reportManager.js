/**
 * Report Manager - Handles reconciliation reports
 */

const ReportManager = {
    reportData: null,

    /**
     * Initialize report manager
     */
    init() {
        this.bindEvents();
    },

    /**
     * Bind UI events
     */
    bindEvents() {
        // View report button
        document.getElementById('viewReportBtn')?.addEventListener('click', () => {
            this.showReportModal();
        });

        // Close report modal
        document.getElementById('closeReportBtn')?.addEventListener('click', () => {
            this.hideReportModal();
        });

        // Export button
        document.getElementById('exportReportBtn')?.addEventListener('click', () => {
            this.exportToCSV();
        });

        // Print button
        document.getElementById('printReportBtn')?.addEventListener('click', () => {
            this.printReport();
        });

        // Close modal on backdrop click
        document.getElementById('reportModal')?.addEventListener('click', (e) => {
            if (e.target.id === 'reportModal') {
                this.hideReportModal();
            }
        });
    },

    /**
     * Show report modal
     */
    async showReportModal() {
        try {
            // Show loading
            document.getElementById('reportModal').classList.add('active');
            document.getElementById('reportContent').innerHTML = `
                <div class="loading">
                    <div class="spinner"></div>
                </div>
            `;

            // Fetch report data
            this.reportData = await API.getReconciliationReport();
            
            // Render report
            this.renderReport();

        } catch (error) {
            console.error('Error loading report:', error);
            document.getElementById('reportContent').innerHTML = `
                <div class="empty-state">
                    <p style="color: var(--danger);">Failed to load report</p>
                </div>
            `;
        }
    },

    /**
     * Hide report modal
     */
    hideReportModal() {
        document.getElementById('reportModal').classList.remove('active');
    },

    /**
     * Render the reconciliation report
     */
    renderReport() {
        const { summary, priority_review, partial_matches, verified_matches } = this.reportData;

        const html = `
            <div class="report-summary">
                <div class="report-stat">
                    <div class="value">${summary.total_records}</div>
                    <div class="label">Total Records</div>
                </div>
                <div class="report-stat match">
                    <div class="value">${summary.matched}</div>
                    <div class="label">Matched</div>
                </div>
                <div class="report-stat partial">
                    <div class="value">${summary.partial_matches}</div>
                    <div class="label">Partial Match</div>
                </div>
                <div class="report-stat mismatch">
                    <div class="value">${summary.mismatches}</div>
                    <div class="label">Mismatches</div>
                </div>
            </div>

            <h3 style="margin-bottom: 1rem; color: var(--danger);">
                Priority Review (${priority_review.length} records)
            </h3>
            ${this.renderTable(priority_review)}

            <h3 style="margin: 1.5rem 0 1rem; color: var(--warning);">
                Partial Matches (${partial_matches.length} records)
            </h3>
            ${this.renderTable(partial_matches)}

            <h3 style="margin: 1.5rem 0 1rem; color: var(--success);">
                Verified Matches (${verified_matches.length} records)
            </h3>
            ${this.renderTable(verified_matches)}
        `;

        document.getElementById('reportContent').innerHTML = html;

        // Bind row clicks
        document.querySelectorAll('.report-table tbody tr').forEach(row => {
            row.addEventListener('click', () => {
                const plotId = row.dataset.plotId;
                this.hideReportModal();
                MapManager.highlightParcel(plotId);
                App.showParcelDetails(plotId);
            });
        });
    },

    /**
     * Render a table of comparisons
     */
    renderTable(comparisons) {
        if (!comparisons || comparisons.length === 0) {
            return '<p style="color: var(--text-muted); padding: 1rem;">No records</p>';
        }

        const rows = comparisons.map(c => {
            const textualName = c.name_analysis?.textual_name || '-';
            const spatialName = c.name_analysis?.spatial_name || '-';
            const score = c.name_analysis?.similarity_score || 0;

            return `
                <tr data-plot-id="${c.plot_id}" style="cursor: pointer;">
                    <td><strong>${c.plot_id}</strong></td>
                    <td>${c.village || '-'}</td>
                    <td>${textualName}</td>
                    <td>${spatialName}</td>
                    <td>${score}%</td>
                </tr>
            `;
        }).join('');

        return `
            <table class="report-table">
                <thead>
                    <tr>
                        <th>Plot ID</th>
                        <th>Village</th>
                        <th>Textual Name</th>
                        <th>Spatial Name</th>
                        <th>Score</th>
                    </tr>
                </thead>
                <tbody>
                    ${rows}
                </tbody>
            </table>
        `;
    },

    /**
     * Export report to CSV
     */
    async exportToCSV() {
        try {
            const data = await API.exportReport();
            
            // Create CSV content
            const headers = data.headers.join(',');
            const rows = data.rows.map(row => 
                data.headers.map(h => `"${row[h] || ''}"`).join(',')
            );
            const csv = [headers, ...rows].join('\n');

            // Download
            const blob = new Blob([csv], { type: 'text/csv' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `reconciliation_report_${new Date().toISOString().split('T')[0]}.csv`;
            a.click();
            URL.revokeObjectURL(url);

            App.showToast('Report exported successfully', 'success');

        } catch (error) {
            console.error('Export error:', error);
            App.showToast('Failed to export report', 'error');
        }
    },

    /**
     * Print report
     */
    printReport() {
        const content = document.getElementById('reportContent').innerHTML;
        const printWindow = window.open('', '_blank');
        
        printWindow.document.write(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>Reconciliation Report</title>
                <style>
                    body { font-family: Arial, sans-serif; padding: 20px; }
                    h1 { color: #1a1a1a; margin-bottom: 20px; }
                    h3 { margin-top: 30px; }
                    .report-summary { display: flex; gap: 20px; margin-bottom: 30px; }
                    .report-stat { text-align: center; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }
                    .report-stat .value { font-size: 32px; font-weight: bold; }
                    .report-stat .label { color: #666; }
                    .report-stat.match .value { color: #10b981; }
                    .report-stat.partial .value { color: #f59e0b; }
                    .report-stat.mismatch .value { color: #ef4444; }
                    table { width: 100%; border-collapse: collapse; margin-top: 10px; }
                    th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
                    th { background: #f5f5f5; }
                </style>
            </head>
            <body>
                <h1>Land Record Reconciliation Report</h1>
                <p>Generated: ${new Date().toLocaleString()}</p>
                ${content}
            </body>
            </html>
        `);

        printWindow.document.close();
        printWindow.print();
    }
};

window.ReportManager = ReportManager;
