from fastapi                                            import Request, Response
from fastapi.responses                                  import HTMLResponse
from osbot_fast_api.api.schemas.consts.consts__Fast_API import ENV_VAR__FAST_API__AUTH__API_KEY__NAME
from osbot_utils.type_safe.Type_Safe                    import Type_Safe
from osbot_utils.utils.Env                              import get_env, load_dotenv
from osbot_fast_api.api.routes.Fast_API__Routes         import Fast_API__Routes

# todo: (once this class has been moved into a better location, move this schema also to a better location
class Schema__Set_Cookie(Type_Safe):
    cookie_value: str

# todo: these are actually routes, so we should move them into a better location
#       maybe 'default_routes' or something similar

ROUTES_PATHS__SET_COOKIE = ['/auth/set-auth-cookie' ,
                            '/auth/set-cookie-form']


class Routes__Set_Cookie(Fast_API__Routes):
    tag: str = 'auth'

    def set_cookie_form(self, request: Request):   # Display form to edit auth cookie with JSON submission
        load_dotenv()
        cookie_name    = get_env(ENV_VAR__FAST_API__AUTH__API_KEY__NAME) or 'auth-cookie'  # Fallback if not set
        current_cookie = request.cookies.get(cookie_name, '') if cookie_name else ''

        # Check if environment variable is properly configured
        env_warning = ""
        if not get_env(ENV_VAR__FAST_API__AUTH__API_KEY__NAME):
            env_warning = f"""
            <div class="warning">
                <strong>⚠️ Warning:</strong> Environment variable <code>{ENV_VAR__FAST_API__AUTH__API_KEY__NAME}</code> is not set.
                Using default cookie name: <code>auth-cookie</code>
            </div>
            """

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Auth Cookie Editor</title>
            <style>{CSS__AUTH_COOKIE_EDITOR}</style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔐 Auth Cookie Editor</h1>
                    <p class="subtitle">Manage your API authentication cookie</p>
                </div>
                
                {env_warning}
                
                <div class="info-section">
                    <div class="info-item">
                        <label>Cookie Name:</label>
                        <code class="cookie-name">{cookie_name}</code>
                    </div>
                    <div class="info-item">
                        <label>Current Value:</label>
                        <code id="currentValue" class="cookie-value">{current_cookie or '(not set)'}</code>
                        <button class="copy-btn" onclick="copyValue('{current_cookie}')" title="Copy current value">
                            📋
                        </button>
                    </div>
                    <div class="info-item">
                        <label>Environment Variable:</label>
                        <code class="env-var">{ENV_VAR__FAST_API__AUTH__API_KEY__NAME}</code>
                    </div>
                </div>
                
                <div id="message"></div>
                
                <form id="cookieForm" class="cookie-form">
                    <div class="form-group">
                        <label for="cookie_value">New Cookie Value:</label>
                        <div class="input-group">
                            <input type="text" 
                                   id="cookie_value" 
                                   name="cookie_value" 
                                   value="{current_cookie}"
                                   placeholder="Enter API key or authentication token...">
                            <button type="button" 
                                    class="generate-btn" 
                                    onclick="generateUUID()"
                                    title="Generate new UUID">
                                🎲 Generate
                            </button>
                        </div>
                        <small class="help-text">Enter your API key or click Generate for a new UUID</small>
                    </div>
                    
                    <div class="button-group">
                        <button type="submit" id="submitBtn" class="submit-btn">
                            ✅ Set Cookie
                        </button>
                        <button type="button" onclick="clearCookie()" class="clear-btn">
                            🗑️ Clear Cookie
                        </button>
                    </div>
                </form>
                
                <div class="footer">
                    <p>Cookie will be set with: <code>httponly=true</code>, <code>samesite=strict</code>, 
                       <code>secure={'true' if request.url.scheme == 'https' else 'false'}</code></p>
                </div>
            </div>

            <script>
                const form = document.getElementById('cookieForm');
                const messageDiv = document.getElementById('message');
                const submitBtn = document.getElementById('submitBtn');
                const currentValueSpan = document.getElementById('currentValue');
                const cookieInput = document.getElementById('cookie_value');
                const cookieName = '{cookie_name}';

                const setAuthCookie = async (value) => {{
                    const res = await fetch("/auth/set-auth-cookie", {{
                        method: "POST",
                        headers: {{ "Content-Type": "application/json" }},
                        body: JSON.stringify({{ cookie_value: value }}),
                        credentials: "same-origin"
                    }});
                    
                    if (!res.ok) {{
                        let errorText = 'Unknown error';
                        try {{
                            const errorData = await res.json();
                            errorText = errorData.detail || errorData.message || await res.text();
                        }} catch {{
                            errorText = await res.text();
                        }}
                        throw new Error(errorText || `HTTP error! status: ${{res.status}}`);
                    }}
                    
                    return res.json();
                }};

                form.addEventListener('submit', async (e) => {{
                    e.preventDefault();
                    
                    const value = cookieInput.value.trim();
                    
                    // Disable button during submission
                    submitBtn.disabled = true;
                    submitBtn.innerHTML = '⏳ Setting...';
                    
                    try {{
                        const result = await setAuthCookie(value);
                        
                        // Show success message
                        showMessage('success', '✅ ' + (result.message || 'Cookie set successfully'));
                        
                        // Update current value display
                        currentValueSpan.textContent = value || '(not set)';
                        
                    }} catch (error) {{
                        // Show error message
                        showMessage('error', '❌ Error: ' + error.message);
                    }} finally {{
                        // Re-enable button
                        submitBtn.disabled = false;
                        submitBtn.innerHTML = '✅ Set Cookie';
                    }}
                }});
                
                function showMessage(type, text) {{
                    messageDiv.className = 'message ' + type;
                    messageDiv.textContent = text;
                    messageDiv.style.display = 'block';
                    
                    // Clear message after 5 seconds
                    setTimeout(() => {{
                        messageDiv.style.display = 'none';
                    }}, 5000);
                }}
                
                function generateUUID() {{
                    const uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {{
                        const r = Math.random() * 16 | 0;
                        const v = c == 'x' ? r : (r & 0x3 | 0x8);
                        return v.toString(16);
                    }});
                    cookieInput.value = uuid;
                    cookieInput.focus();
                }}
                
                async function clearCookie() {{
                    if (confirm('Are you sure you want to clear the authentication cookie?')) {{
                        cookieInput.value = '';
                        form.dispatchEvent(new Event('submit'));
                    }}
                }}
                
                function copyValue(value) {{
                    if (!value) {{
                        showMessage('warning', '⚠️ No value to copy');
                        return;
                    }}
                    navigator.clipboard.writeText(value).then(() => {{
                        showMessage('success', '📋 Copied to clipboard');
                    }}).catch(() => {{
                        showMessage('error', '❌ Failed to copy');
                    }});
                }}
            </script>
        </body>
        </html>
        """

        return HTMLResponse(content=html_content)

    def set_auth_cookie(self, set_cookie: Schema__Set_Cookie, request: Request, response: Response):  # Set the auth cookie via JSON request
        cookie_name = get_env(ENV_VAR__FAST_API__AUTH__API_KEY__NAME) or 'auth-cookie'  # Fallback if not set
        secure_flag = request.url.scheme == 'https'

        # Set the cookie
        response.set_cookie(key         = cookie_name            ,
                            value       = set_cookie.cookie_value,
                            httponly    = True                   ,
                            secure      = secure_flag            ,
                            samesite    ='strict'                )

        return {    "message"     : "Cookie set successfully",
                    "cookie_name" : cookie_name              ,
                    "cookie_value": set_cookie.cookie_value  }

    def setup_routes(self):
        self.add_route_get (self.set_cookie_form)
        self.add_route_post(self.set_auth_cookie)


# CSS at the end of file as requested
CSS__AUTH_COOKIE_EDITOR = """
    body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        margin: 0;
        padding: 20px;
        
        min-height: 100vh;
    }
    .container {
        max-width: 600px;
        margin: 0 auto;
        background: white;
        border-radius: 12px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        overflow: hidden;
    }
    .header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 30px;
        text-align: center;
    }
    .header h1 {
        margin: 0;
        font-size: 28px;
    }
    .subtitle {
        margin: 10px 0 0 0;
        opacity: 0.9;
        font-size: 14px;
    }
    .warning {
        background: #fff3cd;
        border-left: 4px solid #ffc107;
        color: #856404;
        padding: 15px;
        margin: 20px;
        border-radius: 4px;
    }
    .warning code {
        background: rgba(0,0,0,0.05);
        padding: 2px 6px;
        border-radius: 3px;
    }
    .info-section {
        background: #f8f9fa;
        padding: 20px;
        margin: 20px;
        border-radius: 8px;
    }
    .info-item {
        display: flex;
        align-items: center;
        margin-bottom: 15px;
        padding: 10px;
        background: white;
        border-radius: 6px;
    }
    .info-item:last-child {
        margin-bottom: 0;
    }
    .info-item label {
        font-weight: 600;
        color: #495057;
        min-width: 150px;
        font-size: 14px;
    }
    .info-item code {
        font-family: 'Monaco', 'Menlo', monospace;
        background: #e9ecef;
        padding: 6px 12px;
        border-radius: 4px;
        font-size: 13px;
        flex-grow: 1;
    }
    .cookie-name {
        background: #e7f3ff !important;
        color: #0066cc;
    }
    .cookie-value {
        background: #e8f5e9 !important;
        color: #2e7d32;
    }
    .env-var {
        background: #fce4ec !important;
        color: #c2185b;
    }
    .copy-btn {
        background: #6c757d;
        color: white;
        border: none;
        padding: 6px 10px;
        border-radius: 4px;
        cursor: pointer;
        font-size: 14px;
        margin-left: 10px;
        transition: background 0.2s;
    }
    .copy-btn:hover {
        background: #5a6268;
    }
    .cookie-form {
        padding: 20px;
    }
    .form-group {
        margin-bottom: 20px;
    }
    .form-group label {
        display: block;
        font-weight: 600;
        color: #333;
        margin-bottom: 8px;
    }
    .input-group {
        display: flex;
        gap: 10px;
    }
    .input-group input {
        flex: 1;
        padding: 12px;
        border: 2px solid #e0e0e0;
        border-radius: 6px;
        font-size: 14px;
        font-family: 'Monaco', 'Menlo', monospace;
        transition: border-color 0.3s;
    }
    .input-group input:focus {
        outline: none;
        border-color: #667eea;
    }
    .generate-btn {
        background: #17a2b8;
        color: white;
        border: none;
        padding: 12px 20px;
        border-radius: 6px;
        cursor: pointer;
        font-size: 14px;
        white-space: nowrap;
        transition: background 0.2s;
    }
    .generate-btn:hover {
        background: #138496;
    }
    .help-text {
        display: block;
        margin-top: 5px;
        color: #6c757d;
        font-size: 12px;
    }
    .button-group {
        display: flex;
        gap: 10px;
    }
    .submit-btn {
        flex: 1;
        background: #28a745;
        color: white;
        border: none;
        padding: 14px;
        border-radius: 6px;
        font-size: 16px;
        font-weight: 600;
        cursor: pointer;
        transition: background 0.2s;
    }
    .submit-btn:hover:not(:disabled) {
        background: #218838;
    }
    .submit-btn:disabled {
        background: #ccc;
        cursor: not-allowed;
    }
    .clear-btn {
        background: #dc3545;
        color: white;
        border: none;
        padding: 14px 20px;
        border-radius: 6px;
        font-size: 16px;
        font-weight: 600;
        cursor: pointer;
        transition: background 0.2s;
    }
    .clear-btn:hover {
        background: #c82333;
    }
    .message {
        padding: 12px;
        margin: 0 20px 20px 20px;
        border-radius: 6px;
        display: none;
        animation: slideIn 0.3s ease;
    }
    .message.success {
        background: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    .message.error {
        background: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
    .message.warning {
        background: #fff3cd;
        color: #856404;
        border: 1px solid #ffeeba;
    }
    .footer {
        background: #f8f9fa;
        padding: 15px;
        text-align: center;
        font-size: 12px;
        color: #6c757d;
    }
    .footer code {
        background: #e9ecef;
        padding: 2px 6px;
        border-radius: 3px;
    }
    @keyframes slideIn {
        from {
            transform: translateY(-10px);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }
"""