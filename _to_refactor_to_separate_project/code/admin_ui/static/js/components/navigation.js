/**
 * Navigation Web Components
 * Provides header and sidebar navigation for the admin UI
 */

class NavHeader extends HTMLElement {                                   // Header Navigation Component
    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
    }

    connectedCallback() {
        this.render();
    }
    // todo: move css into separate file, since it should not be inline like this
    render() {
        this.shadowRoot.innerHTML = `
            <style>
                :host {
                    display: block;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 0;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    position: sticky;
                    top: 0;
                    z-index: 100;
                }

                .header {
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    padding: 1rem 2rem;
                    max-width: 1400px;
                    margin: 0 auto;
                }

                .brand {
                    display: flex;
                    align-items: center;
                    gap: 1rem;
                    font-size: 1.25rem;
                    font-weight: 600;
                }

                .logo {
                    width: 32px;
                    height: 32px;
                    background: rgba(255,255,255,0.2);
                    border-radius: 8px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }

                .nav-links {
                    display: flex;
                    gap: 2rem;
                    align-items: center;
                }

                .nav-link {
                    color: rgba(255,255,255,0.9);
                    text-decoration: none;
                    transition: color 0.2s;
                    cursor: pointer;
                }

                .nav-link:hover {
                    color: white;
                }

                .status-indicator {
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                    padding: 0.5rem 1rem;
                    background: rgba(255,255,255,0.1);
                    border-radius: 20px;
                    font-size: 0.875rem;
                }

                .status-dot {
                    width: 8px;
                    height: 8px;
                    background: #4ade80;
                    border-radius: 50%;
                    animation: pulse 2s infinite;
                }

                @keyframes pulse {
                    0%, 100% { opacity: 1; }
                    50% { opacity: 0.5; }
                }

                .page-title {
                    font-size: 1rem;
                    opacity: 0.9;
                    margin-left: 2rem;
                }
            </style>

            <header class="header">
                <div class="brand">
                    <div class="logo">⚡</div>
                    <span>FastAPI Admin</span>
                    <span class="page-title" id="page-title"></span>
                </div>
                
                <nav class="nav-links">
                    <a href="/docs" target="_blank" class="nav-link">Swagger</a>
                    <a href="/redoc" target="_blank" class="nav-link">ReDoc</a>
                    <div class="status-indicator">
                        <span class="status-dot"></span>
                        <span>Connected</span>
                    </div>
                </nav>
            </header>
        `;
    }

    updateTitle(title) {
        const titleEl = this.shadowRoot.getElementById('page-title');
        if (titleEl) {
            titleEl.textContent = `/ ${title}`;
        }
    }
}

// todo: move NavSidebar into separate file since we should only have one HtmlElement per file
class NavSidebar extends HTMLElement {                          // Sidebar Navigation Component
    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
        this.activePage = 'dashboard';
    }

    connectedCallback() {
        this.render();
        this.setupEventListeners();
    }
    // todo: move css into separate file, since it should not be inline like this
    // todo: see if can do the same for the HTML below, since it would be much better if this html was all in a separate file
    render() {
        this.shadowRoot.innerHTML = `
            <style>
                :host {
                    display: block;
                    width: 250px;
                    background: #f8f9fa;
                    border-right: 1px solid #e9ecef;
                    height: calc(100vh - 64px);
                    overflow-y: auto;
                }

                .sidebar {
                    padding: 1.5rem 0;
                }

                .nav-section {
                    margin-bottom: 2rem;
                }

                .nav-section-title {
                    padding: 0 1.5rem;
                    margin-bottom: 0.5rem;
                    font-size: 0.75rem;
                    font-weight: 600;
                    text-transform: uppercase;
                    color: #6c757d;
                    letter-spacing: 0.05em;
                }

                .nav-item {
                    display: block;
                    padding: 0.75rem 1.5rem;
                    color: #495057;
                    text-decoration: none;
                    transition: all 0.2s;
                    cursor: pointer;
                    border: none;
                    background: none;
                    width: 100%;
                    text-align: left;
                    font-size: 0.95rem;
                }

                .nav-item:hover {
                    background: #e9ecef;
                    color: #212529;
                }

                .nav-item.active {
                    background: #fff;
                    color: #667eea;
                    border-left: 3px solid #667eea;
                    font-weight: 500;
                }

                .nav-item-icon {
                    display: inline-block;
                    width: 20px;
                    margin-right: 0.75rem;
                    text-align: center;
                }

                .nav-divider {
                    height: 1px;
                    background: #dee2e6;
                    margin: 1.5rem 0;
                }

                .version-info {
                    padding: 1rem 1.5rem;
                    font-size: 0.75rem;
                    color: #6c757d;
                    border-top: 1px solid #dee2e6;
                    margin-top: auto;
                }
            </style>

            <nav class="sidebar">
                <div class="nav-section">
                    <div class="nav-section-title">Main</div>
                    <a href="#dashboard" class="nav-item" data-page="dashboard">
                        <span class="nav-item-icon">📊</span>
                        Dashboard
                    </a>
                    <a href="#routes" class="nav-item" data-page="routes">
                        <span class="nav-item-icon">🛣️</span>
                        API Explorer
                    </a>
                </div>

                <div class="nav-section">
                    <div class="nav-section-title">Configuration</div>
                    <a href="#cookies" class="nav-item" data-page="cookies">
                        <span class="nav-item-icon">🍪</span>
                        Cookie Manager
                    </a>
                </div>

                <div class="nav-section">
                    <div class="nav-section-title">Documentation</div>
                    <a href="#docs" class="nav-item" data-page="docs">
                        <span class="nav-item-icon">📚</span>
                        API Docs
                    </a>
                </div>

                <div class="nav-divider"></div>

                <div class="nav-section">
                    <div class="nav-section-title">External</div>
                    <a href="/docs" target="_blank" class="nav-item">
                        <span class="nav-item-icon">📖</span>
                        Swagger UI
                    </a>
                    <a href="/redoc" target="_blank" class="nav-item">
                        <span class="nav-item-icon">📄</span>
                        ReDoc
                    </a>
                    <a href="/openapi.json" target="_blank" class="nav-item">
                        <span class="nav-item-icon">📋</span>
                        OpenAPI JSON
                    </a>
                </div>

                <div class="version-info">
                    Admin UI v1.0.0
                </div>
            </nav>
        `;
    }

    setupEventListeners() {
        const navItems = this.shadowRoot.querySelectorAll('.nav-item[data-page]');
        navItems.forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const page = item.dataset.page;
                this.setActivePage(page);

                document.dispatchEvent(new CustomEvent('navigate', {                    // Dispatch navigation event
                    detail: { page }
                }));
            });
        });
    }

    setActivePage(page) {
        this.activePage = page;

        const navItems = this.shadowRoot.querySelectorAll('.nav-item[data-page]');      // Update active state
        navItems.forEach(item => {
            if (item.dataset.page === page) {
                item.classList.add('active');
            } else {
                item.classList.remove('active');
            }
        });
    }
}

customElements.define('nav-header' , NavHeader );                                   // Register custom elements
customElements.define('nav-sidebar', NavSidebar);