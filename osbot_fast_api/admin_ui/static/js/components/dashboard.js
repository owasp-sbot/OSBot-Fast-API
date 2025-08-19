/**
 * Dashboard Web Component
 * Provides real-time server statistics and API overview
 */

class AdminDashboard extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
        this.data = {
            serverInfo: null,
            appInfo: null,
            stats: null
        };
        this.refreshInterval = null;
    }

    connectedCallback() {
        this.render();
        this.startAutoRefresh();
    }

    disconnectedCallback() {
        this.stopAutoRefresh();
    }

    setData(data) {
        this.data = { ...this.data, ...data };
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

                .dashboard-header {
                    margin-bottom: 2rem;
                }

                .dashboard-title {
                    font-size: 2rem;
                    font-weight: 600;
                    color: #212529;
                    margin: 0 0 0.5rem 0;
                }

                .dashboard-subtitle {
                    color: #6c757d;
                    font-size: 1rem;
                }

                .stats-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 1.5rem;
                    margin-bottom: 2rem;
                }

                .stat-card {
                    background: white;
                    border-radius: 8px;
                    padding: 1.5rem;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                    transition: transform 0.2s, box-shadow 0.2s;
                }

                .stat-card:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                }

                .stat-card.primary {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                }

                .stat-card.success {
                    background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
                    color: white;
                }

                .stat-card.info {
                    background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%);
                    color: white;
                }

                .stat-card.warning {
                    background: linear-gradient(135deg, #ed8936 0%, #dd6b20 100%);
                    color: white;
                }

                .stat-label {
                    font-size: 0.875rem;
                    opacity: 0.9;
                    text-transform: uppercase;
                    letter-spacing: 0.05em;
                    margin-bottom: 0.5rem;
                }

                .stat-value {
                    font-size: 2rem;
                    font-weight: 700;
                    margin-bottom: 0.5rem;
                }

                .stat-change {
                    font-size: 0.875rem;
                    opacity: 0.9;
                }

                .info-section {
                    background: white;
                    border-radius: 8px;
                    padding: 1.5rem;
                    margin-bottom: 1.5rem;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                }

                .section-title {
                    font-size: 1.25rem;
                    font-weight: 600;
                    margin-bottom: 1rem;
                    color: #212529;
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                }

                .info-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 1rem;
                }

                .info-item {
                    padding: 0.75rem;
                    background: #f8f9fa;
                    border-radius: 6px;
                    border-left: 3px solid #667eea;
                }

                .info-label {
                    font-size: 0.75rem;
                    color: #6c757d;
                    text-transform: uppercase;
                    letter-spacing: 0.05em;
                    margin-bottom: 0.25rem;
                }

                .info-value {
                    font-size: 1rem;
                    font-weight: 600;
                    color: #212529;
                    word-break: break-all;
                }

                .routes-breakdown {
                    display: flex;
                    gap: 1rem;
                    flex-wrap: wrap;
                    margin-top: 1rem;
                }

                .method-badge {
                    display: inline-flex;
                    align-items: center;
                    padding: 0.5rem 1rem;
                    border-radius: 20px;
                    font-size: 0.875rem;
                    font-weight: 600;
                    background: white;
                    border: 2px solid;
                }

                .method-badge.get {
                    border-color: #61affe;
                    color: #61affe;
                }

                .method-badge.post {
                    border-color: #49cc90;
                    color: #49cc90;
                }

                .method-badge.put {
                    border-color: #fca130;
                    color: #fca130;
                }

                .method-badge.delete {
                    border-color: #f93e3e;
                    color: #f93e3e;
                }

                .method-count {
                    margin-left: 0.5rem;
                    font-weight: 700;
                }

                .refresh-button {
                    padding: 0.5rem 1rem;
                    background: #667eea;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-size: 0.875rem;
                    cursor: pointer;
                    transition: background 0.2s;
                }

                .refresh-button:hover {
                    background: #5a67d8;
                }

                .refresh-button:disabled {
                    opacity: 0.5;
                    cursor: not-allowed;
                }

                .status-indicator {
                    display: inline-flex;
                    align-items: center;
                    gap: 0.5rem;
                    padding: 0.25rem 0.75rem;
                    background: #f0fdf4;
                    border: 1px solid #bbf7d0;
                    border-radius: 20px;
                    font-size: 0.875rem;
                    color: #16a34a;
                }

                .status-dot {
                    width: 8px;
                    height: 8px;
                    background: #16a34a;
                    border-radius: 50%;
                    animation: pulse 2s infinite;
                }

                @keyframes pulse {
                    0%, 100% { opacity: 1; }
                    50% { opacity: 0.5; }
                }

                .loading {
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    min-height: 400px;
                    color: #6c757d;
                }

                .loading::after {
                    content: '';
                    display: inline-block;
                    width: 24px;
                    height: 24px;
                    margin-left: 1rem;
                    border: 3px solid #667eea;
                    border-radius: 50%;
                    border-top-color: transparent;
                    animation: spin 0.8s linear infinite;
                }

                @keyframes spin {
                    to { transform: rotate(360deg); }
                }

                .error-message {
                    padding: 1rem;
                    background: #fef2f2;
                    border: 1px solid #fecaca;
                    border-radius: 6px;
                    color: #dc2626;
                    margin: 1rem 0;
                }

                .chart-container {
                    height: 300px;
                    position: relative;
                }

                .mini-chart {
                    width: 100%;
                    height: 60px;
                    margin-top: 0.5rem;
                }

                .sparkline {
                    stroke: #667eea;
                    stroke-width: 2;
                    fill: none;
                }

                .sparkline-area {
                    fill: #667eea;
                    opacity: 0.1;
                }
            </style>

            <div class="dashboard-container">
                <div class="dashboard-header">
                    <h1 class="dashboard-title">Dashboard</h1>
                    <p class="dashboard-subtitle">System overview and real-time statistics</p>
                </div>

                ${this.renderContent()}
            </div>
        `;

        this.attachEventListeners();
    }

    renderContent() {
        if (!this.data.serverInfo && !this.data.appInfo && !this.data.stats) {
            return '<div class="loading">Loading dashboard data...</div>';
        }

        return `
            ${this.renderStatsGrid()}
            ${this.renderServerInfo()}
            ${this.renderAppInfo()}
            ${this.renderRoutesInfo()}
        `;
    }

    renderStatsGrid() {
        const { serverInfo, stats } = this.data;

        if (!serverInfo || !stats) {
            return '';
        }

        const uptime = this.formatUptime(serverInfo.uptime_ms);
        const totalRoutes = stats.total_routes || 0;
        const middlewares = stats.middlewares_count || 0;
        const healthStatus = 'Healthy'; // Could be calculated based on metrics

        return `
            <div class="stats-grid">
                <div class="stat-card primary">
                    <div class="stat-label">System Status</div>
                    <div class="stat-value">${healthStatus}</div>
                    <div class="stat-change">
                        <div class="status-indicator">
                            <span class="status-dot"></span>
                            <span>All systems operational</span>
                        </div>
                    </div>
                </div>

                <div class="stat-card success">
                    <div class="stat-label">Uptime</div>
                    <div class="stat-value">${uptime}</div>
                    <div class="stat-change">Since ${this.formatBootTime(serverInfo.server_boot_time)}</div>
                </div>

                <div class="stat-card info">
                    <div class="stat-label">Total Routes</div>
                    <div class="stat-value">${totalRoutes}</div>
                    <div class="stat-change">${this.getRoutesSummary(stats)}</div>
                </div>

                <div class="stat-card warning">
                    <div class="stat-label">Middlewares</div>
                    <div class="stat-value">${middlewares}</div>
                    <div class="stat-change">Active middleware stack</div>
                </div>
            </div>
        `;
    }

    renderServerInfo() {
        const { serverInfo } = this.data;

        if (!serverInfo) {
            return '';
        }

        return `
            <div class="info-section">
                <div class="section-title">
                    <span>🖥️ Server Information</span>
                    <button class="refresh-button" id="refresh-btn">
                        🔄 Refresh
                    </button>
                </div>
                <div class="info-grid">
                    <div class="info-item">
                        <div class="info-label">Server ID</div>
                        <div class="info-value">${this.truncateId(serverInfo.server_id)}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Server Name</div>
                        <div class="info-value">${serverInfo.server_name || 'unnamed'}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Instance ID</div>
                        <div class="info-value">${this.truncateId(serverInfo.server_instance_id)}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Boot Time</div>
                        <div class="info-value">${this.formatTimestamp(serverInfo.server_boot_time)}</div>
                    </div>
                </div>
            </div>
        `;
    }

    renderAppInfo() {
        const { appInfo } = this.data;

        if (!appInfo) {
            return '';
        }

        return `
            <div class="info-section">
                <div class="section-title">
                    <span>⚡ Application Configuration</span>
                </div>
                <div class="info-grid">
                    <div class="info-item">
                        <div class="info-label">App Name</div>
                        <div class="info-value">${appInfo.name || 'FastAPI App'}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Version</div>
                        <div class="info-value">${appInfo.version || '1.0.0'}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Base Path</div>
                        <div class="info-value">${appInfo.base_path || '/'}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">CORS</div>
                        <div class="info-value">${appInfo.enable_cors ? '✅ Enabled' : '❌ Disabled'}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">API Key Auth</div>
                        <div class="info-value">${appInfo.enable_api_key ? '✅ Enabled' : '❌ Disabled'}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Offline Docs</div>
                        <div class="info-value">${appInfo.docs_offline ? '✅ Enabled' : '❌ Disabled'}</div>
                    </div>
                </div>
            </div>
        `;
    }

    renderRoutesInfo() {
        const { stats } = this.data;

        if (!stats || !stats.methods) {
            return '';
        }

        const methods = stats.methods;

        return `
            <div class="info-section">
                <div class="section-title">
                    <span>🛣️ Routes Breakdown</span>
                </div>
                <div class="routes-breakdown">
                    ${this.renderMethodBadge('GET', methods.GET || 0)}
                    ${this.renderMethodBadge('POST', methods.POST || 0)}
                    ${this.renderMethodBadge('PUT', methods.PUT || 0)}
                    ${this.renderMethodBadge('DELETE', methods.DELETE || 0)}
                    ${this.renderMethodBadge('PATCH', methods.PATCH || 0)}
                    ${this.renderMethodBadge('HEAD', methods.HEAD || 0)}
                    ${this.renderMethodBadge('OPTIONS', methods.OPTIONS || 0)}
                </div>
                ${this.renderPrefixBreakdown(stats.prefixes)}
            </div>
        `;
    }

    renderMethodBadge(method, count) {
        if (count === 0) return '';

        const methodClass = method.toLowerCase();
        return `
            <div class="method-badge ${methodClass}">
                <span>${method}</span>
                <span class="method-count">${count}</span>
            </div>
        `;
    }

    renderPrefixBreakdown(prefixes) {
        if (!prefixes || Object.keys(prefixes).length === 0) {
            return '';
        }

        const sortedPrefixes = Object.entries(prefixes)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 10); // Top 10 prefixes

        return `
            <div style="margin-top: 1.5rem;">
                <div class="info-label">Top Route Prefixes</div>
                <div class="info-grid" style="margin-top: 0.5rem;">
                    ${sortedPrefixes.map(([prefix, count]) => `
                        <div class="info-item">
                            <div class="info-label">${prefix}</div>
                            <div class="info-value">${count} routes</div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    attachEventListeners() {
        const refreshBtn = this.shadowRoot.getElementById('refresh-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refresh());
        }
    }

    async refresh() {
        const refreshBtn = this.shadowRoot.getElementById('refresh-btn');
        if (refreshBtn) {
            refreshBtn.disabled = true;
            refreshBtn.textContent = '⏳ Refreshing...';
        }

        try {
            // Dispatch event to parent to refresh data
            this.dispatchEvent(new CustomEvent('refresh-dashboard', {
                bubbles: true,
                composed: true
            }));

            // Re-enable button after a delay
            setTimeout(() => {
                if (refreshBtn) {
                    refreshBtn.disabled = false;
                    refreshBtn.textContent = '🔄 Refresh';
                }
            }, 1000);
        } catch (error) {
            console.error('Error refreshing dashboard:', error);
            if (refreshBtn) {
                refreshBtn.disabled = false;
                refreshBtn.textContent = '🔄 Refresh';
            }
        }
    }

    startAutoRefresh() {
        // Auto-refresh every 30 seconds
        this.refreshInterval = setInterval(() => {
            this.refresh();
        }, 30000);
    }

    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }

    // Utility methods
    formatUptime(ms) {
        const seconds = Math.floor(ms / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);

        if (days > 0) {
            return `${days}d ${hours % 24}h`;
        } else if (hours > 0) {
            return `${hours}h ${minutes % 60}m`;
        } else if (minutes > 0) {
            return `${minutes}m`;
        } else {
            return `${seconds}s`;
        }
    }

    formatBootTime(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diffMs = now - date;
        const diffHours = Math.floor(diffMs / (1000 * 60 * 60));

        if (diffHours < 24) {
            return date.toLocaleTimeString();
        } else {
            return date.toLocaleDateString();
        }
    }

    formatTimestamp(timestamp) {
        const date = new Date(timestamp);
        return date.toLocaleString();
    }

    truncateId(id) {
        if (!id) return 'N/A';
        if (id.length <= 12) return id;
        return `${id.substring(0, 8)}...`;
    }

    getRoutesSummary(stats) {
        if (!stats.methods) return '';

        const methods = Object.keys(stats.methods).length;
        return `${methods} HTTP methods`;
    }
}

// Register the custom element
customElements.define('admin-dashboard', AdminDashboard);

// Export for use in other modules
export { AdminDashboard };