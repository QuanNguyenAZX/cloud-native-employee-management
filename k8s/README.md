# Local Kubernetes Deployment

This directory contains a simple local Kubernetes setup for the employee management app.

## Architecture

The cluster runs everything inside the `employee-management` namespace:

- `employee-backend`: FastAPI API on port `8000`
- `employee-frontend`: Nginx static frontend on port `80`
- `postgres`: PostgreSQL database on port `5432`
- `minio`: S3-compatible object storage on port `9000`
- `employee-management-config`: non-sensitive configuration
- `employee-management-secret`: application and infrastructure secrets
- `employee-management`: Ingress for `http://employee.local`

Traffic flow:

`browser -> ingress -> frontend`

`browser -> ingress /api -> backend`

`backend -> postgres service DNS`

`backend -> minio service DNS`

## Namespace

All resources are created in:

`employee-management`

## Deployments

- Backend deployment runs the existing backend image strategy and starts FastAPI with the built-in prestart flow.
- Frontend deployment runs the existing nginx-based frontend image.
- PostgreSQL is a local single-replica deployment with a PVC.
- MinIO is a local single-replica deployment with a PVC.

## Services

- `employee-frontend` is exposed internally as `ClusterIP`
- `employee-backend` is exposed internally as `ClusterIP`
- `postgres` is internal only
- `minio` is internal only

## ConfigMap

`employee-management-config` holds:

- `PROJECT_NAME`
- `ENVIRONMENT`
- `FRONTEND_HOST`
- `BACKEND_CORS_ORIGINS`
- `POSTGRES_SERVER`
- `POSTGRES_PORT`
- `POSTGRES_DB`
- `OBJECT_STORAGE_ENDPOINT`
- `OBJECT_STORAGE_BUCKET`
- `OBJECT_STORAGE_REGION`
- `OBJECT_STORAGE_FORCE_PATH_STYLE`
- SMTP defaults

## Secret

`employee-management-secret` holds:

- `SECRET_KEY`
- `FIRST_SUPERUSER`
- `FIRST_SUPERUSER_PASSWORD`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `OBJECT_STORAGE_ACCESS_KEY`
- `OBJECT_STORAGE_SECRET_KEY`
- `MINIO_ROOT_USER`
- `MINIO_ROOT_PASSWORD`

## Persistent Storage

Two PVCs are created:

- `postgres-data`
- `minio-data`

If your local cluster supports dynamic provisioning, they should bind automatically.

## How to Deploy

### 1. Build images locally

```powershell
docker build -t employee-backend:local -f backend/Dockerfile .
docker build -t employee-frontend:local --build-arg VITE_API_URL=/api/v1 -f frontend/Dockerfile .
```

### 2. Apply Kubernetes manifests

```powershell
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/
```

## How to Verify

```powershell
kubectl get nodes
kubectl get pods -n employee-management
kubectl get svc -n employee-management
kubectl get ingress -n employee-management
kubectl get pvc -n employee-management
```

Check health:

```powershell
kubectl port-forward -n employee-management svc/employee-backend 8000:80
curl http://localhost:8000/api/v1/utils/health-check/
```

If you are using Ingress, add this to your hosts file:

```text
127.0.0.1 employee.local
```

Then open:

`http://employee.local`

## How to Delete

```powershell
kubectl delete -f k8s/
kubectl delete namespace employee-management
```

## Troubleshooting

```powershell
kubectl describe pod -n employee-management <pod-name>
kubectl logs -n employee-management deploy/employee-backend
kubectl logs -n employee-management deploy/employee-frontend
kubectl logs -n employee-management deploy/postgres
kubectl logs -n employee-management deploy/minio
kubectl describe ingress -n employee-management employee-management
kubectl get events -n employee-management --sort-by=.metadata.creationTimestamp
```

If the frontend loads but API calls fail, confirm:

- the frontend image was built with `VITE_API_URL=/api/v1`
- the ingress controller is running
- `employee.local` resolves to `127.0.0.1`
