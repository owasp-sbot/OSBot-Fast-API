# API Testing Guide

## Introduction

The API Explorer in FastAPI Admin UI provides a powerful, interactive interface for testing your API endpoints without leaving your browser or writing any code. This guide covers everything from basic endpoint testing to advanced scenarios with authentication, file uploads, and WebSocket connections.

## Getting Started with API Explorer

### Accessing the API Explorer

1. Navigate to `http://localhost:8000/admin`
2. Click on "API Routes" in the sidebar
3. The API Explorer will load with all your discovered endpoints

### Understanding the Interface

The API Explorer consists of three main areas:

1. **Sidebar**: Browse and search through all available endpoints
2. **Main Content**: Detailed endpoint information and testing interface
3. **Response Area**: View test results and response data

## Basic Endpoint Testing

### Testing a GET Endpoint

1. Select a GET endpoint from the sidebar
2. Fill in any required path parameters
3. Click "Send Request"
4. View the response in the response area

**Example**: Testing `/api/users/{user_id}`
```
Path Parameter: user_id = 123
Click: Send Request

Response:
{
  "id": 123,
  "name": "John Doe",
  "email": "john@example.com"
}
```

### Testing a POST Endpoint

1. Select a POST endpoint
2. Enter the request body in JSON format
3. Add any required headers
4. Send the request

**Example**: Creating a new user
```json
Request Body:
{
  "name": "Jane Smith",
  "email": "jane@example.com",
  "password": "secure123"
}

Response:
{
  "id": 456,
  "name": "Jane Smith",
  "email": "jane@example.com",
  "created_at": "2024-01-15T10:30:00Z"
}
```

## Working with Parameters

### Path Parameters

Path parameters are part of the URL path:

```
Endpoint: /api/users/{user_id}/posts/{post_id}

Path Parameters:
- user_id: 123
- post_id: 456

Resulting URL: /api/users/123/posts/456
```

### Query Parameters

Query parameters are appended to the URL:

```
Endpoint: /api/search

Query Parameters:
- q: "fastapi"
- limit: 10
- offset: 0

Resulting URL: /api/search?q=fastapi&limit=10&offset=0
```

### Headers

Custom headers for authentication or content negotiation:

```json
Custom Headers:
{
  "Authorization": "Bearer your-token-here",
  "X-API-Version": "2.0",
  "Accept-Language": "en-US"
}
```

## Request Body Formatting

### JSON Payloads

The most common format for API requests:

```json
{
  "title": "New Blog Post",
  "content": "This is the content...",
  "tags": ["fastapi", "python", "api"],
  "published": true,
  "metadata": {
    "author": "John Doe",
    "category": "Tech"
  }
}
```

### Form Data

For form-encoded requests:

```
Content-Type: application/x-www-form-urlencoded

username=johndoe&password=secret&remember=true
```

### File Uploads

For multipart form data with files:

```
Content-Type: multipart/form-data

file: [Select File]
description: "Profile photo"
```

## Authentication in Tests

### Using API Keys

API keys from the Cookie Manager are automatically included:

1. Set your API key in Cookie Manager
2. Test protected endpoints normally
3. The key is automatically added to requests

### Bearer Token Authentication

For JWT or OAuth tokens:

```json
Headers:
{
  "Authorization": "Bearer eyJhbGciOiJIUzI1NiIs..."
}
```

### Basic Authentication

For username/password authentication:

```json
Headers:
{
  "Authorization": "Basic am9objpwYXNzd29yZA=="
}
```

## Response Handling

### Understanding Response Data

The response area shows:

- **Status Code**: HTTP status (200, 404, 500, etc.)
- **Response Time**: How long the request took
- **Headers**: Response headers from the server
- **Body**: The actual response data

### Status Code Indicators

- 🟢 **2xx Success**: Request was successful
- 🟡 **3xx Redirect**: Request was redirected
- 🟠 **4xx Client Error**: Problem with the request
- 🔴 **5xx Server Error**: Server-side problem

### Response Formats

#### JSON Response
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "name": "Test"
  }
}
```

#### Plain Text Response
```
Operation completed successfully
```

#### HTML Response
```html
<html>
  <body>
    <h1>Success</h1>
  </body>
</html>
```

## Advanced Testing Features

### Request History

The API Explorer maintains a history of your requests:

1. Click the "History" tab
2. View past requests with their responses
3. Click on a history item to reload it
4. Useful for comparing responses

### Code Generation

Generate code snippets for your tests:

#### cURL
```bash
curl -X POST "http://localhost:8000/api/users" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer token123" \
  -d '{"name":"John","email":"john@example.com"}'
```

#### Python
```python
import requests

url = "http://localhost:8000/api/users"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer token123"
}
data = {
    "name": "John",
    "email": "john@example.com"
}

response = requests.post(url, json=data, headers=headers)
print(response.json())
```

#### JavaScript
```javascript
fetch('http://localhost:8000/api/users', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer token123'
  },
  body: JSON.stringify({
    name: 'John',
    email: 'john@example.com'
  })
})
.then(response => response.json())
.then(data => console.log(data));
```

### Environment Variables

Use variables in your tests:

```
Base URL: {{base_url}}
API Key: {{api_key}}
User ID: {{test_user_id}}

Resolved:
http://localhost:8000/api/users/123
```

## Testing Different HTTP Methods

### GET - Retrieve Data
```
Purpose: Fetch resources
Idempotent: Yes
Body: Usually none
Example: GET /api/users
```

### POST - Create Resources
```
Purpose: Create new resources
Idempotent: No
Body: Required
Example: POST /api/users
```

### PUT - Update Resources
```
Purpose: Replace entire resource
Idempotent: Yes
Body: Required
Example: PUT /api/users/123
```

### PATCH - Partial Update
```
Purpose: Update part of resource
Idempotent: Yes
Body: Required
Example: PATCH /api/users/123
```

### DELETE - Remove Resources
```
Purpose: Delete resources
Idempotent: Yes
Body: Usually none
Example: DELETE /api/users/123
```

## Testing Pagination

### Offset-Based Pagination

```
GET /api/items?offset=20&limit=10

Parameters:
- offset: 20 (skip first 20 items)
- limit: 10 (return 10 items)
```

### Page-Based Pagination

```
GET /api/items?page=3&per_page=10

Parameters:
- page: 3 (third page)
- per_page: 10 (items per page)
```

### Cursor-Based Pagination

```
GET /api/items?cursor=eyJpZCI6MTAwfQ==&limit=10

Parameters:
- cursor: encoded position
- limit: items to return
```

## Error Testing

### Testing Error Responses

Deliberately trigger errors to test error handling:

#### 400 Bad Request
```json
Request Body: (invalid JSON)
{
  "email": "not-an-email"
}

Response:
{
  "error": "Validation Error",
  "detail": "Email must be a valid email address"
}
```

#### 401 Unauthorized
```
Headers: (no authentication)

Response:
{
  "error": "Unauthorized",
  "detail": "Authentication required"
}
```

#### 404 Not Found
```
GET /api/users/99999

Response:
{
  "error": "Not Found",
  "detail": "User with ID 99999 not found"
}
```

## Performance Testing

### Response Time Analysis

Monitor response times for performance:

```
Endpoint: GET /api/users
Response Time: 125ms ✅ Good

Endpoint: POST /api/reports/generate
Response Time: 3500ms ⚠️ Slow
```

### Load Testing Tips

While the API Explorer isn't for load testing, you can:

1. Test endpoint functionality before load testing
2. Identify slow endpoints that need optimization
3. Export working requests as cURL/code for load testing tools
4. Use the generated code with tools like Apache JMeter or k6

## WebSocket Testing

### Connecting to WebSocket Endpoints

```javascript
// WebSocket connection example
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = () => {
    console.log('Connected');
    ws.send(JSON.stringify({type: 'subscribe', channel: 'updates'}));
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
};

ws.onerror = (error) => {
    console.error('WebSocket error:', error);
};
```

### Testing WebSocket Messages

Send different message types to test your WebSocket handlers:

```json
// Subscribe to updates
{
  "type": "subscribe",
  "channel": "notifications"
}

// Send data
{
  "type": "message",
  "data": {
    "text": "Hello, server!"
  }
}

// Unsubscribe
{
  "type": "unsubscribe",
  "channel": "notifications"
}
```

## File Upload Testing

### Single File Upload

```
Endpoint: POST /api/upload
Content-Type: multipart/form-data

Fields:
- file: [Select File] → document.pdf
- description: "Important document"

Response:
{
  "filename": "document.pdf",
  "size": 102400,
  "url": "/files/document.pdf"
}
```

### Multiple File Upload

```
Endpoint: POST /api/upload-multiple
Content-Type: multipart/form-data

Fields:
- files: [Select Multiple Files]
  - image1.jpg
  - image2.png
  - document.pdf
- category: "project-files"

Response:
{
  "uploaded": 3,
  "files": [
    {"name": "image1.jpg", "size": 51200},
    {"name": "image2.png", "size": 30720},
    {"name": "document.pdf", "size": 102400}
  ]
}
```

## Testing Best Practices

### 1. Start with Happy Path

Always test the successful case first:

```
✅ Valid input → Expected output
✅ Proper authentication → Access granted
✅ Correct parameters → Successful response
```

### 2. Test Edge Cases

Then test boundary conditions:

```
⚠️ Empty input
⚠️ Maximum length strings
⚠️ Minimum/maximum numeric values
⚠️ Special characters
⚠️ Unicode characters
```

### 3. Test Error Scenarios

Verify error handling:

```
❌ Invalid input → Proper error message
❌ Missing authentication → 401 response
❌ Non-existent resources → 404 response
❌ Server errors → Graceful failure
```

### 4. Document Your Tests

Keep notes on test scenarios:

```markdown
## User Creation Tests

### Test 1: Valid User
- Input: Valid email and password
- Expected: 201 Created with user object
- Result: ✅ Passed

### Test 2: Duplicate Email
- Input: Existing email address
- Expected: 409 Conflict
- Result: ✅ Passed

### Test 3: Invalid Email Format
- Input: "not-an-email"
- Expected: 400 Bad Request
- Result: ✅ Passed
```

## Debugging with API Explorer

### Inspecting Request Details

Use the browser's Developer Tools (F12) alongside API Explorer:

1. Open Network tab
2. Send request from API Explorer
3. Inspect actual request headers and payload
4. Check response headers and timing

### Common Issues and Solutions

#### CORS Errors
**Problem**: "Access to fetch at ... from origin ... has been blocked by CORS policy"

**Solution**:
```python
# Enable CORS in your FastAPI app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 415 Unsupported Media Type
**Problem**: Server rejects the request format

**Solution**:
```json
// Ensure correct Content-Type header
{
  "Content-Type": "application/json"
}
```

#### Request Timeout
**Problem**: Request takes too long and times out

**Solution**:
- Check if endpoint is working correctly
- Verify database connections
- Look for infinite loops or blocking operations

## Integration Testing Workflows

### Complete User Flow Test

Test a complete user journey:

```
1. POST /api/auth/register
   → Create new user account

2. POST /api/auth/login
   → Get authentication token

3. GET /api/users/profile
   → Fetch user profile (authenticated)

4. PUT /api/users/profile
   → Update profile information

5. POST /api/posts
   → Create a new post

6. GET /api/posts?user_id={id}
   → Verify post was created

7. DELETE /api/posts/{post_id}
   → Clean up test data
```

### API Version Testing

Test different API versions:

```
# Version 1
GET /api/v1/users
Headers: {"Accept": "application/vnd.api+json;version=1"}

# Version 2
GET /api/v2/users
Headers: {"Accept": "application/vnd.api+json;version=2"}

Compare responses for backward compatibility
```

## Exporting and Sharing Tests

### Export Test Configuration

Save your test setup for reuse:

```json
{
  "endpoint": "/api/users",
  "method": "POST",
  "headers": {
    "Content-Type": "application/json",
    "Authorization": "Bearer {{token}}"
  },
  "body": {
    "name": "{{userName}}",
    "email": "{{userEmail}}"
  },
  "variables": {
    "userName": "John Doe",
    "userEmail": "john@example.com"
  }
}
```

### Share with Team

Generate shareable links or export configurations:

1. Copy the generated cURL command
2. Share Python/JavaScript code snippets
3. Export as Postman collection (if supported)
4. Document in your API documentation

## Automation Ideas

### Pre-request Scripts

While the API Explorer doesn't support scripts directly, you can:

```javascript
// Generate test data before request
const timestamp = Date.now();
const testEmail = `test_${timestamp}@example.com`;

// Use in your request body
{
  "email": testEmail,
  "name": "Test User"
}
```

### Post-request Validation

Mentally or manually verify:

```
✓ Status code is 200-299
✓ Response time < 1000ms
✓ Required fields are present
✓ Data types are correct
✓ Business logic is satisfied
```

## Performance Optimization Tips

### Identify Slow Endpoints

Look for patterns in slow responses:

- Large data sets without pagination
- Missing database indexes
- N+1 query problems
- Unnecessary data in responses

### Optimize Request Payload

Reduce request size:

```json
// Instead of sending entire object
{
  "user": {
    "id": 1,
    "name": "John",
    "email": "john@example.com",
    "created_at": "...",
    "updated_at": "...",
    // ... 20 more fields
  }
}

// Send only what's needed
{
  "user_id": 1
}
```

## Security Testing

### SQL Injection Tests

Test for SQL injection vulnerabilities:

```
Input: '; DROP TABLE users; --
Expected: Proper escaping, no SQL execution
```

### XSS Testing

Test for cross-site scripting:

```
Input: <script>alert('XSS')</script>
Expected: Proper HTML escaping in response
```

### Authentication Bypass

Test authentication boundaries:

```
1. Access protected endpoint without token
2. Use expired token
3. Use token with insufficient permissions
4. Modify token payload (JWT)
```

## Next Steps

- [Cookie Management](#docs/cookies-guide) - Set up authentication for tests
- [Authentication](#docs/authentication) - Understand security requirements
- [Monitoring](#docs/monitoring-guide) - Track API performance
- [API Endpoints](#docs/endpoints) - Complete endpoint reference