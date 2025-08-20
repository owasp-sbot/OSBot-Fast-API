/**
 * Cookie Editor Web Component
 * Manages cookies with templates for LLM APIs and custom values
 */

class CookieEditor extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
        this.cookies = [];
        this.templates = [];
        this.selectedTemplate = null;
        this.editingCookie = null;
        this.apiBase = '/admin/admin-cookies/api';
    }

    connectedCallback() {
        this.render();
    }

    setCookies(cookies) {
        this.cookies = cookies || [];
        this.render();
    }

    setTemplates(templates) {
        this.templates = templates || [];
        this.render();
    }

    render() {
        this.shadowRoot.innerHTML = `
            <style>
                :host {
                    display: block;
                    padding: 2rem;
                    background: #f8f9fa;
                    min-height: calc(100vh - 64px);
                }

                .editor-header {
                    margin-bottom: 2rem;
                }

                .editor-title {
                    font-size: 2rem;
                    font-weight: 600;
                    color: #212529;
                    margin: 0 0 0.5rem 0;
                }

                .editor-subtitle {
                    color: #6c757d;
                    font-size: 1rem;
                }

                .actions-bar {
                    display: flex;
                    gap: 1rem;
                    margin-bottom: 2rem;
                    flex-wrap: wrap;
                }

                .btn {
                    padding: 0.5rem 1rem;
                    border: none;
                    border-radius: 6px;
                    font-size: 0.875rem;
                    font-weight: 500;
                    cursor: pointer;
                    transition: all 0.2s;
                    display: inline-flex;
                    align-items: center;
                    gap: 0.5rem;
                }

                .btn-primary {
                    background: #667eea;
                    color: white;
                }

                .btn-primary:hover {
                    background: #5a67d8;
                    transform: translateY(-1px);
                    box-shadow: 0 4px 6px rgba(102, 126, 234, 0.2);
                }

                .btn-secondary {
                    background: white;
                    color: #495057;
                    border: 1px solid #dee2e6;
                }

                .btn-secondary:hover {
                    background: #f8f9fa;
                    border-color: #adb5bd;
                }

                .btn-success {
                    background: #48bb78;
                    color: white;
                }

                .btn-success:hover {
                    background: #38a169;
                }

                .btn-danger {
                    background: #f56565;
                    color: white;
                }

                .btn-danger:hover {
                    background: #e53e3e;
                }

                .btn-warning {
                    background: #ed8936;
                    color: white;
                }

                .btn-warning:hover {
                    background: #dd6b20;
                }

                .templates-section {
                    background: white;
                    border-radius: 8px;
                    padding: 1.5rem;
                    margin-bottom: 2rem;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                }

                .section-title {
                    font-size: 1.125rem;
                    font-weight: 600;
                    margin-bottom: 1rem;
                    color: #212529;
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                }

                .template-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
                    gap: 1rem;
                }

                .template-card {
                    padding: 1rem;
                    border: 2px solid #e9ecef;
                    border-radius: 8px;
                    cursor: pointer;
                    transition: all 0.2s;
                    background: white;
                }

                .template-card:hover {
                    border-color: #667eea;
                    background: #f8f9ff;
                    transform: translateY(-2px);
                    box-shadow: 0 4px 6px rgba(102, 126, 234, 0.1);
                }

                .template-card.selected {
                    border-color: #667eea;
                    background: #f8f9ff;
                }

                .template-name {
                    font-weight: 600;
                    color: #212529;
                    margin-bottom: 0.25rem;
                }

                .template-description {
                    font-size: 0.875rem;
                    color: #6c757d;
                }

                .cookies-table {
                    background: white;
                    border-radius: 8px;
                    overflow: hidden;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                }

                table {
                    width: 100%;
                    border-collapse: collapse;
                }

                th {
                    background: #f8f9fa;
                    padding: 1rem;
                    text-align: left;
                    font-weight: 600;
                    font-size: 0.875rem;
                    color: #495057;
                    text-transform: uppercase;
                    letter-spacing: 0.05em;
                    border-bottom: 2px solid #dee2e6;
                }

                td {
                    padding: 1rem;
                    border-bottom: 1px solid #e9ecef;
                    font-size: 0.875rem;
                }

                tr:hover {
                    background: #f8f9fa;
                }

                .cookie-name {
                    font-weight: 600;
                    color: #212529;
                    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
                }

                .cookie-description {
                    font-size: 0.75rem;
                    color: #6c757d;
                    margin-top: 0.25rem;
                }

                .cookie-value {
                    max-width: 200px;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    white-space: nowrap;
                    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
                    font-size: 0.75rem;
                    padding: 0.25rem 0.5rem;
                    background: #f8f9fa;
                    border-radius: 4px;
                }

                .cookie-value.empty {
                    color: #adb5bd;
                    font-style: italic;
                }

                .badge {
                    display: inline-block;
                    padding: 0.25rem 0.5rem;
                    font-size: 0.75rem;
                    font-weight: 600;
                    border-radius: 4px;
                    text-transform: uppercase;
                }

                .badge-category {
                    background: #e9ecef;
                    color: #495057;
                }

                .badge-required {
                    background: #fef2f2;
                    color: #dc2626;
                }

                .badge-optional {
                    background: #f0fdf4;
                    color: #16a34a;
                }

                .badge-valid {
                    background: #f0fdf4;
                    color: #16a34a;
                }

                .badge-invalid {
                    background: #fef2f2;
                    color: #dc2626;
                }

                .cookie-actions {
                    display: flex;
                    gap: 0.5rem;
                }

                .btn-sm {
                    padding: 0.25rem 0.5rem;
                    font-size: 0.75rem;
                }

                .btn-icon {
                    padding: 0.25rem 0.5rem;
                    background: transparent;
                    border: 1px solid #dee2e6;
                    color: #495057;
                    border-radius: 4px;
                    cursor: pointer;
                    transition: all 0.2s;
                }

                .btn-icon:hover {
                    background: #f8f9fa;
                    border-color: #adb5bd;
                }

                .btn-icon.edit {
                    color: #667eea;
                    border-color: #667eea;
                }

                .btn-icon.edit:hover {
                    background: #f8f9ff;
                }

                .btn-icon.delete {
                    color: #f56565;
                    border-color: #f56565;
                }

                .btn-icon.delete:hover {
                    background: #fef2f2;
                }

                .modal-overlay {
                    display: none;
                    position: fixed;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: rgba(0, 0, 0, 0.5);
                    z-index: 1000;
                    align-items: center;
                    justify-content: center;
                }

                .modal-overlay.active {
                    display: flex;
                }

                .modal {
                    background: white;
                    border-radius: 8px;
                    padding: 2rem;
                    max-width: 500px;
                    width: 90%;
                    max-height: 80vh;
                    overflow-y: auto;
                    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
                }

                .modal-header {
                    margin-bottom: 1.5rem;
                }

                .modal-title {
                    font-size: 1.5rem;
                    font-weight: 600;
                    color: #212529;
                    margin: 0;
                }

                .form-group {
                    margin-bottom: 1rem;
                }

                .form-label {
                    display: block;
                    margin-bottom: 0.5rem;
                    font-weight: 500;
                    font-size: 0.875rem;
                    color: #495057;
                }

                .form-control {
                    width: 100%;
                    padding: 0.5rem;
                    border: 1px solid #dee2e6;
                    border-radius: 4px;
                    font-size: 0.875rem;
                    transition: border-color 0.2s;
                }

                .form-control:focus {
                    outline: none;
                    border-color: #667eea;
                    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
                }

                .form-control.textarea {
                    min-height: 100px;
                    resize: vertical;
                    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
                }

                .form-help {
                    font-size: 0.75rem;
                    color: #6c757d;
                    margin-top: 0.25rem;
                }

                .modal-footer {
                    display: flex;
                    gap: 1rem;
                    justify-content: flex-end;
                    margin-top: 1.5rem;
                    padding-top: 1.5rem;
                    border-top: 1px solid #e9ecef;
                }

                .empty-state {
                    text-align: center;
                    padding: 3rem;
                    color: #6c757d;
                }

                .empty-state-icon {
                    font-size: 3rem;
                    margin-bottom: 1rem;
                    opacity: 0.5;
                }

                .empty-state-text {
                    font-size: 1.125rem;
                    margin-bottom: 1rem;
                }

                .toast {
                    position: fixed;
                    bottom: 2rem;
                    right: 2rem;
                    padding: 1rem 1.5rem;
                    background: white;
                    border-radius: 8px;
                    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
                    display: none;
                    align-items: center;
                    gap: 1rem;
                    z-index: 2000;
                    animation: slideIn 0.3s ease-out;
                }

                .toast.show {
                    display: flex;
                }

                .toast.success {
                    border-left: 4px solid #48bb78;
                }

                .toast.error {
                    border-left: 4px solid #f56565;
                }

                @keyframes slideIn {
                    from {
                        transform: translateX(100%);
                        opacity: 0;
                    }
                    to {
                        transform: translateX(0);
                        opacity: 1;
                    }
                }

                .loading {
                    display: inline-block;
                    width: 16px;
                    height: 16px;
                    border: 2px solid #667eea;
                    border-radius: 50%;
                    border-top-color: transparent;
                    animation: spin 0.8s linear infinite;
                }

                @keyframes spin {
                    to { transform: rotate(360deg); }
                }
            </style>

            <div class="editor-container">
                <div class="editor-header">
                    <h1 class="editor-title">Cookie Manager</h1>
                    <p class="editor-subtitle">Manage API keys and authentication cookies</p>
                </div>

                <div class="actions-bar">
                    <button class="btn btn-primary" id="add-cookie-btn">
                        ➕ Add Cookie
                    </button>
                    <button class="btn btn-secondary" id="refresh-btn">
                        🔄 Refresh
                    </button>
                    <button class="btn btn-warning" id="generate-uuid-btn">
                        🎲 Generate UUID
                    </button>
                    <button class="btn btn-warning" id="generate-api-key-btn">
                        🔑 Generate API Key
                    </button>
                </div>

                ${this.renderTemplates()}
                ${this.renderCookiesTable()}
                ${this.renderModal()}
                ${this.renderToast()}
            </div>
        `;

        this.attachEventListeners();
    }

    renderTemplates() {
        if (!this.templates || this.templates.length === 0) {
            return '';
        }

        return `
            <div class="templates-section">
                <div class="section-title">
                    🎯 Quick Templates
                </div>
                <div class="template-grid">
                    ${this.templates.map(template => `
                        <div class="template-card ${this.selectedTemplate === template.id ? 'selected' : ''}" 
                             data-template-id="${template.id}">
                            <div class="template-name">${template.name}</div>
                            <div class="template-description">${template.description}</div>
                        </div>
                    `).join('')}
                </div>
                ${this.selectedTemplate ? `
                    <div style="margin-top: 1rem;">
                        <button class="btn btn-success" id="apply-template-btn">
                            ✅ Apply Template
                        </button>
                        <button class="btn btn-secondary" id="clear-template-btn">
                            ❌ Clear Selection
                        </button>
                    </div>
                ` : ''}
            </div>
        `;
    }

    renderCookiesTable() {
        if (!this.cookies || this.cookies.length === 0) {
            return `
                <div class="cookies-table">
                    <div class="empty-state">
                        <div class="empty-state-icon">🍪</div>
                        <div class="empty-state-text">No cookies found</div>
                        <button class="btn btn-primary" id="add-first-cookie-btn">
                            Add Your First Cookie
                        </button>
                    </div>
                </div>
            `;
        }

        return `
            <div class="cookies-table">
                <table>
                    <thead>
                        <tr>
                            <th>Cookie Name</th>
                            <th>Value</th>
                            <th>Category</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${this.cookies.map(cookie => this.renderCookieRow(cookie)).join('')}
                    </tbody>
                </table>
            </div>
        `;
    }

    renderCookieRow(cookie) {
        const hasValue = cookie.has_value;
        const valueDisplay = hasValue ?
            `<span class="cookie-value">${'•'.repeat(Math.min(cookie.value_length, 20))}</span>` :
            `<span class="cookie-value empty">Not set</span>`;

        const statusBadge = cookie.is_valid ?
            '<span class="badge badge-valid">Valid</span>' :
            hasValue ? '<span class="badge badge-invalid">Invalid</span>' : '';

        const requiredBadge = cookie.required ?
            '<span class="badge badge-required">Required</span>' :
            '<span class="badge badge-optional">Optional</span>';

        return `
            <tr>
                <td>
                    <div class="cookie-name">${cookie.name}</div>
                    ${cookie.description ? `<div class="cookie-description">${cookie.description}</div>` : ''}
                </td>
                <td>${valueDisplay}</td>
                <td>
                    <span class="badge badge-category">${cookie.category || 'general'}</span>
                </td>
                <td>
                    ${requiredBadge}
                    ${statusBadge}
                </td>
                <td>
                    <div class="cookie-actions">
                        <button class="btn-icon edit" data-cookie="${cookie.name}" title="Edit">
                            ✏️
                        </button>
                        ${hasValue ? `
                            <button class="btn-icon delete" data-cookie="${cookie.name}" title="Delete">
                                🗑️
                            </button>
                        ` : ''}
                    </div>
                </td>
            </tr>
        `;
    }

    renderModal() {
        return `
            <div class="modal-overlay" id="cookie-modal">
                <div class="modal">
                    <div class="modal-header">
                        <h2 class="modal-title" id="modal-title">Edit Cookie</h2>
                    </div>
                    <div class="modal-body">
                        <div class="form-group">
                            <label class="form-label" for="cookie-name">Cookie Name</label>
                            <input type="text" class="form-control" id="cookie-name" readonly>
                            <div class="form-help">Cookie names cannot be changed</div>
                        </div>
                        <div class="form-group">
                            <label class="form-label" for="cookie-value">Cookie Value</label>
                            <textarea class="form-control textarea" id="cookie-value" 
                                    placeholder="Enter cookie value..."></textarea>
                            <div class="form-help" id="cookie-help">
                                Enter the value for this cookie
                            </div>
                        </div>
                        <div class="form-group">
                            <label class="form-label" for="cookie-expires">Expires In (seconds)</label>
                            <input type="number" class="form-control" id="cookie-expires" 
                                   placeholder="Leave empty for session cookie">
                            <div class="form-help">Optional: Cookie expiration time in seconds</div>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button class="btn btn-secondary" id="modal-cancel">Cancel</button>
                        <button class="btn btn-primary" id="modal-save">Save Cookie</button>
                    </div>
                </div>
            </div>
        `;
    }

    renderToast() {
        return `
            <div class="toast" id="toast">
                <span id="toast-message"></span>
            </div>
        `;
    }

    attachEventListeners() {
        // Template selection
        this.shadowRoot.querySelectorAll('.template-card').forEach(card => {
            card.addEventListener('click', (e) => {
                const templateId = e.currentTarget.dataset.templateId;
                this.selectTemplate(templateId);
            });
        });

        // Apply template
        const applyTemplateBtn = this.shadowRoot.getElementById('apply-template-btn');
        if (applyTemplateBtn) {
            applyTemplateBtn.addEventListener('click', () => this.applyTemplate());
        }

        // Clear template
        const clearTemplateBtn = this.shadowRoot.getElementById('clear-template-btn');
        if (clearTemplateBtn) {
            clearTemplateBtn.addEventListener('click', () => {
                this.selectedTemplate = null;
                this.render();
            });
        }

        // Add cookie button
        const addCookieBtn = this.shadowRoot.getElementById('add-cookie-btn');
        if (addCookieBtn) {
            addCookieBtn.addEventListener('click', () => this.showAddCookieModal());
        }

        // Add first cookie button
        const addFirstCookieBtn = this.shadowRoot.getElementById('add-first-cookie-btn');
        if (addFirstCookieBtn) {
            addFirstCookieBtn.addEventListener('click', () => this.showAddCookieModal());
        }

        // Refresh button
        const refreshBtn = this.shadowRoot.getElementById('refresh-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refresh());
        }

        // Generate UUID button
        const generateUuidBtn = this.shadowRoot.getElementById('generate-uuid-btn');
        if (generateUuidBtn) {
            generateUuidBtn.addEventListener('click', () => this.generateValue('uuid'));
        }

        // Generate API Key button
        const generateApiKeyBtn = this.shadowRoot.getElementById('generate-api-key-btn');
        if (generateApiKeyBtn) {
            generateApiKeyBtn.addEventListener('click', () => this.generateValue('api_key'));
        }

        // Edit cookie buttons
        this.shadowRoot.querySelectorAll('.btn-icon.edit').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const cookieName = e.currentTarget.dataset.cookie;
                this.showEditCookieModal(cookieName);
            });
        });

        // Delete cookie buttons
        this.shadowRoot.querySelectorAll('.btn-icon.delete').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const cookieName = e.currentTarget.dataset.cookie;
                this.deleteCookie(cookieName);
            });
        });

        // Modal controls
        const modal = this.shadowRoot.getElementById('cookie-modal');
        const modalCancel = this.shadowRoot.getElementById('modal-cancel');
        const modalSave = this.shadowRoot.getElementById('modal-save');

        if (modalCancel) {
            modalCancel.addEventListener('click', () => this.closeModal());
        }

        if (modalSave) {
            modalSave.addEventListener('click', () => this.saveCookie());
        }

        // Close modal on overlay click
        if (modal) {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeModal();
                }
            });
        }
    }

    selectTemplate(templateId) {
        this.selectedTemplate = templateId;
        this.render();
    }

    async applyTemplate() {
        if (!this.selectedTemplate) return;

        const template = this.templates.find(t => t.id === this.selectedTemplate);
        if (!template) return;

        const applyBtn = this.shadowRoot.getElementById('apply-template-btn');
        if (applyBtn) {
            applyBtn.disabled = true;
            applyBtn.innerHTML = '<span class="loading"></span> Applying...';
        }

        try {
            // Prepare cookies data for bulk set
            const cookiesToSet = template.cookies.map(cookie => ({
                name: cookie.name,
                value: '' // User will need to fill in actual values
            }));

            // For now, just show a message - actual implementation would call the API
            this.showToast(`Template "${template.name}" ready. Please edit each cookie to add values.`, 'success');

            // Clear selection
            this.selectedTemplate = null;
            await this.refresh();
        } catch (error) {
            console.error('Error applying template:', error);
            this.showToast('Failed to apply template', 'error');
        } finally {
            if (applyBtn) {
                applyBtn.disabled = false;
                applyBtn.innerHTML = '✅ Apply Template';
            }
        }
    }

    showAddCookieModal() {
        const modal = this.shadowRoot.getElementById('cookie-modal');
        const title = this.shadowRoot.getElementById('modal-title');
        const nameInput = this.shadowRoot.getElementById('cookie-name');
        const valueInput = this.shadowRoot.getElementById('cookie-value');
        const expiresInput = this.shadowRoot.getElementById('cookie-expires');

        if (modal && title && nameInput && valueInput && expiresInput) {
            title.textContent = 'Add New Cookie';
            nameInput.value = '';
            nameInput.readOnly = false;
            valueInput.value = '';
            expiresInput.value = '';
            modal.classList.add('active');
            this.editingCookie = null;
        }
    }

    async showEditCookieModal(cookieName) {
        const cookie = this.cookies.find(c => c.name === cookieName);
        if (!cookie) return;

        const modal = this.shadowRoot.getElementById('cookie-modal');
        const title = this.shadowRoot.getElementById('modal-title');
        const nameInput = this.shadowRoot.getElementById('cookie-name');
        const valueInput = this.shadowRoot.getElementById('cookie-value');
        const expiresInput = this.shadowRoot.getElementById('cookie-expires');
        const helpText = this.shadowRoot.getElementById('cookie-help');

        if (modal && title && nameInput && valueInput && expiresInput) {
            title.textContent = 'Edit Cookie';
            nameInput.value = cookieName;
            nameInput.readOnly = true;

            // Fetch current value from API
            try {
                const response = await fetch(`${this.apiBase}/cookie-get/${cookieName}`);
                const data = await response.json();
                valueInput.value = data.value || '';

                // Update help text based on cookie config
                if (data.config && data.config.validator) {
                    helpText.textContent = `Pattern: ${data.config.validator}`;
                }
            } catch (error) {
                console.error('Error fetching cookie value:', error);
                valueInput.value = '';
            }

            expiresInput.value = '';
            modal.classList.add('active');
            this.editingCookie = cookieName;
        }
    }

    closeModal() {
        const modal = this.shadowRoot.getElementById('cookie-modal');
        if (modal) {
            modal.classList.remove('active');
            this.editingCookie = null;
        }
    }

    async saveCookie() {
        const nameInput = this.shadowRoot.getElementById('cookie-name');
        const valueInput = this.shadowRoot.getElementById('cookie-value');
        const expiresInput = this.shadowRoot.getElementById('cookie-expires');
        const saveBtn = this.shadowRoot.getElementById('modal-save');

        if (!nameInput || !valueInput) return;

        const cookieName = nameInput.value.trim();
        const cookieValue = valueInput.value.trim();
        const expiresIn = expiresInput.value ? parseInt(expiresInput.value) : null;

        if (!cookieName) {
            this.showToast('Cookie name is required', 'error');
            return;
        }

        if (saveBtn) {
            saveBtn.disabled = true;
            saveBtn.innerHTML = '<span class="loading"></span> Saving...';
        }

        try {
            const response = await fetch(`${this.apiBase}/cookie-set/${cookieName}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    value: cookieValue,
                    expires_in: expiresIn
                })
            });

            const result = await response.json();

            if (result.success) {
                this.showToast(`Cookie "${cookieName}" saved successfully`, 'success');
                this.closeModal();
                await this.refresh();

                // Dispatch event for parent
                this.dispatchEvent(new CustomEvent('cookie-updated', {
                    detail: { name: cookieName, value: cookieValue },
                    bubbles: true,
                    composed: true
                }));
            } else {
                this.showToast(result.error || 'Failed to save cookie', 'error');
            }
        } catch (error) {
            console.error('Error saving cookie:', error);
            this.showToast('Failed to save cookie', 'error');
        } finally {
            if (saveBtn) {
                saveBtn.disabled = false;
                saveBtn.innerHTML = 'Save Cookie';
            }
        }
    }

    async deleteCookie(cookieName) {
        if (!confirm(`Are you sure you want to delete the cookie "${cookieName}"?`)) {
            return;
        }

        try {
            const response = await fetch(`${this.apiBase}/cookie-delete/${cookieName}`, {
                method: 'DELETE'
            });

            const result = await response.json();

            if (result.success) {
                this.showToast(`Cookie "${cookieName}" deleted successfully`, 'success');
                await this.refresh();
            } else {
                this.showToast('Failed to delete cookie', 'error');
            }
        } catch (error) {
            console.error('Error deleting cookie:', error);
            this.showToast('Failed to delete cookie', 'error');
        }
    }

    async generateValue(type) {
        try {
            const response = await fetch(`${this.apiBase}/generate-value/${type}`);
            const result = await response.json();

            if (result.value) {
                // Copy to clipboard
                navigator.clipboard.writeText(result.value).then(() => {
                    this.showToast(`Generated ${type} copied to clipboard`, 'success');
                }).catch(() => {
                    this.showToast(`Generated: ${result.value}`, 'success');
                });
            }
        } catch (error) {
            console.error('Error generating value:', error);
            this.showToast('Failed to generate value', 'error');
        }
    }

    async refresh() {
        const refreshBtn = this.shadowRoot.getElementById('refresh-btn');
        if (refreshBtn) {
            refreshBtn.disabled = true;
            refreshBtn.innerHTML = '<span class="loading"></span> Refreshing...';
        }

        try {
            // Fetch fresh cookie list
            const response = await fetch(`${this.apiBase}/cookies-list`);
            const cookies = await response.json();
            this.setCookies(cookies);

            // Fetch templates if not loaded
            if (!this.templates || this.templates.length === 0) {
                const templatesResponse = await fetch(`${this.apiBase}/cookies-templates`);
                const templates = await templatesResponse.json();
                this.setTemplates(templates);
            }

            this.showToast('Cookies refreshed', 'success');
        } catch (error) {
            console.error('Error refreshing cookies:', error);
            this.showToast('Failed to refresh cookies', 'error');
        } finally {
            if (refreshBtn) {
                refreshBtn.disabled = false;
                refreshBtn.innerHTML = '🔄 Refresh';
            }
        }
    }

    showToast(message, type = 'success') {
        const toast = this.shadowRoot.getElementById('toast');
        const toastMessage = this.shadowRoot.getElementById('toast-message');

        if (toast && toastMessage) {
            toastMessage.textContent = message;
            toast.className = `toast ${type}`;
            toast.classList.add('show');

            setTimeout(() => {
                toast.classList.remove('show');
            }, 3000);
        }
    }
}

// Register the custom element
customElements.define('cookie-editor', CookieEditor);

// Export for use in other modules
export { CookieEditor };