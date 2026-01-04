# Kube API Host Project

A FastAPI application deployed on Kubernetes that serves static HTML files. This project provides a simple web service to fetch and serve HTML content stored in the container.

## Project Overview

This application:
- Runs a FastAPI server that serves static HTML files
- Exposes a `/fetch/{page_name}` endpoint to retrieve HTML files
- Can be deployed locally or on a Kubernetes cluster
- Supports multiple deployment configurations (NodePort, LoadBalancer, Ingress)

## Prerequisites

Before deploying this application, ensure you have the following installed:

- **Docker** (v20.10+) - For building and running container images
- **kubectl** (v1.21+) - For managing Kubernetes resources
- **minikube** (v1.25+) - For running local Kubernetes cluster (optional)
- **Python 3.9+** - For local development (optional)

### Verify Installation

```bash
docker --version
kubectl version --client
minikube version
python --version
```

## Project Structure

```
.
├── main.py                     # FastAPI application entry point
├── Dockerfile                  # Docker image definition
├── README.md                   # This file
├── html_files/                 # Static HTML files to serve
│   └── sample.html             # Sample HTML page
└── kubectl_deployment/         # Kubernetes manifests
    ├── deployment.yaml         # Deployment configuration
    ├── service.yaml            # LoadBalancer service
    ├── nodeport-service.yaml   # NodePort service (alternative)
    ├── ingress.yaml            # Ingress configuration
    └── namespace.yaml          # Namespace definition
```

## Local Development

To run the application locally with hot reload:

```bash
# Install dependencies
pip install fastapi uvicorn requests

# Run the application
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Access the application at `http://localhost:8000/fetch/sample.html`

## Docker Deployment

### Build Docker Image

```bash
docker build -t serp-fetcher-fastapi:v1.0.0 . -f Dockerfile
```

### Run Container Locally

```bash
docker run -p 8000:8000 serp-fetcher-fastapi:v1.0.0
```

Access the application at `http://localhost:8000/fetch/sample.html`

## Kubernetes Deployment

### Create Namespace

```bash
kubectl create namespace jg-workers
kubectl apply -f kubectl_deployment/namespace.yaml
```

### Deploy Application

```bash
kubectl apply -f kubectl_deployment/deployment.yaml -n jg-workers
kubectl apply -f kubectl_deployment/service.yaml -n jg-workers
```

### Verify Deployment

```bash
kubectl get services -n jg-workers
kubectl get all -n jg-workers
kubectl config set-context --current --namespace=jg-workers
```

### Configure Ingress (Optional)

If using minikube or a cluster with ingress support:

```bash
minikube addons enable ingress
kubectl apply -f kubectl_deployment/ingress.yaml -n jg-workers
kubectl get ingress -n jg-workers
```

## Accessing the Application

Once deployed, access the application using one of the following methods:

### Via LoadBalancer Service
```bash
kubectl get services -n jg-workers
# Get the EXTERNAL-IP from the service output
curl http://<EXTERNAL-IP>/fetch/sample.html
```

### Via NodePort Service (if using nodeport-service.yaml)
```bash
kubectl get services -n jg-workers
# Get the NODEPORT from the service output
curl http://<NODE-IP>:<NODEPORT>/fetch/sample.html
```

### Via Ingress (if configured)
```bash
kubectl get ingress -n jg-workers
# Use the ingress address provided
http://<EXTERNAL-IP>/fetch/sample.html
```

## API Endpoints

### GET /fetch/{page_name}
Fetches and returns an HTML file from the `html_files` directory.

**Parameters:**
- `page_name` (path parameter): Name of the HTML file to fetch

**Example:**
```bash
curl http://localhost:8000/fetch/sample.html
```

**Response:**
- Status 200: HTML content
- Status 404: Page not found

## Configuration

### Environment-Specific Settings

The application can be configured by modifying constants in `main.py`:

```python
# Change HTML file location
HTML_DIRECTORY = Path("/app/html_files")  # Production
# HTML_DIRECTORY = Path("html_files")    # Local development

# Uncomment to use remote server instead of local files
# REMOTE_SERVER = "http://<YOUR-SERVER-IP>:8080"
```

### Kubernetes Configuration

Key settings in `deployment.yaml`:
- **Replicas**: Number of pod instances (default: 1)
- **Image**: Docker image name and tag (serp-fetcher-fastapi:v1.0.0)
- **Port**: Container port (8000)

Key settings in `service.yaml`:
- **Type**: LoadBalancer (external access) or ClusterIP (internal)
- **Port**: Service port (80)
- **TargetPort**: Container port (8000)

## Troubleshooting

### Container Won't Start

```bash
# Check pod status
kubectl get pods -n jg-workers

# View pod logs
kubectl logs <pod-name> -n jg-workers

# Describe pod for detailed information
kubectl describe pod <pod-name> -n jg-workers
```

### Service Not Accessible

```bash
# Check service endpoints
kubectl get endpoints -n jg-workers

# Verify service is running
kubectl get svc -n jg-workers

# Check if pods are ready
kubectl get pods -n jg-workers
```

### Ingress Not Working

```bash
# Check ingress status
kubectl get ingress -n jg-workers

# View ingress controller logs
kubectl logs -n ingress-nginx <ingress-controller-pod>

# Test DNS resolution
kubectl run -it --rm debug --image=busybox --restart=Never -- wget -O- http://serp-fetcher-fastapi-service
```

### File Not Found Errors

- Ensure HTML files exist in the `html_files` directory
- Verify `HTML_DIRECTORY` path in `main.py` is correct
- Check file permissions on the host system

### Build Issues

```bash
# Clean up old images
docker system prune -a

# Rebuild with no cache
docker build --no-cache -t serp-fetcher-fastapi:v1.0.0 . -f Dockerfile
```

## Testing

### Manual Testing

```bash
# Test with curl
curl http://localhost:8000/fetch/sample.html

# Test non-existent file (should return 404)
curl http://localhost:8000/fetch/nonexistent.html

# Test with minikube
minikube service serp-fetcher-fastapi-service -n jg-workers
```

### Automated Testing

To add automated tests, create a `tests/` directory with pytest test files:

```python
# tests/test_main.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_fetch_html_success():
    response = client.get("/fetch/sample.html")
    assert response.status_code == 200

def test_fetch_html_not_found():
    response = client.get("/fetch/nonexistent.html")
    assert response.status_code == 404
```

Run tests with:
```bash
pytest tests/
```

## Maintenance

### Updating the Application

1. Modify code in `main.py` or update HTML files
2. Rebuild Docker image with new version tag
3. Update image tag in `deployment.yaml`
4. Apply updated deployment

```bash
docker build -t serp-fetcher-fastapi:v1.0.1 . -f Dockerfile
# Update image tag in deployment.yaml to v1.0.1
kubectl apply -f kubectl_deployment/deployment.yaml -n jg-workers
kubectl rollout restart deployment/serp-fetcher-fastapi -n jg-workers
```

### Cleanup

Remove all Kubernetes resources:

```bash
kubectl delete -f kubectl_deployment/ -n jg-workers
kubectl delete namespace jg-workers
```

Remove Docker images:

```bash
docker rmi serp-fetcher-fastapi:v1.0.0
```

## Contributing

Contributions are welcome! Please ensure:
- Code follows project conventions (see AGENTS.md)
- All tests pass
- Docker image builds successfully
- Kubernetes deployment works as expected

## 📄 License

This project is a open source project and is available under the [MIT License](LICENSE).

## 👨‍💻 Author

**Jogesh Kumar Ghadai**
- Email: jogesh6895@gmail.com
- GitHub: [@Jogesh6895](https://github.com/Jogesh6895)

---
