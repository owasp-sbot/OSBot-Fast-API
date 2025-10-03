/**
 * Documentation Viewer Web Component
 * Displays markdown documentation and guides
 */

class DocsViewer extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
        this.currentDoc = 'overview';
        this.docContent = {};
        this.apiBase = '/admin/admin-docs/api';
    }

    connectedCallback() {
        this.render();
        // Don't load default content - wait for parent to specify  // note: this was causing flicking on the screen when navigating
        // if (!this.currentDoc) {
        //     this.showPlaceholder();
        // }
    }

    // showPlaceholder() {                                          // note: this was causing flicking on the screen when navigating (if needed explore other ways to do this)
    //     const contentArea = this.shadowRoot.getElementById('content-area');
    //     if (contentArea) {
    //         contentArea.innerHTML = '<div class="loading">Loading documentation...</div>';
    //     }
    // }

    setDocs(docs) {
        this.docs = docs || [];
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

                .docs-container {
                    display: grid;
                    grid-template-columns: 300px 1fr;
                    gap: 2rem;
                    max-width: 1400px;
                    margin: 0 auto;
                }

                .docs-sidebar {
                    background: white;
                    border-radius: 8px;
                    padding: 1.5rem;
                    height: fit-content;
                    position: sticky;
                    top: 2rem;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                }

                .docs-main {
                    background: white;
                    border-radius: 8px;
                    padding: 2rem;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                    min-height: 600px;
                }

                .docs-header {
                    margin-bottom: 2rem;
                    padding-bottom: 1rem;
                    border-bottom: 2px solid #e9ecef;
                }

                .docs-title {
                    font-size: 2rem;
                    font-weight: 600;
                    color: #212529;
                    margin: 0 0 0.5rem 0;
                }

                .docs-subtitle {
                    color: #6c757d;
                    font-size: 1rem;
                }

                .sidebar-section {
                    margin-bottom: 2rem;
                }

                .sidebar-title {
                    font-size: 0.875rem;
                    font-weight: 600;
                    text-transform: uppercase;
                    color: #6c757d;
                    margin-bottom: 1rem;
                    letter-spacing: 0.05em;
                }

                .doc-link {
                    display: block;
                    padding: 0.5rem 0.75rem;
                    margin-bottom: 0.25rem;
                    color: #495057;
                    text-decoration: none;
                    border-radius: 6px;
                    transition: all 0.2s;
                    cursor: pointer;
                    font-size: 0.875rem;
                }

                .doc-link:hover {
                    background: #f8f9fa;
                    color: #212529;
                }

                .doc-link.active {
                    background: #f8f9ff;
                    color: #667eea;
                    font-weight: 500;
                    border-left: 3px solid #667eea;
                }

                .doc-link-icon {
                    display: inline-block;
                    width: 20px;
                    margin-right: 0.5rem;
                }

                .doc-link.external {
                    color: #6c757d;
                    font-size: 0.8rem;
                }

                .doc-link.external:hover {
                    color: #667eea;
                }

                .markdown-content {
                    line-height: 1.8;
                    color: #495057;
                    font-size: 1rem;
                }

                .markdown-content h1 {
                    font-size: 2rem;
                    font-weight: 600;
                    color: #212529;
                    margin: 2rem 0 1rem 0;
                    padding-bottom: 0.5rem;
                    border-bottom: 2px solid #e9ecef;
                }

                .markdown-content h1:first-child {
                    margin-top: 0;
                }

                .markdown-content h2 {
                    font-size: 1.5rem;
                    font-weight: 600;
                    color: #212529;
                    margin: 1.5rem 0 1rem 0;
                }

                .markdown-content h3 {
                    font-size: 1.25rem;
                    font-weight: 600;
                    color: #495057;
                    margin: 1.25rem 0 0.75rem 0;
                }

                .markdown-content p {
                    margin-bottom: 1rem;
                }

                .markdown-content ul,
                .markdown-content ol {
                    margin: 0 0 1rem 2rem;
                }

                .markdown-content li {
                    margin-bottom: 0.5rem;
                }

                .markdown-content code {
                    background: #f6f8fa;
                    padding: 0.2rem 0.4rem;
                    border-radius: 3px;
                    font-family: 'Monaco', 'Menlo', monospace;
                    font-size: 0.875em;
                    color: #d73a49;
                }

                .markdown-content pre {
                    background: #1e293b;
                    color: #e2e8f0;
                    padding: 1rem;
                    border-radius: 6px;
                    overflow-x: auto;
                    margin: 1rem 0;
                }

                .markdown-content pre code {
                    background: transparent;
                    color: inherit;
                    padding: 0;
                }

                .markdown-content blockquote {
                    border-left: 4px solid #667eea;
                    padding-left: 1rem;
                    margin: 1rem 0;
                    color: #6c757d;
                    font-style: italic;
                }

                .markdown-content table {
                    width: 100%;
                    border-collapse: collapse;
                    margin: 1rem 0;
                }

                .markdown-content th,
                .markdown-content td {
                    padding: 0.75rem;
                    border: 1px solid #e9ecef;
                    text-align: left;
                }

                .markdown-content th {
                    background: #f8f9fa;
                    font-weight: 600;
                }

                .loading {
                    text-align: center;
                    padding: 3rem;
                    color: #6c757d;
                }

                .error-message {
                    padding: 2rem;
                    text-align: center;
                    color: #dc2626;
                    background: #fef2f2;
                    border-radius: 6px;
                    margin: 2rem 0;
                }

                .divider {
                    height: 1px;
                    background: #e9ecef;
                    margin: 1rem 0;
                }
            </style>

            <div class="docs-container">
                <div class="docs-sidebar">
                    <div class="sidebar-section">
                        <div class="sidebar-title">Getting Started</div>
                        <a class="doc-link" data-doc="overview">
                            <span class="doc-link-icon">🏠</span>
                            Overview
                        </a>
                        <a class="doc-link" data-doc="quickstart">
                            <span class="doc-link-icon">🚀</span>
                            Quick Start
                        </a>
                        <a class="doc-link" data-doc="installation">
                            <span class="doc-link-icon">📦</span>
                            Installation
                        </a>
                    </div>

                    <div class="sidebar-section">
                        <div class="sidebar-title">API Reference</div>
                        <a class="doc-link" data-doc="endpoints">
                            <span class="doc-link-icon">🔌</span>
                            Endpoints
                        </a>
                        <a class="doc-link" data-doc="authentication">
                            <span class="doc-link-icon">🔐</span>
                            Authentication
                        </a>
                        <a class="doc-link" data-doc="schemas">
                            <span class="doc-link-icon">📋</span>
                            Schemas
                        </a>
                    </div>

                    <div class="sidebar-section">
                        <div class="sidebar-title">Guides</div>
                        <a class="doc-link" data-doc="cookies-guide">
                            <span class="doc-link-icon">🍪</span>
                            Cookie Management
                        </a>
                        <a class="doc-link" data-doc="testing-guide">
                            <span class="doc-link-icon">🧪</span>
                            Testing APIs
                        </a>
                        <a class="doc-link" data-doc="monitoring-guide">
                            <span class="doc-link-icon">📊</span>
                            Monitoring
                        </a>
                    </div>

                    <div class="divider"></div>

                    <div class="sidebar-section">
                        <div class="sidebar-title">External Docs</div>
                        <a href="/docs" target="_blank" class="doc-link external">
                            <span class="doc-link-icon">📖</span>
                            Swagger UI ↗
                        </a>
                        <a href="/redoc" target="_blank" class="doc-link external">
                            <span class="doc-link-icon">📄</span>
                            ReDoc ↗
                        </a>
                        <a href="/openapi.json" target="_blank" class="doc-link external">
                            <span class="doc-link-icon">📋</span>
                            OpenAPI JSON ↗
                        </a>
                    </div>
                </div>

                <div class="docs-main">
<!--                    <div class="docs-header">-->
<!--                        <h1 class="docs-title" id="doc-title">Documentation</h1>-->
<!--                        <p class="docs-subtitle" id="doc-subtitle">Loading...</p>-->
<!--                    </div>-->
                    <div id="content-area" class="markdown-content">
                        <div class="loading">Loading documentation...</div>
                    </div>
                </div>
            </div>
        `;

        this.attachEventListeners();
    }

    attachEventListeners() {
        // Documentation links
        this.shadowRoot.querySelectorAll('.doc-link[data-doc]').forEach(link => {
            link.addEventListener('click', async (e) => {
                e.preventDefault();
                const docId = e.currentTarget.dataset.doc;

                // Dispatch navigation event to update URL
                this.dispatchEvent(new CustomEvent('navigate-to-doc', {
                    detail: { docId },
                    bubbles: true,
                    composed: true
                }));

                await this.loadDocContent(docId);
            });
        });
    }

    async loadDocContent(docId) {
        // Update active state
        this.shadowRoot.querySelectorAll('.doc-link').forEach(link => {
            link.classList.toggle('active', link.dataset.doc === docId);
        });

        const contentArea = this.shadowRoot.getElementById('content-area');
        //const docTitle = this.shadowRoot.getElementById('doc-title');         // no need for this since we get this from the markdown content
        //const docSubtitle = this.shadowRoot.getElementById('doc-subtitle');

        if (!contentArea) return;

        // Show loading state
        //contentArea.innerHTML = '<div class="loading">Loading documentation...</div>';

        try {
            // Try to fetch from API
            const response = await fetch(`${this.apiBase}/content/${docId}`);

            if (response.ok) {
                const content = await response.json();

                // Update title based on doc
                const titles = {
                    'overview': 'Overview',
                    'quickstart': 'Quick Start Guide',
                    'installation': 'Installation',
                    'endpoints': 'API Endpoints',
                    'authentication': 'Authentication',
                    'schemas': 'Data Schemas',
                    'cookies-guide': 'Cookie Management Guide',
                    'testing-guide': 'API Testing Guide',
                    'monitoring-guide': 'Monitoring Guide'
                };

                //docTitle.textContent = titles[docId] || 'Documentation';
                //docSubtitle.textContent = this.getSubtitle(docId);

                // Render content
                if (content.markdown) {
                    contentArea.innerHTML = this.parseMarkdown(content.markdown);
                } else if (content.sections) {
                    contentArea.innerHTML = this.renderSections(content.sections);
                } else {
                    contentArea.innerHTML = this.getDefaultContent(docId);
                }
            } else {
                // Use default content if API fails
                contentArea.innerHTML = this.getDefaultContent(docId);
            }
        } catch (error) {
            console.error('Error loading documentation:', error);
            contentArea.innerHTML = this.getDefaultContent(docId);
        }

        this.currentDoc = docId;
    }

    getSubtitle(docId) {
        const subtitles = {
            'overview': 'Complete reference for the FastAPI Admin UI',
            'quickstart': 'Get up and running in minutes',
            'installation': 'Setup and configuration instructions',
            'endpoints': 'Available API endpoints reference',
            'authentication': 'Secure your API endpoints',
            'schemas': 'Data models and structures',
            'cookies-guide': 'Managing API keys and authentication',
            'testing-guide': 'Testing your API endpoints',
            'monitoring-guide': 'Monitor performance and usage'
        };
        return subtitles[docId] || 'Documentation and guides';
    }

    parseMarkdown(markdown) {
        // Enhanced markdown parsing
        let html = markdown
            // Headers
            .replace(/^#### (.*$)/gim, '<h3>$1</h3>')
            .replace(/^### (.*$)/gim, '<h3>$1</h3>')
            .replace(/^## (.*$)/gim, '<h2>$1</h2>')
            .replace(/^# (.*$)/gim, '<h1>$1</h1>')
            // Bold and italic
            .replace(/\*\*\*(.*?)\*\*\*/g, '<strong><em>$1</em></strong>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            // Code blocks
            .replace(/```(\w+)?\n([\s\S]*?)```/g, (match, lang, code) => {
                return `<pre><code class="language-${lang || 'plaintext'}">${this.escapeHtml(code.trim())}</code></pre>`;
            })
            // Inline code
            .replace(/`([^`]+)`/g, '<code>$1</code>')
            // Links
            .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>')
            // Lists
            .replace(/^\* (.+)$/gim, '<li>$1</li>')
            .replace(/^- (.+)$/gim, '<li>$1</li>')
            .replace(/^\d+\. (.+)$/gim, '<li>$1</li>')
            // Blockquotes
            .replace(/^> (.+)$/gim, '<blockquote>$1</blockquote>')
            // Paragraphs
            .replace(/\n\n/g, '</p><p>')
            .replace(/^/, '<p>')
            .replace(/$/, '</p>');

        // Wrap consecutive li elements in ul
        html = html.replace(/(<li>.*?<\/li>\s*)+/g, (match) => {
            return `<ul>${match}</ul>`;
        });

        return html;
    }

    escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, m => map[m]);
    }

    renderSections(sections) {
        return sections.map(section => `
            <div class="content-section">
                <h2>${section.title}</h2>
                ${section.content}
            </div>
        `).join('');
    }

    getDefaultContent(docId) {
        const defaultContents = {
            'overview': `
                <h1>Welcome to FastAPI Admin UI</h1>
                <p>The FastAPI Admin UI provides a comprehensive administration interface for your FastAPI applications.</p>
                
                <h2>Features</h2>
                <ul>
                    <li><strong>Real-time Dashboard</strong> - Monitor server statistics and application health</li>
                    <li><strong>API Explorer</strong> - Browse and test all API endpoints interactively</li>
                    <li><strong>Cookie Manager</strong> - Manage authentication tokens and API keys</li>
                    <li><strong>Documentation Hub</strong> - Access all API documentation in one place</li>
                </ul>

                <h2>Getting Started</h2>
                <p>Navigate through the documentation using the sidebar on the left. Start with the <strong>Quick Start</strong> guide to get up and running quickly.</p>

                <h2>Need Help?</h2>
                <p>Check out our guides for detailed instructions on using each feature of the Admin UI.</p>
            `,
            'quickstart': `
                <h1>Quick Start Guide!!!</h1>
                
                <h2>Installation</h2>
                <pre><code>pip install osbot-fast-api</code></pre>
                
                <h2>Basic Setup</h2>
                <pre><code>from osbot_fast_api import Fast_API
from osbot_fast_api.admin_ui import Admin_UI__Fast_API

# Create your FastAPI app
app = Fast_API(name="My API", version="1.0.0")

# Add Admin UI
admin = Admin_UI__Fast_API(parent_app=app)
admin.setup()

# Start the server
app.start_server()</code></pre>

                <h2>Configuration</h2>
                <p>Configure the admin UI through the Admin_UI__Config class:</p>
                <pre><code>from osbot_fast_api.admin_ui import Admin_UI__Config

config = Admin_UI__Config(
    enabled=True,
    base_path='/admin',
    require_auth=True,
    show_dashboard=True,
    show_cookies=True,
    show_routes=True,
    show_docs=True
)</code></pre>

                <h2>Next Steps</h2>
                <ul>
                    <li>Explore the Dashboard for real-time metrics</li>
                    <li>Use the API Explorer to test your endpoints</li>
                    <li>Configure authentication with the Cookie Manager</li>
                </ul>
            `,
            'installation': `
                <h1>Installation Guide</h1>
                
                <h2>Requirements</h2>
                <ul>
                    <li>Python 3.8 or higher</li>
                    <li>FastAPI</li>
                    <li>Uvicorn (for running the server)</li>
                </ul>

                <h2>Install via pip</h2>
                <pre><code>pip install osbot-fast-api</code></pre>

                <h2>Install from source</h2>
                <pre><code>git clone https://github.com/your-repo/osbot-fast-api
cd osbot-fast-api
pip install -e .</code></pre>

                <h2>Verify Installation</h2>
                <pre><code>python -c "import osbot_fast_api; print(osbot_fast_api.__version__)"</code></pre>
            `,
            'authentication': `
                <h1>Authentication</h1>
                
                <h2>API Key Authentication</h2>
                <p>Enable API key authentication in your configuration:</p>
                <pre><code>app = Fast_API(enable_api_key=True)</code></pre>

                <h2>Cookie-based Authentication</h2>
                <p>Use the Cookie Manager to set authentication tokens:</p>
                <ul>
                    <li>Navigate to Cookie Manager in the Admin UI</li>
                    <li>Select an authentication template</li>
                    <li>Enter your API keys or tokens</li>
                    <li>Save the cookies</li>
                </ul>

                <h2>Security Best Practices</h2>
                <ul>
                    <li>Always use HTTPS in production</li>
                    <li>Rotate API keys regularly</li>
                    <li>Use secure cookie settings</li>
                    <li>Implement rate limiting</li>
                </ul>
            `
        };

        return defaultContents[docId] || `
            <div class="error-message">
                <h2>Documentation Not Found</h2>
                <p>The requested documentation page could not be loaded.</p>
                <p>Please try selecting another page from the sidebar.</p>
            </div>
        `;
    }
}

// Register the custom element
customElements.define('docs-viewer', DocsViewer);

// Export for use in other modules
export { DocsViewer };