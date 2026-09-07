param(
  [string]$BackendImage = "employee-backend:local",
  [string]$FrontendImage = "employee-frontend:local",
  [string]$FrontendApiBaseUrl = "/api/v1"
)

$ErrorActionPreference = "Stop"

docker build -t $BackendImage -f backend/Dockerfile .
docker build -t $FrontendImage --build-arg VITE_API_URL=$FrontendApiBaseUrl -f frontend/Dockerfile .

kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/
