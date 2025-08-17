from fastapi                                    import Request, Response
from fastapi.responses                          import HTMLResponse
from osbot_utils.type_safe.Type_Safe            import Type_Safe
from osbot_fast_api.api.routes.Fast_API__Routes import Fast_API__Routes
from osbot_fast_api.schemas.consts__Fast_API    import ENV_VAR__FAST_API__AUTH__API_KEY__NAME

class Schema__Set_Cookie(Type_Safe):
    cookie_value: str

class Routes__Set_Cookie(Fast_API__Routes):
    tag: str = 'auth'

    def set_cookie_form(self, request: Request):   # Display form to edit auth cookie with JSON submission
        current_cookie = request.cookies.get(ENV_VAR__FAST_API__AUTH__API_KEY__NAME, '')

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Auth Cookie Editor</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }}
                input {{ width: 100%; padding: 10px; margin: 10px 0; }}
                button {{ background: #4CAF50; color: white; padding: 10px 20px; border: none; cursor: pointer; }}
                button:hover {{ background: #45a049; }}
                button:disabled {{ background: #ccc; cursor: not-allowed; }}
                .current {{ background: #f0f0f0; padding: 10px; margin: 10px 0; }}
                .message {{ padding: 10px; margin: 10px 0; border-radius: 4px; }}
                .success {{ background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
                .error {{ background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }}
            </style>
        </head>
        <body>
            <h1>Auth Cookie Editor</h1>
            <div class="current">
                <strong>Current Cookie Value:</strong><br>
                <code id="currentValue">{current_cookie or '(not set)'}</code>
            </div>
            <div id="message"></div>
            <form id="cookieForm">
                <label for="cookie_value">New Cookie Value:</label>
                <input type="text" id="cookie_value" name="cookie_value" value="{current_cookie}">
                <button type="submit" id="submitBtn">Set Cookie</button>
            </form>

            <script>
                const form = document.getElementById('cookieForm');
                const messageDiv = document.getElementById('message');
                const submitBtn = document.getElementById('submitBtn');
                const currentValueSpan = document.getElementById('currentValue');
                const cookieInput = document.getElementById('cookie_value');

                const setAuthCookie = async (value) => {{
                    const res = await fetch("/auth/set-auth-cookie", {{
                        method: "POST",
                        headers: {{ "Content-Type": "application/json" }},
                        body: JSON.stringify({{ cookie_value: value }}),
                        credentials: "same-origin"
                    }});
                    
                    if (!res.ok) {{
                        const errorText = await res.text();
                        throw new Error(errorText || `HTTP error! status: ${{res.status}}`);
                    }}
                    
                    return res.json();
                }};

                form.addEventListener('submit', async (e) => {{
                    e.preventDefault();
                    
                    const value = cookieInput.value;
                    
                    // Disable button during submission
                    submitBtn.disabled = true;
                    submitBtn.textContent = 'Setting...';
                    
                    try {{
                        const result = await setAuthCookie(value);
                        
                        // Show success message
                        messageDiv.className = 'message success';
                        messageDiv.textContent = result.message || 'Cookie set successfully';
                        
                        // Update current value display
                        currentValueSpan.textContent = value || '(not set)';
                        
                        // Clear message after 3 seconds
                        setTimeout(() => {{
                            messageDiv.className = '';
                            messageDiv.textContent = '';
                        }}, 3000);
                        
                    }} catch (error) {{
                        // Show error message
                        messageDiv.className = 'message error';
                        messageDiv.textContent = `Error: ${{error.message}}`;
                    }} finally {{
                        // Re-enable button
                        submitBtn.disabled = false;
                        submitBtn.textContent = 'Set Cookie';
                    }}
                }});
            </script>
        </body>
        </html>
        """

        return HTMLResponse(content=html_content)

    def set_auth_cookie(self, set_cookie: Schema__Set_Cookie, response: Response):
        """Set the auth cookie via JSON request"""
        cookie_name = ENV_VAR__FAST_API__AUTH__API_KEY__NAME
        response.set_cookie(
            key=cookie_name,
            value=set_cookie.cookie_value,
            httponly=True,
            secure=True,
            samesite='strict'
        )
        return {
            "message": "Cookie set successfully",
            "cookie_name": cookie_name,
            "cookie_value": set_cookie.cookie_value
        }

    def setup_routes(self):
        self.add_route_get (self.set_cookie_form)
        self.add_route_post(self.set_auth_cookie)