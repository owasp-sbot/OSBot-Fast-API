/**
 * Main Admin UI Application Module - Updated with Deep Linking
 * Handles routing, API communication, and component orchestration
 */

export class AdminUI {
    constructor() {
        this.currentPage = 'dashboard';
        this.currentSubPage = null;
        this.apiBase     = '/admin';
        this.components  = new Map();
        this.appData     = {
            serverInfo : null,
            appInfo    : null,
            routes     : [],
            cookies    : [],
            docs       : []
        };
    }

    async init() {
        this.setupRouter();
        await this.loadInitialData();
        this.registerEventListeners();
        await this.navigateToHash();
    }

    setupRouter() {
        // Handle hash-based routing with support for sub-pages
        window.addEventListener('hashchange', () => this.navigateToHash());
    }

    async navigateToHash() {
        const hash = window.location.hash.slice(1) || 'dashboard';

        // Parse hash for main page and sub-page
        // Format: #docs/quickstart or just #dashboard
        const parts = hash.split('/');
        const mainPage = parts[0];
        const subPage = parts[1] || null;

        await this.navigateTo(mainPage, subPage);
    }

    async navigateTo(page, subPage = null) {
        this.currentPage = page;
        this.currentSubPage = subPage;

        await this.renderPage(page, subPage);
        this.updateNavigation(page, subPage);
    }

    updateNavigation(activePage, activeSubPage) {
        // Update sidebar navigation
        const sidebar = document.querySelector('nav-sidebar');
        if (sidebar && sidebar.setActivePage) {
            sidebar.setActivePage(activePage);
        }

        // Update header if needed
        const header = document.querySelector('nav-header');
        if (header && header.updateTitle) {
            const titles = {
                'dashboard': 'Dashboard',
                'routes'   : 'API Routes',
                'cookies'  : 'Cookie Manager',
                'docs'     : 'Documentation'
            };

            let title = titles[activePage] || 'Admin UI';

            // Add sub-page to title if in docs
            if (activePage === 'docs' && activeSubPage) {
                const subTitles = {
                    'quickstart': 'Quick Start',
                    'installation': 'Installation',
                    'authentication': 'Authentication',
                    'endpoints': 'Endpoints',
                    'schemas': 'Schemas'
                };
                if (subTitles[activeSubPage]) {
                    title += ` / ${subTitles[activeSubPage]}`;
                }
            }

            header.updateTitle(title);
        }
    }

    async renderPage(page, subPage = null) {
        const contentEl = document.getElementById('page-content');
        if (!contentEl) return;

        contentEl.innerHTML = '';
        contentEl.innerHTML = '<div class="loading">Loading...</div>';

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
                    await this.renderDocs(contentEl, subPage);
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
        await this.loadServerInfo();
        await this.loadStats();

        const dashboard = document.createElement('admin-dashboard');
        dashboard.setData({
            serverInfo: this.appData.serverInfo,
            appInfo   : this.appData.appInfo,
            stats     : this.appData.stats
        });

        container.innerHTML = '';
        container.appendChild(dashboard);
    }

    async renderRoutes(container) {
        await this.loadRoutes();

        const explorer = document.createElement('api-explorer');
        explorer.setRoutes(this.appData.routes);

        container.innerHTML = '';
        container.appendChild(explorer);
    }

    async renderCookies(container) {
        await this.loadCookies();

        const editor = document.createElement('cookie-editor');
        editor.setCookies(this.appData.cookies);
        editor.setTemplates(this.appData.cookieTemplates);

        container.innerHTML = '';
        container.appendChild(editor);
    }

    async renderDocs(container, subPage = null) {
        await this.loadDocs();

        const viewer = document.createElement('docs-viewer');
        viewer.setDocs(this.appData.docs);

        container.innerHTML = '';
        container.appendChild(viewer);

        // Load the appropriate content immediately (no setTimeout needed)
        const docToLoad = subPage || 'overview';
        viewer.loadDocContent(docToLoad);
    }

    // API Methods
    async apiCall(endpoint, options = {}) {
        const url = `${this.apiBase}${endpoint}`;
        const defaultOptions = {
            headers: { 'Content-Type': 'application/json' },
            credentials: 'same-origin'
        };

        const response = await fetch(url, { ...defaultOptions, ...options });

        if (!response.ok) {
            throw new Error(`API call failed: ${response.statusText}`);
        }

        return await response.json();
    }

    async loadInitialData() {
        try {
            await Promise.all([
                this.loadServerInfo(),
                this.loadAppInfo()
            ]);
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

    // Cookie Management
    async setCookie(name, value) {
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
        return await this.apiCall(`/admin-cookies/api/generate-value/${type}`);
    }

    // Utility Methods
    registerEventListeners() {
        // Listen for custom events from components
        document.addEventListener('cookie-updated', async (e) => {
            this.showToast(`Cookie "${e.detail.name}" updated`, 'success');
            await this.loadCookies();
        });

        document.addEventListener('navigate', async (e) => {
            const { page, subPage } = e.detail;

            // Update the hash to reflect navigation
            if (subPage) {
                window.location.hash = `${page}/${subPage}`;
            } else {
                window.location.hash = page;
            }
        });

        // Listen for navigate-to-doc events from docs viewer
        document.addEventListener('navigate-to-doc', async (e) => {
            const { docId } = e.detail;
            window.location.hash = `docs/${docId}`;
        });
    }

    showToast(message, type = 'info', duration = 3000) {
        const container = document.getElementById('toast-container');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;

        container.appendChild(toast);

        setTimeout(() => toast.classList.add('show'), 10);

        setTimeout(() => {
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

// Export for use in other modules
window.AdminUI = AdminUI;