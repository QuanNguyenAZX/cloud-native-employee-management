$ErrorActionPreference = "Stop"

kubectl delete -f k8s/ --ignore-not-found=true
kubectl delete namespace employee-management --ignore-not-found=true
