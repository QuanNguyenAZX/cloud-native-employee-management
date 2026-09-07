# Employee Management Helm Chart

This chart is configured for a local Docker Desktop Kubernetes cluster.

## Local images

The backend and frontend use images that already exist in the local Docker image store:

- `backend:latest`
- `frontend:latest`

Both workloads use `imagePullPolicy: IfNotPresent`, so Kubernetes uses the local images and does not require Docker Hub or another registry.

PostgreSQL and MinIO remain configurable independently in `values.yaml`.

## Rebuild local images

From the repository root:

```powershell
docker build -t backend:latest .\backend
docker build --build-arg VITE_API_URL=/api/v1 -t frontend:latest .\frontend
```

If Docker Desktop Kubernetes is enabled, the images are available to the local cluster without pushing them to a registry.

## Deploy or upgrade

```powershell
helm upgrade --install employee-management .\helm\employee-management `
  --namespace employee-management `
  --create-namespace `
  -f .\helm\employee-management\values-dev.yaml
```

Check the rollout with:

```powershell
kubectl get pods -n employee-management
kubectl get deployments -n employee-management
kubectl get svc -n employee-management
kubectl get ingress -n employee-management
```
