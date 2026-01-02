# AGENTS.md - Agent Instructions for Kube_API_Host_Project

This repository contains a FastAPI application deployed on Kubernetes that serves static HTML files.

## Build and Development Commands

```bash
# Build Docker
docker build -t serp-fetcher-fastapi:v1.0.0 . -f Dockerfile
docker run -p 8000:8000 serp-fetcher-fastapi:v1.0.0

# Run locally with hot reload
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Kubernetes deployment
kubectl apply -f kubectl_deployment/namespace.yaml -n jg-workers
kubectl apply -f kubectl_deployment/deployment.yaml -n jg-workers
kubectl apply -f kubectl_deployment/service.yaml -n jg-workers
kubectl get all -n jg-workers

# Testing (pytest recommended)
pytest                                    # All tests
pytest tests/test_main.py                 # Single file
pytest tests/test_main.py::test_fetch_html  # Specific test
pytest --cov=.

# Linting and type checking (recommended)
pip install black ruff mypy pytest pytest-cov
black .
ruff check .
mypy main.py
```

## Code Style Guidelines

### Import Ordering
Standard library → Third-party → Local (blank lines between groups)
```python
from pathlib import Path
import os

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
```

### Naming Conventions
- Variables/functions: `snake_case` (e.g., `fetch_html`)
- Constants: `UPPER_CASE` (e.g., `HTML_DIRECTORY`)
- Classes: `PascalCase`
- Files: `snake_case.py`

### Type Hints
Always include type hints:
```python
def fetch_html(page_name: str) -> HTMLResponse:
    file_path: Path = HTML_DIRECTORY / page_name
```

### Error Handling
- Use `HTTPException` with appropriate status codes
- Include descriptive error messages in `detail` parameter
- Wrap external calls in try-except blocks

```python
try:
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Page not found")
    return HTMLResponse(content=content, status_code=200)
except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
```

### File Operations
- Use `pathlib.Path` instead of `os.path`
- Specify encoding explicitly (prefer `utf-8`)

```python
HTML_DIRECTORY = Path("/app/html_files")
file_path = HTML_DIRECTORY / page_name
content = file_path.read_text(encoding="utf-8")
```

### API Design
- Use descriptive, lowercase path parameters with underscores
- Return FastAPI response types (`HTMLResponse`, `JSONResponse`)
- Constants at module level, not in functions
- Add triple-quoted docstrings at module level

## Project Structure
```
main.py              # FastAPI app entry point
Dockerfile           # Docker image definition
README.md            # Deployment instructions
html_files/          # Static HTML files to serve
kubectl_deployment/  # Kubernetes manifests
```

## Docker Guidelines
- Use official Python images with explicit versions (`python:3.9`)
- Set `WORKDIR` explicitly
- Minimize image layers
- Expose port 8000
- Use non-root users in production (not yet implemented)

## Kubernetes Guidelines
- Use consistent naming (`serp-fetcher-fastapi`)
- Define and use namespaces (`jg-workers`)
- Use labels/selectors for resource association
- Use LoadBalancer for external access, ClusterIP for internal

## Testing Guidelines
- Write pytest tests for all endpoints
- Test success and error paths
- Mock external dependencies
- Use descriptive names: `test_<function>_<scenario>`

```python
def test_fetch_html_success():
    response = client.get("/fetch/sample.html")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/html; charset=utf-8"

def test_fetch_html_not_found():
    response = client.get("/fetch/nonexistent.html")
    assert response.status_code == 404
```

## Versioning
- Use semantic versioning for Docker images (e.g., `v1.0.0`)
- Update image tags in deployment.yaml when releasing new versions
- Tag commit messages with version numbers for traceability
