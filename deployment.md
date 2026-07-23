# Deployment

This project can be deployed to Render, Railway, or Fly.io.

## Shared requirements

Set these environment variables in the hosting provider:

- ENVIRONMENT=production
- SECRET_KEY=<strong-random-value>
- POSTGRES_SERVER=<host>
- POSTGRES_PORT=5432
- POSTGRES_USER=<user>
- POSTGRES_PASSWORD=<password>
- POSTGRES_DB=<database>
- FIRST_SUPERUSER=<admin@example.com>
- FIRST_SUPERUSER_PASSWORD=<password>
- BACKEND_CORS_ORIGINS=https://<frontend-url>

## Render

1. Create a PostgreSQL database.
2. Deploy the backend as a Docker service using [backend/Dockerfile](backend/Dockerfile).
3. Deploy the frontend as a Docker service using [frontend/Dockerfile](frontend/Dockerfile).
4. Set the environment variables above.
5. Use the frontend URL as the public link for recruiters.

## Railway

1. Create a new Railway project.
2. Add a PostgreSQL service.
3. Deploy the backend and frontend from the repository using their Dockerfiles.
4. Connect the services with the environment variables above.

## Fly.io

1. Create separate apps for the backend and frontend.
2. Deploy each app with the matching Dockerfile.
3. Configure the same environment variables.
4. Use the frontend public URL as the final recruiter-facing link.

To make sure it runs on startup and continues running, you can install it as a service. To do that, exit the `github` user and go back to the `root` user:

```bash
exit
```

After you do it, you will be on the previous user again. And you will be on the previous directory, belonging to that user.

Before being able to go the `github` user directory, you need to become the `root` user (you might already be):

```bash
sudo su
```

* As the `root` user, go to the `actions-runner` directory inside of the `github` user's home directory:

```bash
cd /home/github/actions-runner
```

* Install the self-hosted runner as a service with the user `github`:

```bash
./svc.sh install github
```

* Start the service:

```bash
./svc.sh start
```

* Check the status of the service:

```bash
./svc.sh status
```

You can read more about it in the official guide: [Configuring the self-hosted runner application as a service](https://docs.github.com/en/actions/hosting-your-own-runners/managing-self-hosted-runners/configuring-the-self-hosted-runner-application-as-a-service).

### Configure GitHub Environments

The deployment workflows use [GitHub Environments](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments) for `staging` and `production`. This enables environment-specific secrets, deployment protection rules (e.g. required reviewers, wait timers), and deployment status tracking.

To configure them, go to your repository's **Settings** > **Environments** and create the `staging` and `production` environments.

### Set Secrets

For each GitHub Environment (`staging` and `production`), configure the required secrets as [environment secrets](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets#creating-secrets-for-an-environment). Environment secrets are preferred over [repository secrets](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets#creating-secrets-for-a-repository) because they are scoped to the specific environment, reducing exposure and aligning with any protection rules you configure.

The current Github Actions workflows expect these secrets:

* `DOMAIN_PRODUCTION`
* `DOMAIN_STAGING`
* `STACK_NAME_PRODUCTION`
* `STACK_NAME_STAGING`
* `EMAILS_FROM_EMAIL`
* `FIRST_SUPERUSER`
* `FIRST_SUPERUSER_PASSWORD`
* `POSTGRES_PASSWORD`
* `SECRET_KEY`
* `LATEST_CHANGES`
* `SMOKESHOW_AUTH_KEY`

## GitHub Action Deployment Workflows

There are GitHub Action workflows in the `.github/workflows` directory already configured for deploying to the environments (GitHub Actions runners with the labels):

* `staging`: after pushing (or merging) to the branch `master`.
* `production`: after publishing a release.

Both workflows are associated with their respective GitHub Environments, so deployments will be visible in the repository's **Environments** section and will respect any protection rules you configure.

If you need to add extra environments you could use those as a starting point.

## URLs

Replace `fastapi-project.example.com` with your domain.

### Main Traefik Dashboard

Traefik UI: `https://traefik.fastapi-project.example.com`

### Production

Frontend: `https://dashboard.fastapi-project.example.com`

Backend API docs: `https://api.fastapi-project.example.com/docs`

Backend API base URL: `https://api.fastapi-project.example.com`

Adminer: `https://adminer.fastapi-project.example.com`

### Staging

Frontend: `https://dashboard.staging.fastapi-project.example.com`

Backend API docs: `https://api.staging.fastapi-project.example.com/docs`

Backend API base URL: `https://api.staging.fastapi-project.example.com`

Adminer: `https://adminer.staging.fastapi-project.example.com`
