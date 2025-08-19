/**
 * Main Admin UI Application Module
 * Handles routing, API communication, and component orchestration
 */

export class AdminUI {
    constructor() {
        this.currentPage = 'dashboard';
        this.apiBase     = '/admin';
        this.components  = new Map();
        this.appData     = { serverInfo : null  ,
                             appInfo    : null  ,
                             routes     : []    ,
                             cookies    : []    ,
                             docs       : []    };
    }

    async init() {
        this.setupRouter                 ();
        await this.loadInitialData       ();
        this.registerEventListeners      ();
        await this.navigateToHash        ();
    }

    setupRouter() {                 // Handle hash-based routing
        window.addEventListener('hashchange', () => this.navigateToHash());
    }

    async navigateToHash() {
        const hash = window.location.hash.slice(1) || 'dashboard';
        await this.navigateTo(hash);
    }

    async navigateTo(page) {
        this.currentPage = page;
        await this.renderPage(page);
        this.updateNavigation(page);                                    // Update active nav items
    }

    updateNavigation(activePage) {                                      // Update sidebar navigation
        const sidebar = document.querySelector('nav-sidebar');
        if (sidebar && sidebar.setActivePage) {
            sidebar.setActivePage(activePage);
        }

        const header = document.querySelector('nav-header');            // Update header if needed
        if (header && header.updateTitle) {
            const titles = { 'dashboard': 'Dashboard'    ,
                             'routes'   : 'API Routes'    ,
                             'cookies'  : 'Cookie Manager',
                             'docs'     : 'Documentation'
            };
            header.updateTitle(titles[activePage] || 'Admin UI');
        }
    }

    async renderPage(page) {
        const contentEl = document.getElementById('page-content');
        if (!contentEl) return;

        contentEl.innerHTML = '';                                           // Clear current content

        contentEl.innerHTML = '<div class="loading">Loading...</div>';      // Add loading indicator

        try {
            switch (page) {
                case 'dashboard':
                    await this.renderDashboard(contentEl);
                    break;
                case 'routes':
                    await this.renderRoutes(contentEl);
                    break;
                case 'cookies':
                    await this.renderCookies(contentEl);
                    break;
                case 'docs':
                    await this.renderDocs(contentEl);
                    break;
                default:
                    contentEl.innerHTML = '<div class="error">Page not found</div>';
            }
        } catch (error) {
            console.error('Error rendering page:', error);
            contentEl.innerHTML = `<div class="error">Error loading page: ${error.message}</div>`;
        }
    }

    async renderDashboard(container) {
        await this.loadServerInfo();                                            // Fetch latest data
        await this.loadStats();

        const dashboard = document.createElement('admin-dashboard');            // Create dashboard component
        dashboard.setData({ serverInfo  : this.appData.serverInfo,
                            appInfo     : this.appData.appInfo   ,
                            stats       : this.appData.stats    });

        container.innerHTML = '';
        container.appendChild(dashboard);
    }

    async renderRoutes(container) {
        await this.loadRoutes();                                                // Fetch routes data

        const explorer = document.createElement('api-explorer');                // Create routes explorer component
        explorer.setRoutes(this.appData.routes);

        container.innerHTML = '';
        container.appendChild(explorer);
    }

    async renderCookies(container) {
        await this.loadCookies();                                               // Fetch cookies data

        const editor = document.createElement('cookie-editor');                 // Create cookie editor component
        editor.setCookies(this.appData.cookies);
        editor.setTemplates(this.appData.cookieTemplates);

        container.innerHTML = '';
        container.appendChild(editor);
    }

    async renderDocs(container) {
        await this.loadDocs();                                                  // Fetch docs endpoints

        const viewer = document.createElement('docs-viewer');                   // Create docs viewer component
        viewer.setDocs(this.appData.docs);

        container.innerHTML = '';
        container.appendChild(viewer);
    }

    async apiCall(endpoint, options = {}) {                                     // API Methods
        const url            = `${this.apiBase}${endpoint}`;
        const defaultOptions = { headers    : {  'Content-Type': 'application/json' },
                                 credentials: 'same-origin'                         };

        const response = await fetch(url, { ...defaultOptions, ...options });

        if (!response.ok) {
            throw new Error(`API call failed: ${response.statusText}`);
        }

        return await response.json();
    }

    async loadInitialData() {
        try {
            await Promise.all([this.loadServerInfo(),                               // Load basic app info
                               this.loadAppInfo   () ]);
        } catch (error) {
            console.error('Error loading initial data:', error);
            this.showToast('Error loading application data', 'error');
        }
    }

    async loadServerInfo() {
        this.appData.serverInfo = await this.apiCall('/admin-info/api/server-info');
    }

    async loadAppInfo() {
        this.appData.appInfo = await this.apiCall('/admin-info/api/app-info');
    }

    async loadStats() {
        this.appData.stats = await this.apiCall('/admin-info/api/stats');
    }

    async loadRoutes() {
        this.appData.routes = await this.apiCall('/admin-config/api/routes');
    }

    async loadCookies() {
        this.appData.cookies = await this.apiCall('/admin-cookies/api/cookies-list');
        this.appData.cookieTemplates = await this.apiCall('/admin-cookies/api/cookies-templates');
    }

    async loadDocs() {
        this.appData.docs = await this.apiCall('/admin-docs/api/docs-endpoints');
    }

    async setCookie(name, value) {                                                  // Cookie Management
        return await this.apiCall(`/admin-cookies/api/cookie-set/${name}`, {
            method: 'POST',
            body: JSON.stringify({ value })
        });
    }

    async deleteCookie(name) {
        return await this.apiCall(`/admin-cookies/api/cookie-delete/${name}`, {
            method: 'DELETE'
        });
    }

    async generateValue(type = 'uuid') {
        return await this.apiCall(`/admin-cookies/api/generate-value?value_type=${type}`);
    }

    registerEventListeners() {                                                      // Utility Methods
        document.addEventListener('cookie-updated', async (e) => {                  // Listen for custom events from components
            this.showToast(`Cookie "${e.detail.name}" updated`, 'success');
            await this.loadCookies();                                               // Refresh cookie data
        });

        document.addEventListener('navigate',async (e) => {
            await this.navigateTo(e.detail.page);
        });
    }

    showToast(message, type = 'info', duration = 3000) {
        const container = document.getElementById('toast-container');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;

        container.appendChild(toast);

        setTimeout(() => toast.classList.add('show'), 10);                      // Animate in

        setTimeout(() => {                                                      // Remove after duration
            toast.classList.remove('show');
            setTimeout(() => container.removeChild(toast), 300);
        }, duration);
    }

    formatBytes(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    formatUptime(ms) {
        const seconds = Math.floor(ms / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);

        if (days > 0) return `${days}d ${hours % 24}h`;
        if (hours > 0) return `${hours}h ${minutes % 60}m`;
        if (minutes > 0) return `${minutes}m ${seconds % 60}s`;
        return `${seconds}s`;
    }
}

window.AdminUI = AdminUI;                                                   // Export for use in other modules