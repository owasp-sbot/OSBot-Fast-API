# Monitoring Guide

## Introduction

Effective monitoring is crucial for maintaining healthy FastAPI applications. The Admin UI provides comprehensive monitoring capabilities that give you real-time insights into your application's performance, health, and usage patterns. This guide covers everything from basic metrics to advanced observability strategies.

## Dashboard Overview

### Key Metrics at a Glance

The Admin UI dashboard provides instant visibility into:

- **System Status**: Overall health indicator
- **Uptime**: How long your server has been running
- **Total Routes**: Number of API endpoints
- **Active Middlewares**: Processing pipeline components
- **Request Statistics**: Traffic patterns and response times
- **Error Rates**: Failed request percentages

### Understanding the Dashboard

#### System Status Indicator
```
🟢 Healthy - All systems operational
🟡 Warning - Some issues detected
🔴 Critical - Immediate attention required
```

#### Uptime Display
```
Uptime: 5d 14h 23m
Since: 2024-01-10 09:00:00 UTC
Last Restart: Planned maintenance
```

#### Route Statistics
```
Total Routes: 47
├── GET: 25 endpoints
├── POST: 12 endpoints
├── PUT: 6 endpoints
└── DELETE: 4 endpoints
```

## Real-Time Monitoring

### Server Metrics

Monitor your server's vital statistics in real-time:

#### CPU Usage
```python
{
  "cpu_percent": 45.2,
  "cpu_cores": 8,
  "cpu_frequency": 2400,  # MHz
  "load_average": [2.1, 1.8, 1.5]  # 1, 5, 15 minutes
}
```

#### Memory Usage
```python
{
  "memory_total": 16384,  # MB
  "memory_used": 8192,    # MB
  "memory_percent": 50.0,
  "memory_available": 8192  # MB
}
```

#### Disk Usage
```python
{
  "disk_total": 512000,    # MB
  "disk_used": 256000,     # MB
  "disk_free": 256000,     # MB
  "disk_percent": 50.0
}
```

### Application Metrics

Track application-specific metrics:

#### Request Metrics
```python
{
  "total_requests": 1000000,
  "requests_per_second": 150,
  "average_response_time": 125,  # milliseconds
  "median_response_time": 100,   # milliseconds
  "p95_response_time": 500,      # milliseconds
  "p99_response_time": 1000      # milliseconds
}
```

#### Error Metrics
```python
{
  "total_errors": 523,
  "error_rate": 0.052,  # 5.2%
  "errors_by_code": {
    "400": 200,
    "401": 150,
    "404": 100,
    "500": 50,
    "503": 23
  }
}
```

## Performance Monitoring

### Response Time Analysis

Understanding response time distribution:

```
Response Time Distribution:
0-100ms   : ████████████████████ 60%
100-200ms : ████████ 25%
200-500ms : ████ 10%
500-1000ms: ██ 4%
>1000ms   : ▌ 1%
```

### Slow Endpoint Detection

Identify endpoints that need optimization:

```python
slow_endpoints = [
    {
        "path": "/api/reports/generate",
        "avg_time": 3500,  # ms
        "calls": 100,
        "timeout_rate": 0.05
    },
    {
        "path": "/api/data/export",
        "avg_time": 2100,  # ms
        "calls": 50,
        "timeout_rate": 0.02
    }
]
```

### Database Performance

Monitor database query performance:

```python
{
  "total_queries": 50000,
  "avg_query_time": 15,  # ms
  "slow_queries": 23,
  "connection_pool": {
    "size": 20,
    "active": 12,
    "idle": 8,
    "waiting": 0
  }
}
```

## Health Checks

### Basic Health Check

Simple endpoint to verify service is running:

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0"
    }
```

### Detailed Health Check

Comprehensive health status including dependencies:

```python
@app.get("/health/detailed")
async def detailed_health():
    health_status = {
        "service": check_service_health(),
        "database": check_database_health(),
        "cache": check_cache_health(),
        "external_apis": check_external_apis(),
        "disk_space": check_disk_space(),
        "memory": check_memory_usage()
    }
    
    overall_status = "healthy"
    for component, status in health_status.items():
        if status["status"] != "healthy":
            overall_status = "unhealthy"
            break
    
    return {
        "status": overall_status,
        "components": health_status,
        "timestamp": datetime.utcnow()
    }
```

### Readiness vs Liveness

Understanding the difference:

#### Liveness Probe
Checks if the application is running:
```python
@app.get("/health/live")
async def liveness():
    # Basic check - is the app responsive?
    return {"status": "alive"}
```

#### Readiness Probe
Checks if the application is ready to serve traffic:
```python
@app.get("/health/ready")
async def readiness():
    # Can we handle requests?
    ready = (
        database_connected() and
        cache_available() and
        not under_maintenance()
    )
    
    if ready:
        return {"status": "ready"}
    else:
        return {"status": "not_ready"}, 503
```

## Logging and Tracing

### Structured Logging

Implement structured logging for better analysis:

```python
import structlog

logger = structlog.get_logger()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log request
    logger.info("request_started",
        method=request.method,
        path=request.url.path,
        client_ip=request.client.host
    )
    
    response = await call_next(request)
    
    # Log response
    duration = time.time() - start_time
    logger.info("request_completed",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=duration * 1000
    )
    
    return response
```

### Distributed Tracing

Track requests across multiple services:

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

@app.middleware("http")
async def trace_requests(request: Request, call_next):
    with tracer.start_as_current_span(
        f"{request.method} {request.url.path}"
    ) as span:
        span.set_attribute("http.method", request.method)
        span.set_attribute("http.url", str(request.url))
        
        response = await call_next(request)
        
        span.set_attribute("http.status_code", response.status_code)
        return response
```

### Log Aggregation

Centralize logs for analysis:

```python
# Configure log shipping to centralized system
LOGGING_CONFIG = {
    "version": 1,
    "handlers": {
        "elasticsearch": {
            "class": "elasticsearch_handler.ElasticsearchHandler",
            "hosts": ["localhost:9200"],
            "index": "fastapi-logs"
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": "/var/log/fastapi/app.log",
            "formatter": "json"
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["elasticsearch", "file"]
    }
}
```

## Alert Configuration

### Setting Up Alerts

Define alert rules for critical metrics:

```python
alert_rules = [
    {
        "name": "High Error Rate",
        "condition": "error_rate > 0.05",  # 5%
        "duration": "5m",
        "severity": "warning",
        "notification": ["email", "slack"]
    },
    {
        "name": "Low Disk Space",
        "condition": "disk_free < 10000",  # MB
        "duration": "1m",
        "severity": "critical",
        "notification": ["pagerduty"]
    },
    {
        "name": "High Response Time",
        "condition": "p95_response_time > 1000",  # ms
        "duration": "10m",
        "severity": "warning",
        "notification": ["email"]
    }
]
```

### Alert Channels

Configure notification channels:

#### Email Alerts
```python
email_config = {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "from_email": "alerts@yourapp.com",
    "to_emails": ["ops@yourapp.com", "dev@yourapp.com"]
}
```

#### Slack Alerts
```python
slack_config = {
    "webhook_url": "https://hooks.slack.com/services/...",
    "channel": "#alerts",
    "username": "FastAPI Monitor"
}
```

#### PagerDuty Integration
```python
pagerduty_config = {
    "integration_key": "your-integration-key",
    "severity_mapping": {
        "critical": "critical",
        "warning": "warning",
        "info": "info"
    }
}
```

## Custom Metrics

### Creating Custom Metrics

Track business-specific metrics:

```python
from prometheus_client import Counter, Histogram, Gauge

# Define metrics
request_count = Counter(
    'app_requests_total',
    'Total requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'app_request_duration_seconds',
    'Request duration',
    ['method', 'endpoint']
)

active_users = Gauge(
    'app_active_users',
    'Currently active users'
)

# Use in your application
@app.middleware("http")
async def track_metrics(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    # Update metrics
    request_count.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    request_duration.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(time.time() - start_time)
    
    return response
```

### Business Metrics

Track business KPIs:

```python
# Business metrics
orders_processed = Counter(
    'business_orders_total',
    'Total orders processed'
)

revenue = Counter(
    'business_revenue_total',
    'Total revenue in cents'
)

conversion_rate = Gauge(
    'business_conversion_rate',
    'Current conversion rate'
)

# Track in your business logic
@app.post("/api/orders")
async def create_order(order: Order):
    # Process order
    result = process_order(order)
    
    # Update metrics
    orders_processed.inc()
    revenue.inc(order.total_cents)
    
    return result
```

## Database Monitoring

### Query Performance

Monitor slow queries:

```python
from sqlalchemy import event

@event.listens_for(Engine, "before_execute")
def receive_before_execute(conn, clauseelement, multiparams, params, execution_options):
    conn.info.setdefault('query_start_time', []).append(time.time())

@event.listens_for(Engine, "after_execute")
def receive_after_execute(conn, clauseelement, multiparams, params, result, execution_options):
    start_time = conn.info['query_start_time'].pop()
    duration = time.time() - start_time
    
    if duration > 1.0:  # Log slow queries (>1 second)
        logger.warning("slow_query",
            query=str(clauseelement),
            duration_seconds=duration
        )
```

### Connection Pool Monitoring

Track database connection usage:

```python
from sqlalchemy.pool import Pool
from sqlalchemy import event

@event.listens_for(Pool, "connect")
def receive_connect(dbapi_conn, connection_record):
    connection_record.info['connect_time'] = time.time()

@event.listens_for(Pool, "checkout")
def receive_checkout(dbapi_conn, connection_record, connection_proxy):
    logger.info("connection_checkout",
        pool_size=connection_proxy._pool.size(),
        overflow=connection_proxy._pool.overflow(),
        total=connection_proxy._pool.size() + connection_proxy._pool.overflow()
    )
```

## Security Monitoring

### Authentication Attempts

Track authentication events:

```python
auth_attempts = Counter(
    'security_auth_attempts_total',
    'Authentication attempts',
    ['result', 'method']
)

failed_auth_ips = {}

@app.post("/auth/login")
async def login(credentials: LoginCredentials, request: Request):
    client_ip = request.client.host
    
    try:
        user = authenticate(credentials)
        auth_attempts.labels(result='success', method='password').inc()
        
        # Clear failed attempts for this IP
        failed_auth_ips.pop(client_ip, None)
        
        return {"token": create_token(user)}
    
    except AuthenticationError:
        auth_attempts.labels(result='failure', method='password').inc()
        
        # Track failed attempts
        failed_auth_ips[client_ip] = failed_auth_ips.get(client_ip, 0) + 1
        
        # Alert on suspicious activity
        if failed_auth_ips[client_ip] > 5:
            logger.warning("suspicious_auth_activity",
                ip=client_ip,
                attempts=failed_auth_ips[client_ip]
            )
        
        raise HTTPException(status_code=401)
```

### Rate Limiting Monitoring

Track rate limit violations:

```python
rate_limit_hits = Counter(
    'security_rate_limit_hits_total',
    'Rate limit violations',
    ['endpoint', 'ip']
)

@app.middleware("http")
async def monitor_rate_limits(request: Request, call_next):
    # Check rate limit
    if is_rate_limited(request):
        rate_limit_hits.labels(
            endpoint=request.url.path,
            ip=request.client.host
        ).inc()
        
        return JSONResponse(
            status_code=429,
            content={"error": "Rate limit exceeded"}
        )
    
    return await call_next(request)
```

## Dashboard Customization

### Creating Custom Dashboards

Extend the Admin UI with custom metrics:

```python
@app.get("/admin/custom-metrics")
async def custom_dashboard():
    return {
        "business_metrics": {
            "daily_active_users": get_dau(),
            "monthly_revenue": get_monthly_revenue(),
            "conversion_rate": get_conversion_rate(),
            "churn_rate": get_churn_rate()
        },
        "technical_metrics": {
            "cache_hit_rate": get_cache_hit_rate(),
            "queue_depth": get_queue_depth(),
            "worker_utilization": get_worker_utilization()
        }
    }
```

## Best Practices

### 1. Define SLIs and SLOs

Service Level Indicators and Objectives:

```python
slos = {
    "availability": {
        "target": 99.9,  # Three nines
        "window": "30d",
        "measurement": "uptime_percentage"
    },
    "latency": {
        "target": 200,  # milliseconds
        "percentile": 95,
        "window": "5m"
    },
    "error_rate": {
        "target": 1,  # percent
        "window": "5m"
    }
}
```

### 2. Use the Four Golden Signals

Monitor these key metrics:
- **Latency**: Response time of requests
- **Traffic**: Requests per second
- **Errors**: Rate of failed requests
- **Saturation**: Resource utilization

### 3. Implement Synthetic Monitoring

Proactively test your API:

```python
async def synthetic_check():
    """Run synthetic tests against production"""
    
    # Test critical user journey
    test_results = []
    
    # 1. Health check
    result = await test_endpoint("/health")
    test_results.append(result)
    
    # 2. Authentication
    result = await test_login()
    test_results.append(result)
    
    # 3. Core functionality
    result = await test_core_api()
    test_results.append(result)
    
    # Report results
    for result in test_results:
        if not result.success:
            alert("Synthetic test failed", result)
```

## Next Steps

- [Testing Guide](#docs/testing-guide) - Test your monitoring setup
- [API Endpoints](#docs/endpoints) - Monitor specific endpoints
- [Authentication](#docs/authentication) - Secure your monitoring data