# Quick Start Guide

## Installation

```bash
pip install osbot-fast-api
````
### Basic Setup

```
from osbot_fast_api import Fast_API
from osbot_fast_api.admin_ui import Admin_UI__Fast_API

# Create your FastAPI app
app = Fast_API(name="My API", version="1.0.0")

# Add Admin UI
admin = Admin_UI__Fast_API(parent_app=app)
admin.setup()

# Start the server
app.start_server()
```

### Configuration

Configure the admin UI through the Admin_UI__Config class...

