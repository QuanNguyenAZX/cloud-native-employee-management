# MVP Starter

This project is trimmed down to the core features you want to build and keep:

- CRUD
- Authentication
- Refresh token
- RBAC
- Dashboard
- Search
- Pagination
- Sort
- Filter
- Validation
- MinIO
- Audit log

## Quick start

1. Copy the environment file and update secrets:

```bash
cp .env.example .env
```

2. Start the stack with Docker Compose:

```bash
docker compose up -d --build
```

3. Open the app:

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API docs: http://localhost:8000/docs

## Required environment variables

At minimum, set these values in your environment before running the app:

- SECRET_KEY
- POSTGRES_PASSWORD
- FIRST_SUPERUSER
- FIRST_SUPERUSER_PASSWORD

## Main folders

- backend/: FastAPI application
- frontend/: React + TypeScript dashboard
- compose.yml: production-style Docker Compose setup
- deployment.md: deployment notes for Render, Railway, and Fly.io
