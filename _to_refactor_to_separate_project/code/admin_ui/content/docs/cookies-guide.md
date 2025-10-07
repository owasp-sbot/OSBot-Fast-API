# Cookie Management Guide

## Introduction

The Cookie Manager is a powerful feature of the FastAPI Admin UI that simplifies the management of authentication tokens, API keys, and other sensitive credentials. This guide will walk you through everything you need to know about managing cookies effectively and securely.

## Why Use the Cookie Manager?

Managing API credentials can be challenging, especially when working with multiple services. The Cookie Manager provides:

- **Centralized Management**: All your API keys and tokens in one place
- **Security**: Encrypted storage with configurable security settings
- **Templates**: Pre-configured templates for popular services
- **Validation**: Automatic validation of API key formats
- **Convenience**: No need to manually set headers for every request

## Getting Started

### Accessing the Cookie Manager

1. Navigate to your Admin UI at `http://localhost:8000/admin`
2. Click on "Cookie Manager" in the sidebar
3. You'll see a list of configured cookies and available templates

### Understanding the Interface

The Cookie Manager interface consists of three main sections:

1. **Actions Bar**: Quick actions like adding cookies and generating values
2. **Templates Section**: Pre-configured cookie templates for common services
3. **Cookies Table**: List of all cookies with their current status

## Using Cookie Templates

Templates provide pre-configured cookie settings for popular services.

### Available Templates

#### OpenAI Configuration
Perfect for OpenAI API integration:
- **Cookie Name**: `openai-api-key`
- **Format**: `sk-[48 characters]`
- **Security**: HTTPS-only, HttpOnly

#### Anthropic Configuration
For Claude API integration:
- **Cookie Name**: `anthropic-api-key`
- **Format**: `sk-ant-[95 characters]`
- **Security**: HTTPS-only, HttpOnly

#### Authentication Template
General authentication tokens:
- **Cookie Name**: `auth-token`
- **Type**: Session or JWT token
- **Security**: Strict SameSite policy

### Applying a Template

1. Click on a template card to select it
2. Click "Apply Template" button
3. Enter your actual API key or token values
4. Save the configuration

## Managing Individual Cookies

### Adding a New Cookie

1. Click the "➕ Add Cookie" button
2. Enter the cookie details:
   ```
   Name: my-api-key
   Value: your-secret-key-here
   Expires In: 3600 (optional, in seconds)
   ```
3. Click "Save Cookie"

### Editing an Existing Cookie

1. Find the cookie in the table
2. Click the ✏️ edit icon
3. Modify the value (name cannot be changed)
4. Save your changes

### Deleting a Cookie

1. Click the 🗑️ delete icon next to the cookie
2. Confirm the deletion

## Generating Secure Values

The Cookie Manager can generate secure random values:

### Generate UUID
Click "🎲 Generate UUID" to create a universally unique identifier:
```
550e8400-e29b-41d4-a716-446655440000
```

### Generate API Key
Click "🔑 Generate API Key" to create a mock API key:
```
sk-Xy7Kp9Lm2Nq4Rs6Tv8Wz1Ab3Cd5Ef7Gh9Jk2Mn4Pq6St8Vx
```

These values are automatically copied to your clipboard.

## Security Best Practices

### Cookie Security Settings

Always use appropriate security settings for your environment:

```python
{
    "secure": True,      # HTTPS only
    "http_only": True,   # No JavaScript access
    "same_site": "strict" # CSRF protection
}
```

### Development vs Production

#### Development Settings
```python
{
    "secure": False,     # Allow HTTP
    "http_only": True,
    "same_site": "lax"
}
```

#### Production Settings
```python
{
    "secure": True,      # HTTPS required
    "http_only": True,
    "same_site": "strict",
    "max_age": 3600     # Short expiration
}
```

## Cookie Validation

The Cookie Manager includes built-in validation for common API key formats:

### OpenAI Keys
Pattern: `^sk-[a-zA-Z0-9]{48}$`
```
✅ Valid: sk-abcdef1234567890abcdef1234567890abcdef12345678
❌ Invalid: sk-short
```

### Anthropic Keys
Pattern: `^sk-ant-[a-zA-Z0-9-]{95}$`
```
✅ Valid: sk-ant-[95 characters]
❌ Invalid: sk-ant-short
```

### Custom Validation

You can add custom validation patterns:

```python
Cookie__Config(
    name="custom-api-key",
    validator=r"^api_[A-Z0-9]{32}$"
)
```

## Integration with API Testing

Cookies set through the Cookie Manager are automatically included in API requests:

### Automatic Inclusion
When testing APIs through the Admin UI Explorer, cookies are automatically sent:

```javascript
// Cookies are included automatically
fetch('/api/protected-endpoint', {
    credentials: 'include'  // Sends cookies
})
```

### Manual Testing
For manual testing with curl:

```bash
# Export cookies
curl -b "api-key=your-key; auth-token=your-token" \
     http://localhost:8000/api/endpoint
```

## Bulk Operations

### Setting Multiple Cookies

Use the bulk set endpoint for multiple cookies:

```python
cookies_to_set = [
    {"name": "api-key", "value": "key-123"},
    {"name": "auth-token", "value": "token-456"},
    {"name": "session-id", "value": "session-789"}
]

# All cookies are set in a single operation
```

### Export/Import Cookies

While not directly supported in the UI, you can export cookies via the API:

```bash
# Export all cookies
curl http://localhost:8000/admin/admin-cookies/api/cookies-list \
     -H "X-API-Key: your-admin-key" > cookies.json

# Process and reimport as needed
```

## Troubleshooting

### Cookie Not Being Set

**Problem**: Cookie appears to save but isn't visible in requests.

**Solutions**:
- Check browser developer tools (F12) → Application → Cookies
- Verify security settings match your environment (HTTP vs HTTPS)
- Ensure SameSite policy allows the cookie for your use case

### Validation Errors

**Problem**: "Value does not match required pattern"

**Solutions**:
- Check the exact format required by the validator
- Remove any extra spaces or hidden characters
- Use the "Generate API Key" feature for correct format

### Cookie Not Persisting

**Problem**: Cookie disappears after browser restart.

**Solutions**:
- Set an explicit `max_age` or `expires_in` value
- Check if browser is configured to clear cookies on exit
- Verify the cookie isn't a session cookie (no expiration set)

## Advanced Configuration

### Custom Cookie Templates

Create your own templates by modifying the configuration:

```python
custom_template = {
    "id": "my-service",
    "name": "My Service API",
    "description": "Custom service configuration",
    "cookies": [
        {
            "name": "my-service-key",
            "description": "API Key for My Service",
            "required": True,
            "category": "custom",
            "validator": "^msv_[a-zA-Z0-9]{40}$"
        }
    ]
}
```

### Environment-Specific Cookies

Use environment variables to set different cookies per environment:

```bash
# Development
export DEV_API_KEY=dev-key-123

# Production
export PROD_API_KEY=prod-key-456
```

### Cookie Rotation

Implement automatic cookie rotation for enhanced security:

```python
from datetime import datetime, timedelta

def rotate_cookie(cookie_name: str):
    # Generate new value
    new_value = generate_api_key()
    
    # Set with short expiration
    set_cookie(cookie_name, new_value, expires_in=3600)
    
    # Log rotation for audit
    log_cookie_rotation(cookie_name, datetime.now())
```

## Integration Examples

### With OpenAI

```python
# Set OpenAI API key via Cookie Manager
cookie_name = "openai-api-key"
cookie_value = "sk-proj-abcdef..."  # Your actual key

# Now requests to OpenAI endpoints will include this key
response = requests.get('/api/openai/complete', 
                        cookies={'openai-api-key': cookie_value})
```

### With Custom Authentication

```python
# Set authentication token
cookie_name = "auth-token"
cookie_value = jwt_token  # Your JWT token

# Protected endpoints now accessible
response = requests.get('/api/protected',
                        cookies={'auth-token': cookie_value})
```

## Best Practices Summary

1. **Use Templates**: Start with templates for common services
2. **Secure Settings**: Always use HTTPS in production
3. **Short Expiration**: Set reasonable expiration times
4. **Validate Format**: Use validators to ensure correct format
5. **Rotate Regularly**: Change API keys periodically
6. **Audit Access**: Log cookie usage for security audits
7. **Environment Separation**: Different keys for dev/staging/prod

## Next Steps

- [Authentication Guide](#docs/authentication) - Secure your cookies
- [API Testing](#docs/testing-guide) - Use cookies in API tests
- [Security Best Practices](#docs/authentication) - Advanced security configuration