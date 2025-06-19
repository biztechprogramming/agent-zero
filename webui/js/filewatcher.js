// Filewatcher management functionality
window.filewatcherManager = {
    initialized: false,
    pollingInterval: null,
    activeSubTab: 'watchers',
    
    init() {
        if (this.initialized) return;
        this.initialized = true;
        
        // Start polling for updates
        this.startPolling();
        
        // Load initial data
        this.loadWatchers();
        this.loadInvestigations();
    },
    
    switchTab(tab) {
        this.activeSubTab = tab;
        
        // Update tab classes
        document.querySelectorAll('#filewatcher-panel .tab').forEach(el => {
            el.classList.remove('active');
        });
        document.querySelectorAll('#filewatcher-panel .tab-content').forEach(el => {
            el.classList.remove('active');
        });
        
        // Activate selected tab
        if (tab === 'watchers') {
            document.querySelector('#filewatcher-panel .tab:nth-child(1)').classList.add('active');
            document.getElementById('watchers-tab').classList.add('active');
        } else if (tab === 'investigations') {
            document.querySelector('#filewatcher-panel .tab:nth-child(2)').classList.add('active');
            document.getElementById('investigations-tab').classList.add('active');
        }
    },
    
    startPolling() {
        // Poll every 5 seconds
        this.pollingInterval = setInterval(() => {
            if (document.querySelector('#filewatcher-panel:not(.hidden)')) {
                this.loadWatchers();
                this.loadInvestigations();
            }
        }, 5000);
    },
    
    stopPolling() {
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
            this.pollingInterval = null;
        }
    },
    
    async loadWatchers() {
        try {
            const response = await fetch("/filewatcher_list", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({})
            });
            const data = await response.json();
            if (data.watchers) {
                this.renderWatchers(data.watchers);
            } else {
                this.renderWatchers([]);
            }
        } catch (error) {
            console.error("Failed to load watchers:", error);
            this.renderWatchers([]);
        }
    },
    
    async loadInvestigations() {
        try {
            const response = await fetch("/filewatcher_investigations", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({})
            });
            const data = await response.json();
            if (data.investigations) {
                this.renderInvestigations(data.investigations);
            } else {
                this.renderInvestigations([]);
            }
        } catch (error) {
            console.error("Failed to load investigations:", error);
            this.renderInvestigations([]);
        }
    },
    
    renderWatchers(watchers) {
        const container = document.getElementById('filewatcher-list');
        if (!container) return;
        
        if (watchers.length === 0) {
            container.innerHTML = '<div class="empty-state">No file watchers configured</div>';
            return;
        }
        
        const html = watchers.map(watcher => {
            const statusClass = watcher.is_running ? 'status-active' : 'status-inactive';
            const statusText = watcher.is_running ? 'Active' : watcher.state;
            
            return `
                <div class="watcher-item" data-watcher-id="${watcher.id}">
                    <div class="watcher-header">
                        <h4>${this.escapeHtml(watcher.name)}</h4>
                        <span class="watcher-status ${statusClass}">${statusText}</span>
                    </div>
                    <div class="watcher-details">
                        <div class="detail-row">
                            <span class="label">Directory:</span>
                            <span class="value">${this.escapeHtml(watcher.directory)}</span>
                        </div>
                        <div class="detail-row">
                            <span class="label">Pattern:</span>
                            <span class="value">${this.escapeHtml(watcher.file_pattern || '*')}</span>
                        </div>
                        <div class="detail-row">
                            <span class="label">Investigations:</span>
                            <span class="value">${watcher.investigation_count}</span>
                        </div>
                        <div class="detail-row">
                            <span class="label">Error Patterns:</span>
                            <span class="value">${watcher.error_patterns.length} patterns</span>
                        </div>
                    </div>
                    <div class="watcher-actions">
                        <button onclick="filewatcherManager.editWatcher('${watcher.id}')" class="btn-small">Edit</button>
                        <button onclick="filewatcherManager.toggleWatcher('${watcher.id}', '${watcher.state}')" class="btn-small">
                            ${watcher.is_running ? 'Stop' : 'Start'}
                        </button>
                        <button onclick="filewatcherManager.deleteWatcher('${watcher.id}')" class="btn-small btn-danger">Delete</button>
                    </div>
                </div>
            `;
        }).join('');
        
        container.innerHTML = html;
    },
    
    renderInvestigations(investigations) {
        const container = document.getElementById('investigation-list');
        if (!container) return;
        
        if (investigations.length === 0) {
            container.innerHTML = '<div class="empty-state">No investigations yet</div>';
            return;
        }
        
        const html = investigations.slice(0, 10).map(inv => {
            const statusClass = `inv-status-${inv.investigation_status}`;
            
            return `
                <div class="investigation-item ${statusClass}" data-investigation-id="${inv.id}">
                    <div class="inv-header">
                        <span class="inv-watcher">${this.escapeHtml(inv.watcher_name)}</span>
                        <span class="inv-status">${inv.investigation_status}</span>
                    </div>
                    <div class="inv-error">${this.escapeHtml(inv.error_pattern)}</div>
                    <div class="inv-details">
                        <span class="inv-file">${this.escapeHtml(inv.file_path)}</span>
                        <span class="inv-occurrences">Occurrences: ${inv.occurrences}</span>
                        <span class="inv-time">${new Date(inv.last_seen).toLocaleString()}</span>
                    </div>
                    <div class="inv-actions">
                        <button onclick="filewatcherManager.updateInvestigation('${inv.id}', 'ignored')" 
                                class="btn-small" ${inv.investigation_status === 'ignored' ? 'disabled' : ''}>
                            Ignore
                        </button>
                        <button onclick="filewatcherManager.updateInvestigation('${inv.id}', 'pending')" 
                                class="btn-small" ${inv.investigation_status === 'pending' ? 'disabled' : ''}>
                            Reinvestigate
                        </button>
                    </div>
                </div>
            `;
        }).join('');
        
        container.innerHTML = html;
    },
    
    toggleCreateForm() {
        const formContainer = document.getElementById('filewatcher-form-container');
        if (!formContainer) {
            console.error('Filewatcher form container not found');
            return;
        }
        
        if (formContainer.classList.contains('hidden')) {
            // Show form and reset it
            formContainer.classList.remove('hidden');
            document.getElementById('watcher-form').reset();
            document.getElementById('watcher-id').value = '';
            
            // Update button text
            const btn = document.querySelector('[onclick="filewatcherManager.toggleCreateForm()"]');
            if (btn) {
                btn.innerHTML = '<i class="fas fa-times"></i> Cancel';
            }
        } else {
            // Hide form
            this.cancelEdit();
        }
    },
    
    cancelEdit() {
        const formContainer = document.getElementById('filewatcher-form-container');
        if (formContainer) {
            formContainer.classList.add('hidden');
        }
        
        // Reset button text
        const btn = document.querySelector('[onclick="filewatcherManager.toggleCreateForm()"]');
        if (btn) {
            btn.innerHTML = '<i class="fas fa-plus"></i> Create Watcher';
        }
    },
    
    async editWatcher(watcherId) {
        try {
            const response = await fetch("/filewatcher_list", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({})
            });
            const data = await response.json();
            const watcher = data.watchers.find(w => w.id === watcherId);
            
            if (watcher) {
                const formContainer = document.getElementById('filewatcher-form-container');
                formContainer.classList.remove('hidden');
                
                // Populate form
                document.getElementById('watcher-id').value = watcher.id;
                document.getElementById('watcher-name').value = watcher.name;
                document.getElementById('watcher-directory').value = watcher.directory;
                document.getElementById('watcher-pattern').value = watcher.file_pattern || '';
                document.getElementById('watcher-prompt').value = watcher.prompt;
                document.getElementById('watcher-error-patterns').value = watcher.error_patterns.join('\n');
                
                // Update button text
                const btn = document.querySelector('[onclick="filewatcherManager.toggleCreateForm()"]');
                if (btn) {
                    btn.innerHTML = '<i class="fas fa-times"></i> Cancel';
                }
            }
        } catch (error) {
            console.error("Failed to load watcher for editing:", error);
        }
    },
    
    async saveWatcher() {
        console.log('Saving watcher...');
        const watcherId = document.getElementById('watcher-id').value;
        const data = {
            name: document.getElementById('watcher-name').value,
            directory: document.getElementById('watcher-directory').value,
            file_pattern: document.getElementById('watcher-pattern').value,
            prompt: document.getElementById('watcher-prompt').value,
            error_patterns: document.getElementById('watcher-error-patterns').value
                .split('\n')  // Fixed: was using '\\n' which would look for literal \n
                .filter(p => p.trim())
        };
        
        console.log('Watcher data:', data);
        
        try {
            let response;
            if (watcherId) {
                // Update existing
                response = await fetch("/filewatcher_update", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        watcher_id: watcherId,
                        ...data
                    })
                });
            } else {
                // Create new
                response = await fetch("/filewatcher_create", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(data)
                });
            }
            
            if (!response.ok) {
                let errorMessage = 'Failed to save watcher';
                try {
                    const errorData = await response.json();
                    errorMessage = errorData.error || errorMessage;
                } catch (e) {
                    // If not JSON, try to get text
                    try {
                        errorMessage = await response.text();
                    } catch (e2) {
                        errorMessage = `Server error (${response.status})`;
                    }
                }
                console.error('Server error:', errorMessage);
                throw new Error(errorMessage);
            }
            
            const result = await response.json();
            console.log('API response:', result);
            
            if (result.error) {
                throw new Error(result.error);
            }
            
            this.cancelEdit();
            this.loadWatchers();
            
            if (window.showToast) {
                window.showToast("Watcher saved successfully", "success");
            } else {
                console.log("Watcher saved successfully");
            }
        } catch (error) {
            console.error("Failed to save watcher:", error);
            if (window.showToast) {
                window.showToast("Failed to save watcher: " + error.message, "error");
            }
        }
    },
    
    async deleteWatcher(watcherId) {
        if (!confirm("Are you sure you want to delete this watcher?")) return;
        
        try {
            const response = await fetch("/filewatcher_delete", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ watcher_id: watcherId })
            });
            const result = await response.json();
            if (result.error) {
                throw new Error(result.error);
            }
            this.loadWatchers();
            if (window.showToast) {
                window.showToast("Watcher deleted successfully", "success");
            }
        } catch (error) {
            console.error("Failed to delete watcher:", error);
            if (window.showToast) {
                window.showToast("Failed to delete watcher", "error");
            }
        }
    },
    
    async toggleWatcher(watcherId, currentState) {
        const newState = currentState === 'active' ? 'stopped' : 'active';
        
        try {
            const response = await fetch("/filewatcher_update", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    watcher_id: watcherId,
                    state: newState
                })
            });
            const result = await response.json();
            if (result.error) {
                throw new Error(result.error);
            }
            this.loadWatchers();
        } catch (error) {
            console.error("Failed to toggle watcher:", error);
            if (window.showToast) {
                window.showToast("Failed to toggle watcher", "error");
            }
        }
    },
    
    async updateInvestigation(investigationId, status) {
        try {
            const response = await fetch("/filewatcher_update_investigation", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    investigation_id: investigationId,
                    status: status
                })
            });
            const result = await response.json();
            if (result.error) {
                throw new Error(result.error);
            }
            this.loadInvestigations();
            if (window.showToast) {
                window.showToast("Investigation updated", "success");
            }
        } catch (error) {
            console.error("Failed to update investigation:", error);
            if (window.showToast) {
                window.showToast("Failed to update investigation", "error");
            }
        }
    },
    
    
    async browseDirectory() {
        // For now, just show a helpful message
        // TODO: Integrate with the work_dir file browser when available
        const currentValue = document.getElementById('watcher-directory').value;
        const suggestion = currentValue || '/var/log';
        
        showToast('Enter the full path to the directory you want to monitor (e.g., ' + suggestion + ')', 'info');
    },
    
    escapeHtml(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Ensure filewatcherManager is available globally
    if (!window.filewatcherManager) {
        console.error('filewatcherManager not initialized properly');
    }
    
    // Add styles
    const style = document.createElement('style');
    style.textContent = `
        /* Override modal-content width for settings modal */
        #settingsModal .modal-content {
            max-width: none !important;
            width: 100% !important;
        }
        
        #filewatcher-panel {
            padding: 20px;
        }
        
        .filewatcher-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        
        .watcher-item {
            background: var(--primary-bg);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
        }
        
        .watcher-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .watcher-header h4 {
            margin: 0;
            color: var(--text-primary);
        }
        
        .watcher-status {
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
        }
        
        .status-active {
            background: #10b981;
            color: white;
        }
        
        .status-inactive {
            background: #6b7280;
            color: white;
        }
        
        .watcher-details {
            margin-bottom: 10px;
        }
        
        .detail-row {
            display: flex;
            margin-bottom: 5px;
            font-size: 14px;
        }
        
        .detail-row .label {
            width: 120px;
            color: var(--text-secondary);
        }
        
        .detail-row .value {
            color: var(--text-primary);
            flex: 1;
        }
        
        .watcher-actions {
            display: flex;
            gap: 10px;
        }
        
        .investigation-item {
            background: var(--primary-bg);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 10px;
        }
        
        .inv-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
        }
        
        .inv-watcher {
            font-weight: 500;
            color: var(--text-primary);
        }
        
        .inv-status {
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
        }
        
        .inv-status-pending { background: #f59e0b; color: white; }
        .inv-status-investigating { background: #3b82f6; color: white; }
        .inv-status-completed { background: #10b981; color: white; }
        .inv-status-ignored { background: #6b7280; color: white; }
        
        .inv-error {
            font-family: monospace;
            font-size: 13px;
            color: #ef4444;
            margin-bottom: 10px;
            padding: 8px;
            background: rgba(239, 68, 68, 0.1);
            border-radius: 4px;
            overflow-x: auto;
        }
        
        .inv-details {
            display: flex;
            gap: 20px;
            font-size: 12px;
            color: var(--text-secondary);
            margin-bottom: 10px;
        }
        
        .inv-actions {
            display: flex;
            gap: 10px;
        }
        
        .empty-state {
            text-align: center;
            padding: 40px;
            color: var(--text-secondary);
        }
        
        .hidden {
            display: none !important;
        }
        
        #filewatcher-form-container {
            background: var(--secondary-bg);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        }
        
        #filewatcher-form-container .form-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }
        
        @media (max-width: 768px) {
            #filewatcher-form-container .form-row {
                grid-template-columns: 1fr;
            }
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 5px;
            color: var(--text-primary);
            font-weight: 500;
        }
        
        .form-group input,
        .form-group textarea {
            width: 100%;
            padding: 8px 12px;
            border: 1px solid var(--color-secondary);
            border-radius: 4px;
            background: var(--color-background);
            color: var(--color-text);
            font-family: inherit;
            transition: all 0.3s ease;
        }
        
        .form-group input:focus,
        .form-group textarea:focus {
            outline: none;
            border-color: var(--accent-color);
            background: var(--color-background-dark, #151515);
        }
        
        .form-group textarea {
            min-height: 100px;
            resize: vertical;
        }
        
        .form-group .help-text {
            font-size: 12px;
            color: var(--text-secondary);
            margin-top: 4px;
        }
        
        .input-with-button {
            display: flex;
            gap: 8px;
            align-items: stretch;
        }
        
        .input-with-button input {
            flex: 1;
        }
        
        .btn-browse {
            padding: 8px 16px;
            background: var(--button-bg);
            color: var(--button-text);
            border: 1px solid var(--color-secondary);
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .btn-browse:hover {
            background: var(--button-hover-bg);
            border-color: var(--accent-color);
        }
        
        .form-actions {
            display: flex;
            justify-content: flex-end;
            gap: 10px;
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid var(--border-color);
        }
        
        .btn-small {
            padding: 6px 12px;
            font-size: 14px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            background: var(--button-bg);
            color: var(--button-text);
            transition: opacity 0.2s;
        }
        
        .btn-small:hover {
            opacity: 0.8;
        }
        
        .btn-small:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .btn-danger {
            background: #ef4444;
            color: white;
        }
        
        .btn-primary {
            background: #3b82f6;
            color: white;
        }
        
        .tabs {
            display: flex;
            gap: 20px;
            margin-bottom: 20px;
            border-bottom: 1px solid var(--border-color);
        }
        
        .tab {
            padding: 10px 0;
            cursor: pointer;
            border-bottom: 2px solid transparent;
            transition: all 0.2s;
        }
        
        .tab.active {
            color: var(--accent-color);
            border-bottom-color: var(--accent-color);
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
    `;
    document.head.appendChild(style);
});