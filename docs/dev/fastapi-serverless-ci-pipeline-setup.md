# FastAPI Serverless Project Setup Guide
*A complete guide to CI/CD repository configuration before writing application code*

## Why This Matters
Setting up proper infrastructure before writing application code is crucial for long-term project success. Each component in this guide addresses specific challenges that become exponentially harder to implement as the codebase grows. By establishing these foundations early, we create a robust development environment that supports quality, testing, and automated deployments from day one.

### Key Benefits
- Consistent development environment across team members
- Automated quality checks and deployments from the start
- Clear separation of development and production environments
- Built-in testing practices that scale with the code
- Infrastructure-as-code approach for reproducible deployments

## The CI/CD Pipeline
On the topic of good engineering and quality code, this is the pipeline and setup that we should have on each new repo before adding application code. 

This v1.0.0 approach ensures quality, maintainability, and proper CI/CD from day one.

- 1️⃣ Git repo 
- 2️⃣ FastAPI base app 
- 3️⃣ CI pipeline (dev and main) 
- 4️⃣ Unit, integration and QA tests 
- 5️⃣ 100% code coverage 
- 6️⃣ Auto-tagging on commits 
- 7️⃣ Create Docker container 
- 8️⃣ Push Docker container to AWS ECR 
- 9️⃣ Create AWS Lambda 
- 🔟 Enable AWS Function URL 
- 1️⃣1️⃣ Ensure AWS Lambda/FastAPI works

Adding these elements later when complexity has grown becomes exponentially more difficult. This guide provides step-by-step instructions to implement this foundation correctly from the start.

## 1. Repository Setup
Repository setup establishes the foundation for the entire development workflow. A well-structured repository ensures consistent development practices, clear code organization, and efficient collaboration. The directory structure follows separation of concerns principles and supports independent testing of each component.

### Initial Structure
```bash
mkdir my-fastapi-project
cd my-fastapi-project
git init

# Create core directories
mkdir -p {src,tests/{unit,integration,qa},deploy/{docker,lambdas},.github/workflows}

# Create essential files
touch README.md LICENSE pyproject.toml requirements-test.txt
touch .gitignore .env.example
```

### Base Configuration Files
Configuration files establish project dependencies, testing requirements, and build settings. Poetry provides reliable dependency management while maintaining reproducible environments. The test requirements ensure consistent quality checks across all environments.

**pyproject.toml**
```toml
[tool.poetry]
name        = "my_fastapi_project"
version     = "v0.0.1"
description = "FastAPI Serverless Project"
authors     = ["Your Name <your.email@domain.com>"]
license     = "Apache 2.0"
readme      = "README.md"

[tool.poetry.dependencies]
python           = "^3.11"
fastapi          = "*"
mangum           = "*"
httpx           = "*"
uvicorn         = "*"

[build-system]
requires      = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"
```

**requirements-test.txt**
```text
pytest
pytest-cov
coveralls
```

## 2. FastAPI Base Application
FastAPI applications require clear structure to support scalability and maintenance. This setup separates routes, utilities, and core application logic while maintaining AWS Lambda compatibility through Mangum. The structure supports independent testing of components and clear separation of concerns.

### Core Application Structure
```
src/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── routes/
│   │   ├── __init__.py
│   │   └── info.py
│   └── utils/
│       ├── __init__.py
│       └── version.py
└── handler.py
```

### Basic FastAPI Application (main.py)
The main application file serves as the entry point, combining route configuration with AWS Lambda integration. Mangum handles the translation between AWS Lambda events and FastAPI requests, ensuring seamless serverless operation while maintaining local development capabilities.

```python
from fastapi import FastAPI
from mangum import Mangum
from app.routes import info

app = FastAPI()
app.include_router(info.router, prefix="/info", tags=["info"])

# Lambda handler
handler = Mangum(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Info Routes (routes/info.py)
Route modules provide clear API endpoint organization. The info routes offer essential system health checks and version information, crucial for monitoring and deployment verification. This structure supports easy addition of new endpoints while maintaining code organization.

```python
from fastapi import APIRouter
from app.utils.version import get_version

router = APIRouter()

@router.get("/version")
async def version():
    return {"version": get_version()}

@router.get("/ping")
async def ping():
    return "pong"
```

## 3. CI Pipeline Setup
Continuous Integration ensures code quality and automated deployments. The dual pipeline approach (dev/main) enables feature development while maintaining stable production code. Automated versioning and testing prevent broken deployments and maintain consistent release practices.

### GitHub Actions Workflows

**.github/workflows/ci-pipeline-dev.yml**
```yaml
name: CI Pipeline - DEV
on:
  push:
    branches:
      - dev

env:
  RELEASE_TYPE: 'minor'
  
jobs:
  run-tests:
    name: "Run tests"
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements-test.txt
      - name: Run tests
        run: pytest tests/ --cov=src/

  increment-tag:
    needs: run-tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Increment version
        run: |
          # Version increment logic here
          git tag v0.1.0
          git push origin --tags
```

**.github/workflows/ci-pipeline-main.yml**
```yaml
name: CI Pipeline - MAIN
on:
  push:
    branches:
      - main

env:
  RELEASE_TYPE: 'major'
  
jobs:
  # Similar to dev pipeline but with additional deployment steps
  deploy-to-aws:
    needs: [run-tests, increment-tag]
    runs-on: ubuntu-latest
    steps:
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v1
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ secrets.AWS_REGION }}
```

## 4. Testing Framework
Multi-layer testing catches issues at different stages of development. Unit tests verify component behavior, integration tests ensure proper system interaction, and QA tests validate production deployment. 100% coverage ensures no untested code paths exist.

### Unit Tests (tests/unit/test_version.py)
```python
from unittest import TestCase
from app.utils.version import get_version

class TestVersion(TestCase):
    def test_get_version(self):
        version = get_version()
        assert isinstance(version, str)
        assert version.startswith('v')
```

### Integration Tests (tests/integration/test_routes.py)
Integration tests validate the complete request-response cycle using FastAPI's test client. These tests ensure proper routing, middleware functionality, and response formatting. They catch issues that unit tests might miss while verifying the entire API behavior.

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_version_endpoint():
    response = client.get("/info/version")
    assert response.status_code == 200
    assert "version" in response.json()

def test_ping_endpoint():
    response = client.get("/info/ping")
    assert response.status_code == 200
    assert response.json() == "pong"
```

### QA Tests (tests/qa/test_lambda.py)
QA tests validate the deployed Lambda function through its public URL. These tests verify the complete deployment pipeline, including AWS configuration, networking, and Lambda execution environment. They serve as the final quality gate before production traffic.

```python
import pytest
import requests
from unittest import TestCase

class TestLambdaEndpoints(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lambda_url = "your-lambda-url"
        
    def test_version_endpoint_live(self):
        response = requests.get(f"{self.lambda_url}/info/version")
        assert response.status_code == 200
        assert "version" in response.json()
```

## 5. Docker Configuration
Docker containers ensure consistent environments across development and production. The configuration includes AWS Lambda compatibility layers and optimized Python settings. Multi-stage builds and proper base images maintain small deployment sizes while supporting development needs.

### Dockerfile
```dockerfile
FROM python:3.11-slim

RUN pip install mangum uvicorn fastapi

COPY --from=public.ecr.aws/awsguru/aws-lambda-adapter:0.8.4 \
     /lambda-adapter /opt/extensions/lambda-adapter

WORKDIR /app
COPY ./src /app/src
ENV PYTHONPATH="/app"
ENV PORT=8080

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### docker-compose.yml
Docker Compose facilitates local development by matching production container configurations. It provides volume mounting for live code updates and port mapping for local access. This setup ensures development closely matches production behavior while maintaining developer productivity.

```yaml
services:
  app:
    build:
      context: .
      dockerfile: deploy/docker/Dockerfile
    ports:
      - "8080:8080"
    volumes:
      - ./src:/app/src
```

## 6. AWS Lambda Deployment
Serverless deployment reduces operational overhead and provides automatic scaling. The Lambda setup includes proper memory allocation, timeout configurations, and URL endpoints. Infrastructure-as-code ensures reproducible deployments and proper version tracking.

### Lambda Function Setup
```python
from typing import Dict
from aws_cdk import (
    aws_lambda as _lambda,
    aws_ecr as ecr,
    core
)

class LambdaStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
        # Create Lambda function
        function = _lambda.DockerImageFunction(
            self, 'FastAPIFunction',
            code=_lambda.DockerImageCode.from_ecr(
                repository=ecr.Repository.from_repository_name(
                    self, 'ECRRepo',
                    repository_name='your-repo-name'
                )
            ),
            memory_size=1024,
            timeout=core.Duration.seconds(30),
        )
        
        # Add function URL
        function.add_function_url(
            auth_type=_lambda.FunctionUrlAuthType.NONE
        )
```

## 7. Validation Steps
Comprehensive validation prevents deployment issues and ensures system health. The steps cover local development, container verification, and production deployment checks. Automated validation in CI/CD pipelines prevents manual errors and maintains deployment quality.

### Local Testing
```bash
# Start local server
uvicorn src.main:app --reload

# Run test suite
pytest tests/ --cov=src/

# Build and run Docker container
docker-compose up --build
```

### AWS Deployment Validation
Deployment validation ensures the entire pipeline functions correctly. These commands verify ECR push permissions, container registry access, and Lambda URL functionality. Regular validation prevents deployment-related downtimes and ensures system reliability.

```bash
# Push to ECR
aws ecr get-login-password --region region | docker login --username AWS --password-stdin aws_account_id.dkr.ecr.region.amazonaws.com
docker push aws_account_id.dkr.ecr.region.amazonaws.com/your-repo:latest

# Test Lambda URL
curl https://your-lambda-url/info/version
```

## Best Practices
These practices form the foundation of professional development workflows. Each category addresses specific challenges in modern software development, ensuring code quality, team collaboration, and system reliability.

1. **Version Control**
   - Use semantic versioning
   - Maintain clean git history
   - Protect main branch
   - Require PR reviews

2. **Testing**
   - Maintain 100% code coverage
   - Implement all test types from start
   - Use fixtures for test data
   - Mock external services

3. **CI/CD**
   - Automate all deployments
   - Include security scans
   - Test in multiple Python versions
   - Maintain deployment history

4. **Documentation**
   - Keep README updated
   - Document all endpoints
   - Include setup instructions
   - Document deployment process

Remember: This foundation guarantees maintainable, scalable applications. Invest time in setting it up correctly before writing application code.
