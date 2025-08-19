/**
 * API Explorer Web Component
 * Browse, test, and interact with API endpoints
 */

class APIExplorer extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
        this.routes = [];
        this.groupedRoutes = {};
        this.selectedRoute = null;
        this.selectedTag = null;
        this.testHistory = [];
        this.apiBase = '';
    }

    connectedCallback() {
        this.render();
    }

    setRoutes(routes) {
        this.routes = routes || [];
        this.groupRoutes();
        this.render();
    }

    groupRoutes() {
        this.groupedRoutes = {};
        this.routes.forEach(route => {
            const tag = route.tag || 'other';
            if (!this.groupedRoutes[tag]) {
                this.groupedRoutes[tag] = [];
            }
            this.groupedRoutes[tag].push(route);
        });
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

                .explorer-header {
                    margin-bottom: 2rem;
                }

                .explorer-title {
                    font-size: 2rem;
                    font-weight: 600;
                    color: #212529;
                    margin: 0 0 0.5rem 0;
                }

                .explorer-subtitle {
                    color: #6c757d;
                    font-size: 1rem;
                }

                .explorer-layout {
                    display: grid;
                    grid-template-columns: 350px 1fr;
                    gap: 2rem;
                    height: calc(100vh - 200px);
                }

                @media (max-width: 1024px) {
                    .explorer-layout {
                        grid-template-columns: 1fr;
                        height: auto;
                    }
                }

                .sidebar {
                    background: white;
                    border-radius: 8px;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                    overflow: hidden;
                    display: flex;
                    flex-direction: column;
                }

                .sidebar-header {
                    padding: 1rem;
                    border-bottom: 2px solid #e9ecef;
                    background: #f8f9fa;
                }

                .search-box {
                    width: 100%;
                    padding: 0.5rem 1rem;
                    border: 1px solid #dee2e6;
                    border-radius: 6px;
                    font-size: 0.875rem;
                    transition: border-color 0.2s;
                }

                .search-box:focus {
                    outline: none;
                    border-color: #667eea;
                    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
                }

                .route-groups {
                    flex: 1;
                    overflow-y: auto;
                    padding: 1rem;
                }

                .route-group {
                    margin-bottom: 1.5rem;
                }

                .group-header {
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    padding: 0.5rem;
                    margin-bottom: 0.5rem;
                    cursor: pointer;
                    border-radius: 6px;
                    transition: background 0.2s;
                }

                .group-header:hover {
                    background: #f8f9fa;
                }

                .group-title {
                    font-weight: 600;
                    color: #212529;
                    text-transform: capitalize;
                    font-size: 0.875rem;
                }

                .group-count {
                    background: #e9ecef;
                    color: #495057;
                    padding: 0.25rem 0.5rem;
                    border-radius: 12px;
                    font-size: 0.75rem;
                    font-weight: 600;
                }

                .route-list {
                    margin-left: 0.5rem;
                }

                .route-item {
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                    padding: 0.5rem;
                    margin-bottom: 0.25rem;
                    border-radius: 6px;
                    cursor: pointer;
                    transition: all 0.2s;
                    border: 1px solid transparent;
                    min-width: max-content;  /* Ensure full width */
                }

                .route-item:hover {
                    background: #f8f9fa;
                    border-color: #e9ecef;
                }

                .route-item.selected {
                    background: #f8f9ff;
                    border-color: #667eea;
                }

                .method-badge {
                    display: inline-block;
                    padding: 0.25rem 0.5rem;
                    font-size: 0.625rem;
                    font-weight: 700;
                    text-transform: uppercase;
                    border-radius: 4px;
                    min-width: 50px;
                    text-align: center;
                }

                .method-get { background: #61affe; color: white; }
                .method-post { background: #49cc90; color: white; }
                .method-put { background: #fca130; color: white; }
                .method-delete { background: #f93e3e; color: white; }
                .method-patch { background: #50e3c2; color: white; }
                .method-head { background: #9012fe; color: white; }
                .method-options { background: #0d5aa7; color: white; }

                .route-path {
                    flex: 1;
                    font-size: 0.875rem;
                    color: #495057;
                    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
                    word-break: break-all;  /* Allow breaking long paths */
                }

                .main-content {
                    background: white;
                    border-radius: 8px;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                    overflow: hidden;
                    display: flex;
                    flex-direction: column;
                }

                .content-header {
                    padding: 1.5rem;
                    border-bottom: 2px solid #e9ecef;
                    background: #f8f9fa;
                }

                .route-info {
                    display: flex;
                    align-items: center;
                    gap: 1rem;
                    margin-bottom: 0.5rem;
                }

                .route-info .method-badge {
                    font-size: 0.875rem;
                    padding: 0.5rem 1rem;
                }

                .route-full-path {
                    font-size: 1.25rem;
                    font-weight: 600;
                    color: #212529;
                    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
                }

                .route-name {
                    color: #6c757d;
                    font-size: 0.875rem;
                }

                .content-body {
                    flex: 1;
                    overflow-y: auto;
                    padding: 1.5rem;
                }

                .test-section {
                    margin-bottom: 2rem;
                }

                .section-title {
                    font-size: 1rem;
                    font-weight: 600;
                    margin-bottom: 1rem;
                    color: #212529;
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                }

                .params-form {
                    background: #f8f9fa;
                    padding: 1rem;
                    border-radius: 6px;
                    margin-bottom: 1rem;
                }

                .form-group {
                    margin-bottom: 1rem;
                }

                .form-group:last-child {
                    margin-bottom: 0;
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
                    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
                }

                .form-control:focus {
                    outline: none;
                    border-color: #667eea;
                    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
                }

                .form-control.textarea {
                    min-height: 120px;
                    resize: vertical;
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

                .btn:disabled {
                    opacity: 0.5;
                    cursor: not-allowed;
                    transform: none;
                }

                .response-section {
                    margin-top: 2rem;
                    padding-top: 2rem;
                    border-top: 2px solid #e9ecef;
                }

                .response-header {
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    margin-bottom: 1rem;
                }

                .response-status {
                    display: inline-flex;
                    align-items: center;
                    gap: 0.5rem;
                    padding: 0.5rem 1rem;
                    border-radius: 6px;
                    font-weight: 600;
                    font-size: 0.875rem;
                }

                .status-success {
                    background: #f0fdf4;
                    color: #16a34a;
                    border: 1px solid #bbf7d0;
                }

                .status-error {
                    background: #fef2f2;
                    color: #dc2626;
                    border: 1px solid #fecaca;
                }

                .status-info {
                    background: #eff6ff;
                    color: #1e40af;
                    border: 1px solid #bfdbfe;
                }

                .response-time {
                    color: #6c757d;
                    font-size: 0.875rem;
                }

                .response-body {
                    background: #1e293b;
                    color: #e2e8f0;
                    padding: 1rem;
                    border-radius: 6px;
                    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
                    font-size: 0.875rem;
                    line-height: 1.5;
                    overflow-x: auto;
                    max-height: 400px;
                    overflow-y: auto;
                }

                .response-body pre {
                    margin: 0;
                    white-space: pre-wrap;
                    word-wrap: break-word;
                }

                .json-key {
                    color: #7dd3c0;
                }

                .json-string {
                    color: #a5f3fc;
                }

                .json-number {
                    color: #fbbf24;
                }

                .json-boolean {
                    color: #f472b6;
                }

                .json-null {
                    color: #94a3b8;
                }

                .tabs {
                    display: flex;
                    gap: 0.5rem;
                    margin-bottom: 1rem;
                    border-bottom: 2px solid #e9ecef;
                }

                .tab {
                    padding: 0.5rem 1rem;
                    background: transparent;
                    border: none;
                    border-bottom: 2px solid transparent;
                    color: #6c757d;
                    font-size: 0.875rem;
                    font-weight: 500;
                    cursor: pointer;
                    transition: all 0.2s;
                    margin-bottom: -2px;
                }

                .tab:hover {
                    color: #495057;
                }

                .tab.active {
                    color: #667eea;
                    border-bottom-color: #667eea;
                }

                .tab-content {
                    display: none;
                }

                .tab-content.active {
                    display: block;
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
                    margin-bottom: 0.5rem;
                }

                .empty-state-subtext {
                    font-size: 0.875rem;
                    color: #94a3b8;
                }

                .history-item {
                    padding: 0.75rem;
                    background: #f8f9fa;
                    border-radius: 6px;
                    margin-bottom: 0.5rem;
                    cursor: pointer;
                    transition: all 0.2s;
                    border: 1px solid transparent;
                }

                .history-item:hover {
                    background: #e9ecef;
                    border-color: #dee2e6;
                }

                .history-item-header {
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    margin-bottom: 0.25rem;
                }

                .history-item-method {
                    font-weight: 600;
                    font-size: 0.75rem;
                }

                .history-item-time {
                    font-size: 0.75rem;
                    color: #6c757d;
                }

                .history-item-path {
                    font-size: 0.75rem;
                    color: #495057;
                    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
                    overflow: hidden;
                    text-overflow: ellipsis;
                    white-space: nowrap;
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

                .collapsed {
                    display: none;
                }

                .group-toggle {
                    background: transparent;
                    border: none;
                    color: #6c757d;
                    cursor: pointer;
                    transition: transform 0.2s;
                }

                .group-toggle.expanded {
                    transform: rotate(90deg);
                }

                .code-block {
                    background: #1e293b;
                    color: #e2e8f0;
                    padding: 1rem;
                    border-radius: 6px;
                    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
                    font-size: 0.875rem;
                    line-height: 1.5;
                    overflow-x: auto;
                    margin-top: 0.5rem;
                }

                .copy-btn {
                    float: right;
                    padding: 0.25rem 0.5rem;
                    background: #475569;
                    color: #e2e8f0;
                    border: none;
                    border-radius: 4px;
                    font-size: 0.75rem;
                    cursor: pointer;
                    transition: background 0.2s;
                }

                .copy-btn:hover {
                    background: #64748b;
                }
            </style>

            <div class="explorer-container">
                <div class="explorer-header">
                    <h1 class="explorer-title">API Explorer</h1>
                    <p class="explorer-subtitle">Browse and test API endpoints interactively</p>
                </div>

                <div class="explorer-layout">
                    ${this.renderSidebar()}
                    ${this.renderMainContent()}
                </div>
            </div>
        `;

        this.attachEventListeners();
    }

    renderSidebar() {
        return `
            <div class="sidebar">
                <div class="sidebar-header">
                    <input type="text" class="search-box" placeholder="🔍 Search endpoints..." id="search-input">
                </div>
                <div class="route-groups">
                    ${Object.entries(this.groupedRoutes).map(([tag, routes]) => this.renderRouteGroup(tag, routes)).join('')}
                </div>
            </div>
        `;
    }

    renderRouteGroup(tag, routes) {
        const isExpanded = !this.selectedTag || this.selectedTag === tag;

        return `
            <div class="route-group">
                <div class="group-header" data-tag="${tag}">
                    <button class="group-toggle ${isExpanded ? 'expanded' : ''}">▶</button>
                    <span class="group-title">${tag}</span>
                    <span class="group-count">${routes.length}</span>
                </div>
                <div class="route-list ${!isExpanded ? 'collapsed' : ''}" data-tag-routes="${tag}">
                    ${routes.map(route => this.renderRouteItem(route)).join('')}
                </div>
            </div>
        `;
    }

    renderRouteItem(route) {
        const methods = route.methods || [];
        const method = methods[0] || 'GET';
        const isSelected = this.selectedRoute &&
                          this.selectedRoute.path === route.path &&
                          this.selectedRoute.methods[0] === method;

        return `
            <div class="route-item ${isSelected ? 'selected' : ''}" 
                 data-route-path="${route.path}"
                 data-route-method="${method}">
                <span class="method-badge method-${method.toLowerCase()}">${method}</span>
                <span class="route-path">${route.path}</span>
            </div>
        `;
    }

    renderMainContent() {
        if (!this.selectedRoute) {
            return `
                <div class="main-content">
                    <div class="empty-state">
                        <div class="empty-state-icon">🚀</div>
                        <div class="empty-state-text">Select an endpoint to test</div>
                        <div class="empty-state-subtext">Choose from the routes on the left to get started</div>
                    </div>
                </div>
            `;
        }

        return `
            <div class="main-content">
                <div class="content-header">
                    <div class="route-info">
                        <span class="method-badge method-${this.selectedRoute.methods[0].toLowerCase()}">
                            ${this.selectedRoute.methods[0]}
                        </span>
                        <span class="route-full-path">${this.selectedRoute.path}</span>
                    </div>
                    <div class="route-name">
                        ${this.selectedRoute.name || 'Unnamed endpoint'}
                    </div>
                </div>
                <div class="content-body">
                    <div class="tabs">
                        <button class="tab active" data-tab="test">Test</button>
                        <button class="tab" data-tab="docs">Documentation</button>
                        <button class="tab" data-tab="code">Code Examples</button>
                        <button class="tab" data-tab="history">History</button>
                    </div>
                    
                    <div class="tab-content active" data-tab-content="test">
                        ${this.renderTestSection()}
                    </div>
                    
                    <div class="tab-content" data-tab-content="docs">
                        ${this.renderDocsSection()}
                    </div>
                    
                    <div class="tab-content" data-tab-content="code">
                        ${this.renderCodeSection()}
                    </div>
                    
                    <div class="tab-content" data-tab-content="history">
                        ${this.renderHistorySection()}
                    </div>
                </div>
            </div>
        `;
    }

    renderTestSection() {
        const pathParams = this.extractPathParams(this.selectedRoute.path);
        const method = this.selectedRoute.methods[0];
        const needsBody = ['POST', 'PUT', 'PATCH'].includes(method);

        return `
            <div class="test-section">
                <div class="section-title">
                    🧪 Test Endpoint
                </div>
                
                <div class="params-form">
                    ${pathParams.length > 0 ? `
                        <div class="section-title">Path Parameters</div>
                        ${pathParams.map(param => `
                            <div class="form-group">
                                <label class="form-label" for="param-${param}">${param}</label>
                                <input type="text" class="form-control" id="param-${param}" 
                                       placeholder="Enter ${param}">
                            </div>
                        `).join('')}
                    ` : ''}
                    
                    ${needsBody ? `
                        <div class="section-title">Request Body</div>
                        <div class="form-group">
                            <textarea class="form-control textarea" id="request-body" 
                                      placeholder='{"key": "value"}'></textarea>
                        </div>
                    ` : ''}
                    
                    <div class="form-group">
                        <label class="form-label" for="custom-headers">Custom Headers (Optional)</label>
                        <textarea class="form-control" id="custom-headers" 
                                  placeholder='{"Authorization": "Bearer token"}'
                                  style="min-height: 60px;"></textarea>
                    </div>
                </div>
                
                <button class="btn btn-primary" id="test-btn">
                    <span>Send Request</span>
                </button>
                <button class="btn btn-secondary" id="clear-btn">
                    Clear
                </button>
                
                <div id="response-container"></div>
            </div>
        `;
    }

    renderDocsSection() {
        return `
            <div class="test-section">
                <div class="section-title">
                    📚 Documentation
                </div>
                <p>Endpoint: <strong>${this.selectedRoute.path}</strong></p>
                <p>Method: <strong>${this.selectedRoute.methods.join(', ')}</strong></p>
                <p>Handler: <code>${this.selectedRoute.name || 'N/A'}</code></p>
                
                ${this.selectedRoute.is_get ? '<p>✅ Supports GET requests</p>' : ''}
                ${this.selectedRoute.is_post ? '<p>✅ Supports POST requests</p>' : ''}
                ${this.selectedRoute.is_put ? '<p>✅ Supports PUT requests</p>' : ''}
                ${this.selectedRoute.is_delete ? '<p>✅ Supports DELETE requests</p>' : ''}
                
                <div class="section-title" style="margin-top: 2rem;">
                    🔗 Full URL
                </div>
                <div class="code-block">
                    ${window.location.origin}${this.selectedRoute.path}
                </div>
            </div>
        `;
    }

    renderCodeSection() {
        const method = this.selectedRoute.methods[0];
        const path = this.selectedRoute.path;
        const url = `${window.location.origin}${path}`;

        const curlExample = this.generateCurlExample(method, url);
        const jsExample = this.generateJavaScriptExample(method, url);
        const pythonExample = this.generatePythonExample(method, url);

        return `
            <div class="test-section">
                <div class="section-title">
                    💻 Code Examples
                </div>
                
                <div class="section-title" style="font-size: 0.875rem; margin-top: 1rem;">
                    cURL
                    <button class="copy-btn" data-copy="curl">Copy</button>
                </div>
                <div class="code-block" id="curl-code">${curlExample}</div>
                
                <div class="section-title" style="font-size: 0.875rem; margin-top: 1rem;">
                    JavaScript (Fetch)
                    <button class="copy-btn" data-copy="js">Copy</button>
                </div>
                <div class="code-block" id="js-code">${jsExample}</div>
                
                <div class="section-title" style="font-size: 0.875rem; margin-top: 1rem;">
                    Python (Requests)
                    <button class="copy-btn" data-copy="python">Copy</button>
                </div>
                <div class="code-block" id="python-code">${pythonExample}</div>
            </div>
        `;
    }

    renderHistorySection() {
        const relevantHistory = this.testHistory.filter(
            item => item.path === this.selectedRoute.path
        );

        if (relevantHistory.length === 0) {
            return `
                <div class="test-section">
                    <div class="section-title">
                        🕐 Request History
                    </div>
                    <div class="empty-state" style="padding: 2rem;">
                        <div class="empty-state-text">No requests yet</div>
                        <div class="empty-state-subtext">Test this endpoint to see history</div>
                    </div>
                </div>
            `;
        }

        return `
            <div class="test-section">
                <div class="section-title">
                    🕐 Request History
                </div>
                ${relevantHistory.map((item, index) => `
                    <div class="history-item" data-history-index="${index}">
                        <div class="history-item-header">
                            <span class="history-item-method method-badge method-${item.method.toLowerCase()}">
                                ${item.method}
                            </span>
                            <span class="history-item-time">${this.formatTime(item.timestamp)}</span>
                        </div>
                        <div class="history-item-path">${item.path}</div>
                        <div style="display: flex; gap: 0.5rem; margin-top: 0.25rem;">
                            <span class="response-status ${item.success ? 'status-success' : 'status-error'}" 
                                  style="font-size: 0.75rem; padding: 0.125rem 0.5rem;">
                                ${item.status}
                            </span>
                            <span style="font-size: 0.75rem; color: #6c757d;">
                                ${item.duration}ms
                            </span>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    extractPathParams(path) {
        const matches = path.match(/{([^}]+)}/g);
        return matches ? matches.map(m => m.slice(1, -1)) : [];
    }

    generateCurlExample(method, url) {
        if (method === 'GET') {
            return `curl -X GET "${url}" \\
  -H "Accept: application/json"`;
        } else if (method === 'POST') {
            return `curl -X POST "${url}" \\
  -H "Content-Type: application/json" \\
  -H "Accept: application/json" \\
  -d '{"key": "value"}'`;
        } else if (method === 'PUT') {
            return `curl -X PUT "${url}" \\
  -H "Content-Type: application/json" \\
  -H "Accept: application/json" \\
  -d '{"key": "value"}'`;
        } else if (method === 'DELETE') {
            return `curl -X DELETE "${url}" \\
  -H "Accept: application/json"`;
        }
        return `curl -X ${method} "${url}"`;
    }

    generateJavaScriptExample(method, url) {
        if (method === 'GET') {
            return `fetch('${url}', {
  method: 'GET',
  headers: {
    'Accept': 'application/json'
  }
})
.then(response => response.json())
.then(data => console.log(data))
.catch(error => console.error('Error:', error));`;
        } else if (['POST', 'PUT'].includes(method)) {
            return `fetch('${url}', {
  method: '${method}',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  body: JSON.stringify({
    key: 'value'
  })
})
.then(response => response.json())
.then(data => console.log(data))
.catch(error => console.error('Error:', error));`;
        }
        return `fetch('${url}', {
  method: '${method}'
})
.then(response => response.json())
.then(data => console.log(data));`;
    }

    generatePythonExample(method, url) {
        if (method === 'GET') {
            return `import requests

response = requests.get('${url}')
print(response.json())`;
        } else if (['POST', 'PUT'].includes(method)) {
            return `import requests

data = {
    'key': 'value'
}

response = requests.${method.toLowerCase()}('${url}', json=data)
print(response.json())`;
        } else if (method === 'DELETE') {
            return `import requests

response = requests.delete('${url}')
print(response.status_code)`;
        }
        return `import requests

response = requests.request('${method}', '${url}')
print(response.json())`;
    }

    attachMainContentEventListeners() {
        // Tab switching
        this.shadowRoot.querySelectorAll('.tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                this.switchTab(e.target.dataset.tab);
            });
        });

        // Test button
        const testBtn = this.shadowRoot.getElementById('test-btn');
        if (testBtn) {
            testBtn.addEventListener('click', () => this.testEndpoint());
        }

        // Clear button
        const clearBtn = this.shadowRoot.getElementById('clear-btn');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.clearForm());
        }

        // Copy buttons
        this.shadowRoot.querySelectorAll('.copy-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const type = e.target.dataset.copy;
                this.copyCode(type);
            });
        });

        // History item clicks
        this.shadowRoot.querySelectorAll('.history-item').forEach(item => {
            item.addEventListener('click', (e) => {
                const index = e.currentTarget.dataset.historyIndex;
                this.loadHistoryItem(index);
            });
        });
    }

    attachEventListeners() {
        // Search functionality
        const searchInput = this.shadowRoot.getElementById('search-input');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => this.filterRoutes(e.target.value));
        }

        // Group toggle
        this.shadowRoot.querySelectorAll('.group-header').forEach(header => {
            header.addEventListener('click', (e) => {
                const tag = e.currentTarget.dataset.tag;
                this.toggleGroup(tag);
            });
        });

        // Route selection
        this.shadowRoot.querySelectorAll('.route-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const path = e.currentTarget.dataset.routePath;
                const method = e.currentTarget.dataset.routeMethod;
                this.selectRoute(path, method);
            });
        });

        // Tab switching
        this.shadowRoot.querySelectorAll('.tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                this.switchTab(e.target.dataset.tab);
            });
        });

        // Test button
        const testBtn = this.shadowRoot.getElementById('test-btn');
        if (testBtn) {
            testBtn.addEventListener('click', () => this.testEndpoint());
        }

        // Clear button
        const clearBtn = this.shadowRoot.getElementById('clear-btn');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.clearForm());
        }

        // Copy buttons
        this.shadowRoot.querySelectorAll('.copy-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const type = e.target.dataset.copy;
                this.copyCode(type);
            });
        });

        // History item clicks
        this.shadowRoot.querySelectorAll('.history-item').forEach(item => {
            item.addEventListener('click', (e) => {
                const index = e.currentTarget.dataset.historyIndex;
                this.loadHistoryItem(index);
            });
        });
    }

    filterRoutes(searchTerm) {
        const term = searchTerm.toLowerCase();
        this.shadowRoot.querySelectorAll('.route-item').forEach(item => {
            const path = item.dataset.routePath.toLowerCase();
            const method = item.dataset.routeMethod.toLowerCase();
            const matches = path.includes(term) || method.includes(term);
            item.style.display = matches ? 'flex' : 'none';
        });

        // Show/hide groups based on visible routes
        this.shadowRoot.querySelectorAll('.route-group').forEach(group => {
            const hasVisibleRoutes = group.querySelectorAll('.route-item:not([style*="none"])').length > 0;
            group.style.display = hasVisibleRoutes ? 'block' : 'none';
        });
    }

    toggleGroup(tag) {
        const routeList = this.shadowRoot.querySelector(`[data-tag-routes="${tag}"]`);
        const toggle = this.shadowRoot.querySelector(`.group-header[data-tag="${tag}"] .group-toggle`);

        if (routeList && toggle) {
            routeList.classList.toggle('collapsed');
            toggle.classList.toggle('expanded');
        }
    }

    selectRoute(path, method) {
        this.selectedRoute = this.routes.find(
            r => r.path === path && r.methods.includes(method)
        );

        // Instead of this.render(), just update the main content
        const mainContent = this.shadowRoot.querySelector('.main-content');
        if (mainContent) {
            mainContent.outerHTML = this.renderMainContent();

            // Re-attach event listeners for the new content
            this.attachMainContentEventListeners();
        }

        // Update selected state in sidebar without re-rendering
        this.shadowRoot.querySelectorAll('.route-item').forEach(item => {
            const isSelected = item.dataset.routePath === path &&
                              item.dataset.routeMethod === method;
            item.classList.toggle('selected', isSelected);
        });
    }

    switchTab(tabName) {
        this.shadowRoot.querySelectorAll('.tab').forEach(tab => {
            tab.classList.toggle('active', tab.dataset.tab === tabName);
        });

        this.shadowRoot.querySelectorAll('.tab-content').forEach(content => {
            content.classList.toggle('active', content.dataset.tabContent === tabName);
        });
    }

    async testEndpoint() {
        const testBtn = this.shadowRoot.getElementById('test-btn');
        const responseContainer = this.shadowRoot.getElementById('response-container');

        if (!testBtn || !responseContainer) return;

        // Build URL with path parameters
        let url = this.selectedRoute.path;
        const pathParams = this.extractPathParams(url);
        pathParams.forEach(param => {
            const input = this.shadowRoot.getElementById(`param-${param}`);
            if (input && input.value) {
                url = url.replace(`{${param}}`, input.value);
            }
        });

        // Get request body if needed
        const method = this.selectedRoute.methods[0];
        let body = null;
        const bodyInput = this.shadowRoot.getElementById('request-body');
        if (bodyInput && bodyInput.value) {
            try {
                body = JSON.parse(bodyInput.value);
            } catch {
                body = bodyInput.value;
            }
        }

        // Get custom headers
        let customHeaders = {};
        const headersInput = this.shadowRoot.getElementById('custom-headers');
        if (headersInput && headersInput.value) {
            try {
                customHeaders = JSON.parse(headersInput.value);
            } catch {
                // Invalid JSON, ignore
            }
        }

        // Show loading state
        testBtn.disabled = true;
        testBtn.innerHTML = '<span class="loading"></span> Sending...';

        const startTime = Date.now();

        try {
            const options = {
                method: method,
                headers: {
                    'Accept': 'application/json',
                    ...customHeaders
                }
            };

            if (body && ['POST', 'PUT', 'PATCH'].includes(method)) {
                options.headers['Content-Type'] = 'application/json';
                options.body = typeof body === 'string' ? body : JSON.stringify(body);
            }

            const response = await fetch(url, options);
            const duration = Date.now() - startTime;

            let responseData;
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                responseData = await response.json();
            } else {
                responseData = await response.text();
            }

            // Add to history
            this.testHistory.unshift({
                path: this.selectedRoute.path,
                method: method,
                status: response.status,
                success: response.ok,
                duration: duration,
                timestamp: new Date(),
                response: responseData
            });

            // Display response
            responseContainer.innerHTML = `
                <div class="response-section">
                    <div class="response-header">
                        <span class="response-status ${response.ok ? 'status-success' : 'status-error'}">
                            Status: ${response.status} ${response.statusText}
                        </span>
                        <span class="response-time">Time: ${duration}ms</span>
                    </div>
                    <div class="response-body">
                        <pre>${this.formatJson(responseData)}</pre>
                    </div>
                </div>
            `;
        } catch (error) {
            const duration = Date.now() - startTime;

            responseContainer.innerHTML = `
                <div class="response-section">
                    <div class="response-header">
                        <span class="response-status status-error">
                            Error: ${error.message}
                        </span>
                        <span class="response-time">Time: ${duration}ms</span>
                    </div>
                    <div class="response-body">
                        <pre>${error.stack || error.message}</pre>
                    </div>
                </div>
            `;
        } finally {
            testBtn.disabled = false;
            testBtn.innerHTML = 'Send Request';
        }
    }

    clearForm() {
        this.shadowRoot.querySelectorAll('.form-control').forEach(input => {
            input.value = '';
        });

        const responseContainer = this.shadowRoot.getElementById('response-container');
        if (responseContainer) {
            responseContainer.innerHTML = '';
        }
    }

    copyCode(type) {
        let codeElement;
        if (type === 'curl') {
            codeElement = this.shadowRoot.getElementById('curl-code');
        } else if (type === 'js') {
            codeElement = this.shadowRoot.getElementById('js-code');
        } else if (type === 'python') {
            codeElement = this.shadowRoot.getElementById('python-code');
        }

        if (codeElement) {
            navigator.clipboard.writeText(codeElement.textContent).then(() => {
                const btn = this.shadowRoot.querySelector(`[data-copy="${type}"]`);
                if (btn) {
                    const originalText = btn.textContent;
                    btn.textContent = 'Copied!';
                    setTimeout(() => {
                        btn.textContent = originalText;
                    }, 2000);
                }
            });
        }
    }

    loadHistoryItem(index) {
        const item = this.testHistory[index];
        if (item) {
            this.switchTab('test');
            // Could populate form with historical values
        }
    }

    formatJson(obj) {
        if (typeof obj === 'string') {
            try {
                obj = JSON.parse(obj);
            } catch {
                return obj;
            }
        }

        return JSON.stringify(obj, null, 2)
            .replace(/(".*?")/g, '<span class="json-key">$1</span>')
            .replace(/: "([^"]*)"/g, ': <span class="json-string">"$1"</span>')
            .replace(/: (\d+)/g, ': <span class="json-number">$1</span>')
            .replace(/: (true|false)/g, ': <span class="json-boolean">$1</span>')
            .replace(/: null/g, ': <span class="json-null">null</span>');
    }

    formatTime(date) {
        const now = new Date();
        const diff = now - date;

        if (diff < 60000) {
            return 'Just now';
        } else if (diff < 3600000) {
            return `${Math.floor(diff / 60000)}m ago`;
        } else if (diff < 86400000) {
            return `${Math.floor(diff / 3600000)}h ago`;
        } else {
            return date.toLocaleDateString();
        }
    }
}

// Register the custom element
customElements.define('api-explorer', APIExplorer);

// Export for use in other modules
export { APIExplorer };