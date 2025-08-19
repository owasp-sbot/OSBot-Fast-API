# Authentication

## Overview

Security is paramount when exposing administrative interfaces. The FastAPI Admin UI provides multiple layers of authentication and authorization to protect your API and administrative functions. This guide covers all authentication methods, best practices, and security configurations.

## Authentication Methods

### 1. API Key Authentication

The simplest form of authentication uses API keys passed in request headers.

#### Enable API Key Authentication

```python
from osbot_fast_api import Fast_API

app = Fast_API(
    name="Secure API",
    enable_api_key=True  # Enable API key checking
)

# Set the API key via environment variables
# export FAST_API__AUTH__API_KEY__NAME=X-API-Key
# export FAST_API__AUTH__API_KEY__VALUE=your-secret-api-key-here
```

#### Custom API Key Configuration

```python
from osbot_fast_api.admin_ui import Admin_UI__Config

config = Admin_UI__Config(
    require_auth=True,  # Require authentication for Admin UI
)

# Configure API key header name and value
import os
os.environ['FAST_API__AUTH__API_KEY__NAME'] = 'X-Custom-Auth'
os.environ['FAST_API__AUTH__API_KEY__VALUE'] = 'super-secret-key-123'
```

#### Using API Keys in Requests

```bash
# Include the API key in your requests
curl -H "X-API-Key: your-secret-api-key-here" http://localhost:8000/admin/api/server-info

# Or using Python requests
import requests
headers = {'X-API-Key': 'your-secret-api-key-here'}
response = requests.get('http://localhost:8000/admin/api/server-info', headers=headers)
```

### 2. Cookie-Based Authentication

For browser-based access, cookie authentication provides a seamless user experience.

#### Setting Authentication Cookies

1. Navigate to the Cookie Manager in the Admin UI
2. Select the "Authentication" template
3. Enter your authentication token or API key
4. Save the cookie with appropriate security settings

#### Cookie Configuration

```python
# Configure secure cookie settings
cookie_config = {
    "secure": True,      # Only send over HTTPS
    "http_only": True,   # Not accessible via JavaScript
    "same_site": "strict",  # CSRF protection
    "max_age": 3600     # Expire after 1 hour
}
```

### 3. OAuth 2.0 Integration

For production environments, integrate with OAuth 2.0 providers:

```python
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.app().get("/protected")
async def protected_route(token: str = Depends(oauth2_scheme)):
    # Verify token and return protected data
    return {"data": "protected"}
```

### 4. JWT Token Authentication

Implement JWT tokens for stateless authentication:

```python
import jwt
from datetime import datetime, timedelta

def create_jwt_token(user_id: str) -> str:
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, "SECRET_KEY", algorithm="HS256")

def verify_jwt_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, "SECRET_KEY", algorithms=["HS256"])
        return payload
    except jwt.InvalidTokenError:
        return None
```

## Security Best Practices

### 1. Environment Variables

Never hardcode sensitive credentials. Always use environment variables:

```bash
# .env file (never commit to version control)
ADMIN_API_KEY=your-secret-key-here
JWT_SECRET=your-jwt-secret
OAUTH_CLIENT_ID=your-oauth-client-id
OAUTH_CLIENT_SECRET=your-oauth-secret
```

```python
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

api_key = os.getenv('ADMIN_API_KEY')
jwt_secret = os.getenv('JWT_SECRET')
```

### 2. HTTPS in Production

Always use HTTPS in production environments:

```python
# Force HTTPS redirect
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

app.app().add_middleware(HTTPSRedirectMiddleware)

# Configure secure cookies
config = Admin_UI__Config(
    require_auth=True
)
```

### 3. Rate Limiting

Implement rate limiting to prevent abuse:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/hour"]
)

app.app().state.limiter = limiter
app.app().add_exception_handler(429, _rate_limit_exceeded_handler)

@app.app().get("/api/data")
@limiter.limit("10/minute")
async def get_data(request: Request):
    return {"data": "limited"}
```

### 4. CORS Configuration

Configure CORS properly for your domain:

```python
from fastapi.middleware.cors import CORSMiddleware

app.app().add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specific origins only
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["X-API-Key", "Authorization"],
)
```

## Access Control

### Role-Based Access Control (RBAC)

Implement different access levels for different users:

```python
from enum import Enum

class Role(Enum):
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"

def check_permission(required_role: Role):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Check user role from token/session
            user_role = get_current_user_role()
            if user_role != required_role:
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            return await func(*args, **kwargs)
        return wrapper
    return decorator

@app.app().get("/admin/sensitive")
@check_permission(Role.ADMIN)
async def sensitive_data():
    return {"data": "admin only"}
```

### IP Whitelisting

Restrict access to specific IP addresses:

```python
from fastapi import Request, HTTPException

ALLOWED_IPS = ["192.168.1.1", "10.0.0.1"]

@app.app().middleware("http")
async def ip_whitelist(request: Request, call_next):
    client_ip = request.client.host
    if client_ip not in ALLOWED_IPS:
        raise HTTPException(status_code=403, detail="Access denied")
    response = await call_next(request)
    return response
```

## Security Headers

Add security headers to all responses:

```python
@app.app().middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response
```

## Monitoring and Auditing

### Logging Authentication Attempts

```python
import logging

logger = logging.getLogger(__name__)

def log_auth_attempt(user: str, success: bool, ip: str):
    if success:
        logger.info(f"Successful auth: user={user}, ip={ip}")
    else:
        logger.warning(f"Failed auth attempt: user={user}, ip={ip}")
```

### Session Management

```python
from datetime import datetime, timedelta

class SessionManager:
    def __init__(self):
        self.sessions = {}
    
    def create_session(self, user_id: str) -> str:
        session_id = generate_session_id()
        self.sessions[session_id] = {
            "user_id": user_id,
            "created": datetime.utcnow(),
            "expires": datetime.utcnow() + timedelta(hours=24)
        }
        return session_id
    
    def validate_session(self, session_id: str) -> bool:
        session = self.sessions.get(session_id)
        if not session:
            return False
        if datetime.utcnow() > session["expires"]:
            del self.sessions[session_id]
            return False
        return True
```

## Testing Authentication

### Unit Tests

```python
from fastapi.testclient import TestClient

def test_auth_required():
    client = TestClient(app.app())
    
    # Test without auth
    response = client.get("/admin/api/server-info")
    assert response.status_code == 401
    
    # Test with auth
    headers = {"X-API-Key": "test-key"}
    response = client.get("/admin/api/server-info", headers=headers)
    assert response.status_code == 200
```

## Troubleshooting

### Common Authentication Issues

**401 Unauthorized**: Check that your API key is correct and properly formatted in the header.

**403 Forbidden**: Verify that your user has the necessary permissions for the requested resource.

**CORS Errors**: Ensure your CORS configuration includes the origin making the request.

**Cookie Not Set**: Verify that cookies are enabled and using the correct security settings for your environment.

## Next Steps

- [Cookie Management Guide](#docs/cookies-guide) - Learn to manage authentication cookies
- [API Testing](#docs/testing-guide) - Test authenticated endpoints
- [Monitoring](#docs/monitoring-guide) - Monitor authentication attempts and security events