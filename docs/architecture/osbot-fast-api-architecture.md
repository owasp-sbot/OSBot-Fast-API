# OSBot-Fast-API Architecture

## 📋 Overview

**Module**: `osbot_fast_api`  
**Purpose**: Type-Safe FastAPI wrapper with enhanced middleware and monitoring capabilities  
**Status**: Production Ready

## 🏗️ System Architecture

```mermaid
graph TB
    subgraph "External Layer"
        CLIENT[HTTP Client]
        LAMBDA[AWS Lambda]
        LOCAL[Local Server]
    end
    
    subgraph "OSBot-Fast-API Core"
        FA[Fast_API<br/>Main Controller]
        
        subgraph "Middleware Pipeline"
            MW1[Detect_Disconnect]
            MW2[Http_Request]
            MW3[CORS]
            MW4[API_Key_Check]
            MW1 --> MW2 --> MW3 --> MW4
        end
        
        subgraph "Type System"
            TS[Type_Safe Converters]
            TSB[To_BaseModel]
            BTS[From_BaseModel]
            TSD[To_Dataclass]
            DTS[From_Dataclass]
        end
        
        subgraph "Event System"
            HE[Http_Events Manager]
            HEI[Event Info]
            HEQ[Request Data]
            HER[Response Data]
            HET[Trace Data]
        end
        
        subgraph "Routing"
            FAR[Fast_API_Routes]
            RC[Route Config]
            RM[Route Methods]
        end
    end
    
    subgraph "FastAPI Layer"
        APP[FastAPI App]
        ROUTER[API Router]
        HANDLERS[Route Handlers]
    end
    
    CLIENT --> FA
    LAMBDA --> FA
    LOCAL --> FA
    
    FA --> MW1
    FA --> TS
    FA --> HE
    FA --> FAR
    
    FAR --> APP
    APP --> ROUTER
    ROUTER --> HANDLERS
    
    HE --> HEI
    HE --> HEQ
    HE --> HER
    HE --> HET
    
    TS --> TSB
    TS --> BTS
    TS --> TSD
    TS --> DTS
```

## 🔄 Request Lifecycle

```mermaid
sequenceDiagram
    participant C as Client
    participant MW as Middleware Stack
    participant TS as Type Converter
    participant H as Handler
    participant E as Event System
    
    C->>MW: HTTP Request
    MW->>MW: Detect_Disconnect check
    MW->>E: Create Http_Event
    E->>E: Capture request data
    MW->>MW: API Key validation
    MW->>TS: Convert BaseModel to Type_Safe
    TS->>H: Call handler with Type_Safe
    H->>H: Process request
    H->>TS: Return Type_Safe response
    TS->>MW: Convert to BaseModel
    MW->>E: Capture response data
    E->>E: Store event (max 50)
    MW->>C: HTTP Response
```

## 🧩 Core Components

### Fast_API Class

The main controller that orchestrates all components:

```mermaid
classDiagram
    class Fast_API {
        +str base_path
        +bool enable_cors
        +bool enable_api_key
        +bool default_routes
        +Fast_API__Http_Events http_events
        +Random_Guid server_id
        
        +setup()
        +add_route_get(function)
        +add_route_post(function)
        +add_routes(class_routes)
        +setup_middlewares()
        +app()
        +routes()
        +client()
    }
    
    Fast_API --|> Type_Safe
    Fast_API *-- Fast_API__Http_Events
    Fast_API ..> FastAPI : creates
    Fast_API ..> Fast_API_Routes : manages
```

**Responsibilities**:
- FastAPI application lifecycle
- Middleware chain configuration
- Route registration and management
- HTTP event coordination
- Global exception handling

### Fast_API_Routes Class

Base class for organizing routes with automatic Type-Safe conversion:

```mermaid
classDiagram
    class Fast_API_Routes {
        +APIRouter router
        +FastAPI app
        +str prefix
        +str tag
        
        +add_route(function, methods)
        +add_route_with_body(function, methods)
        +add_route_get(function)
        +add_route_post(function)
        +parse_function_name(function_name)
        +setup_routes()
    }
    
    Fast_API_Routes --|> Type_Safe
    Fast_API_Routes --> APIRouter
    Fast_API_Routes --> FastAPI
```

**Route Path Generation Algorithm**:
```python
# Function name to path conversion
an_post()           → /an-post
get_user()          → /get-user
users__id()         → /users/{id}
users__id_profile() → /users/{id}/profile
```

### HTTP Events System

Comprehensive request/response tracking:

```mermaid
graph LR
    subgraph "Http Event"
        EVENT[Fast_API__Http_Event]
        EVENT --> INFO[Event Info<br/>- timestamp<br/>- client IP<br/>- thread ID]
        EVENT --> REQ[Request<br/>- method<br/>- path<br/>- headers<br/>- duration]
        EVENT --> RESP[Response<br/>- status<br/>- headers<br/>- content type]
        EVENT --> TRACE[Traces<br/>- call stack<br/>- execution path]
    end
```

**Event Storage**:
- Circular buffer (deque) with max 50 events
- FIFO eviction policy
- Automatic sensitive data cleaning

## 🔐 Middleware Architecture

### Middleware Pipeline

```mermaid
graph TD
    REQ[Incoming Request]
    
    subgraph "Middleware Stack"
        MD[Detect_Disconnect<br/>Monitor client connection]
        MH[Http_Request<br/>Event tracking]
        MC[CORS<br/>Cross-origin headers]
        MA[API_Key_Check<br/>Authentication]
        
        MD --> MH
        MH --> MC
        MC --> MA
    end
    
    HANDLER[Route Handler]
    RESP[Response]
    
    REQ --> MD
    MA --> HANDLER
    HANDLER --> RESP
```

### Middleware Responsibilities

| Middleware | Purpose | Configuration |
|------------|---------|---------------|
| `Detect_Disconnect` | Monitor client disconnections | Always enabled |
| `Http_Request` | Track HTTP events | Always enabled |
| `CORS` | Handle cross-origin requests | `enable_cors=True` |
| `API_Key_Check` | Validate API keys | `enable_api_key=True` |

## 🔄 Type Conversion System

### Conversion Matrix

```mermaid
graph TD
    TS[Type_Safe Class]
    BM[BaseModel]
    DC[Dataclass]
    
    TS -->|Type_Safe__To__BaseModel| BM
    BM -->|BaseModel__To__Type_Safe| TS
    TS -->|Type_Safe__To__Dataclass| DC
    DC -->|Dataclass__To__Type_Safe| TS
    BM -->|BaseModel__To__Dataclass| DC
    DC -->|Dataclass__To__BaseModel| BM
```

### Conversion Process

```mermaid
sequenceDiagram
    participant API as FastAPI
    participant Conv as Converter
    participant Cache as Model Cache
    participant Handler as Route Handler
    
    API->>Conv: Request with JSON
    Conv->>Cache: Check for cached model
    
    alt Model Cached
        Cache-->>Conv: Return cached BaseModel class
    else Model Not Cached
        Conv->>Conv: Generate BaseModel class
        Conv->>Cache: Store in cache
    end
    
    Conv->>Conv: Instantiate with data
    Conv->>Handler: Type_Safe instance
    Handler->>Conv: Type_Safe response
    Conv->>API: BaseModel response
```

## 📊 Performance Characteristics

### Operation Complexity

| Operation | Time | Space | Notes |
|-----------|------|-------|-------|
| Route registration | O(1) | O(1) | Direct dictionary insertion |
| Type conversion (cached) | O(1) | O(1) | Cache lookup |
| Type conversion (new) | O(n) | O(n) | n = number of fields |
| Event tracking | O(1) | O(1) | Deque operations |
| Middleware chain | O(m) | O(1) | m = number of middleware |

### Memory Management

- **Model Cache**: Singleton pattern, shared across instances
- **Event Buffer**: Maximum 50 events, ~10KB per event
- **Route Registry**: Lazy loading, minimal overhead

## 🛡️ Security Architecture

### API Key Validation

```mermaid
sequenceDiagram
    participant Client
    participant Middleware
    participant Env
    
    Client->>Middleware: Request with API key
    Middleware->>Env: Get expected key
    
    alt Header contains key
        Middleware->>Middleware: Validate header
    else Cookie contains key
        Middleware->>Middleware: Validate cookie
    else No key found
        Middleware-->>Client: 401 Unauthorized
    end
    
    alt Key valid
        Middleware->>Handler: Continue
    else Key invalid
        Middleware-->>Client: 401 Unauthorized
    end
```

### Data Sanitization

- Automatic cookie removal from logged headers
- Auth header masking in events
- Stack trace prevention in production

## 🔧 Extension Points

### Custom Middleware

```python
class Custom_Fast_API(Fast_API):
    def setup_middlewares(self):
        super().setup_middlewares()
        # Add custom middleware here
        self.app().add_middleware(CustomMiddleware)
```

### Custom Routes

```python
class Custom_Routes(Fast_API_Routes):
    def setup_routes(self):
        # Add routes with Type-Safe support
        self.add_route_get(self.custom_method)
```

### Event Callbacks

```python
fast_api.http_events.callback_on_request = handle_request
fast_api.http_events.callback_on_response = handle_response
```

## 🚀 Deployment Patterns

### Local Development

```
Fast_API → Uvicorn → Local Server
```

### AWS Lambda

```
Fast_API → Mangum → Lambda Handler → API Gateway
```

### Docker Container

```
Fast_API → Uvicorn → Docker → Container Service
```

## 📈 Scalability Considerations

- **Stateless Design**: No shared state between requests
- **Cache Efficiency**: Model caching reduces CPU overhead
- **Event Buffer**: Fixed memory footprint
- **Middleware Performance**: O(1) operations per middleware

## 🔍 Monitoring & Observability

Built-in monitoring through:
- Request correlation IDs
- Execution traces
- Duration measurements
- Thread tracking
- Event history