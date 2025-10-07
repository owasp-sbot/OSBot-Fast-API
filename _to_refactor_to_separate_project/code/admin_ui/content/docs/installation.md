# Installation

## System Requirements

Before installing FastAPI Admin UI, ensure your system meets the following requirements:

### Python Version
- **Minimum**: Python 3.8 or higher
- **Recommended**: Python 3.10+ for optimal performance
- **Testing**: Fully tested on Python 3.8, 3.9, 3.10, 3.11, and 3.12

### Dependencies
The Admin UI requires the following core dependencies:
- `fastapi >= 0.100.0` - The web framework
- `uvicorn >= 0.23.0` - ASGI server for running the application
- `starlette >= 0.27.0` - ASGI framework used by FastAPI
- `pydantic >= 2.0.0` - Data validation and settings management
- `osbot-utils >= 1.0.0` - Utility functions and type safety

## Installation Methods

### 1. Install via pip (Recommended)

The simplest way to install FastAPI Admin UI is through pip:

```bash
# Install the latest stable version
pip install osbot-fast-api

# Install with all optional dependencies
pip install osbot-fast-api[all]

# Install a specific version
pip install osbot-fast-api==1.0.0
```

### 2. Install from Source

For development or to get the latest features:

```bash
# Clone the repository
git clone https://github.com/owasp-sbot/OSBot-Fast-API.git
cd OSBot-Fast-API

# Install in development mode
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

### 3. Install in Virtual Environment

It's recommended to use a virtual environment to avoid conflicts:

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install the package
pip install osbot-fast-api
```

### 4. Install with Poetry

If you're using Poetry for dependency management:

```bash
# Add to your project
poetry add osbot-fast-api

# Or add as a development dependency
poetry add --dev osbot-fast-api
```

## Verify Installation

After installation, verify everything is working correctly:

```python
# Check if the package is installed
python -c "import osbot_fast_api; print(osbot_fast_api.__version__)"

# Test basic functionality
python -c "from osbot_fast_api import Fast_API; print('Installation successful!')"
```

## Post-Installation Setup

### 1. Create Your First App

Create a new Python file `main.py`:

```python
from osbot_fast_api import Fast_API
from osbot_fast_api.admin_ui import Admin_UI__Fast_API

# Initialize FastAPI application
app = Fast_API(
    name="My API",
    version="1.0.0",
    description="My FastAPI application with Admin UI"
)

# Add the Admin UI
admin = Admin_UI__Fast_API(parent_app=app)
admin.setup()

# Add your API routes here
@app.app().get("/hello")
def hello():
    return {"message": "Hello, World!"}

# Start the server (for development)
if __name__ == "__main__":
    app.start_server(port=8000)
```

### 2. Run Your Application

Start your FastAPI application with the Admin UI:

```bash
# Run directly with Python
python main.py

# Or use uvicorn for more control
uvicorn main:app --reload --port 8000
```

### 3. Access the Admin UI

Once your application is running, access the Admin UI at:
- Admin Dashboard: `http://localhost:8000/admin`
- API Documentation: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Configuration Options

### Basic Configuration

```python
from osbot_fast_api.admin_ui import Admin_UI__Config

config = Admin_UI__Config(
    enabled=True,           # Enable/disable Admin UI
    base_path='/admin',     # URL path for Admin UI
    require_auth=False,     # Require authentication
    show_dashboard=True,    # Show dashboard page
    show_cookies=True,      # Show cookie manager
    show_routes=True,       # Show API routes explorer
    show_docs=True,         # Show documentation viewer
    allow_api_testing=True  # Allow API testing from UI
)

admin = Admin_UI__Fast_API(
    parent_app=app,
    admin_config=config
)
```

### Environment Variables

You can also configure the Admin UI using environment variables:

```bash
# Enable/disable features
export ADMIN_UI_ENABLED=true
export ADMIN_UI_BASE_PATH=/admin
export ADMIN_UI_REQUIRE_AUTH=false

# API configuration
export FAST_API__AUTH__API_KEY__NAME=X-API-Key
export FAST_API__AUTH__API_KEY__VALUE=your-secret-key
```

## Troubleshooting

### Common Issues

**Import Error**: If you get an import error, ensure all dependencies are installed:
```bash
pip install --upgrade osbot-fast-api
```

**Port Already in Use**: If port 8000 is already in use:
```python
app.start_server(port=8080)  # Use a different port
```

**Static Files Not Loading**: Ensure the static files path is correctly configured:
```python
admin.path_static_folder()  # Check the static files path
```

**Authentication Issues**: If authentication is enabled but not working:
```python
# Disable auth for testing
config.require_auth = False
```

## Upgrading

To upgrade to the latest version:

```bash
# Upgrade to the latest version
pip install --upgrade osbot-fast-api

# Check the current version
python -c "import osbot_fast_api; print(osbot_fast_api.__version__)"
```

## Uninstallation

To remove the package:

```bash
pip uninstall osbot-fast-api
```

## Next Steps

Now that you have the Admin UI installed, explore:
- [Quick Start Guide](#docs/quickstart) - Get up and running quickly
- [Authentication Setup](#docs/authentication) - Secure your Admin UI
- [API Explorer](#docs/testing-guide) - Learn to test your APIs
- [Cookie Management](#docs/cookies-guide) - Manage API credentials