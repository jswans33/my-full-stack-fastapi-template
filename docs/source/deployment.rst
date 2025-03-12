Deployment Guide
================

This guide covers the deployment process for the FastAPI Full Stack Template.

Prerequisites
-------------

* Docker and Docker Compose
* Domain name (for production)
* SSL certificate (Let's Encrypt recommended)
* PostgreSQL database
* SMTP server for emails

Environment Setup
-----------------

1. Create production environment file:

   .. code-block:: bash

      cp .env.example .env.prod

2. Update production variables:

   .. code-block:: text

      # Domain
      DOMAIN=your-domain.com
      SERVER_NAME=your-domain.com
      SERVER_HOST=https://your-domain.com

      # Security
      SECRET_KEY=your-secret-key  # Generate with: openssl rand -hex 32
      FIRST_SUPERUSER_PASSWORD=secure-password

      # Database
      POSTGRES_SERVER=db
      POSTGRES_DB=app
      POSTGRES_USER=postgres
      POSTGRES_PASSWORD=secure-password

      # Email
      SMTP_TLS=True
      SMTP_HOST=smtp.gmail.com
      SMTP_PORT=587
      SMTP_USER=your-email@gmail.com
      SMTP_PASSWORD=your-app-specific-password
      EMAILS_FROM_EMAIL=your-email@gmail.com

Docker Deployment
-----------------

1. Build production images:

   .. code-block:: bash

      docker compose -f docker-compose.yml -f docker-compose.prod.yml build

2. Start services:

   .. code-block:: bash

      docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

3. Run migrations:

   .. code-block:: bash

      docker compose exec backend alembic upgrade head

4. Create initial superuser:

   .. code-block:: bash

      docker compose exec backend python -m app.initial_data

Traefik Configuration
---------------------

The project includes Traefik as a reverse proxy:

1. Create network:

   .. code-block:: bash

      docker network create traefik-public

2. Configure domain:

   Update ``docker-compose.traefik.yml``:

   .. code-block:: yaml

      labels:
        - "traefik.http.routers.${STACK_NAME}-backend.rule=Host(`${DOMAIN}`)"

3. Start Traefik:

   .. code-block:: bash

      docker compose -f docker-compose.traefik.yml up -d

SSL Certificates
----------------

Traefik handles SSL certificates automatically:

1. Enable HTTPS:

   Update ``docker-compose.traefik.yml``:

   .. code-block:: yaml

      labels:
        - "traefik.http.routers.${STACK_NAME}-backend.tls=true"
        - "traefik.http.routers.${STACK_NAME}-backend.tls.certresolver=le"

2. Configure email:

   Update ``.env``:

   .. code-block:: text

      TRAEFIK_EMAIL=your-email@domain.com

Monitoring
----------

1. Check service status:

   .. code-block:: bash

      docker compose ps

2. View logs:

   .. code-block:: bash

      # All services
      docker compose logs

      # Specific service
      docker compose logs backend

3. Monitor resources:

   .. code-block:: bash

      docker stats

Backup and Restore
------------------

1. Backup database:

   .. code-block:: bash

      docker compose exec db pg_dump -U postgres app > backup.sql

2. Restore database:

   .. code-block:: bash

      docker compose exec -T db psql -U postgres app < backup.sql

Updates and Maintenance
-----------------------

1. Pull latest changes:

   .. code-block:: bash

      git pull origin main

2. Update dependencies:

   .. code-block:: bash

      # Backend
      docker compose exec backend uv pip install -U -e ".[dev]"

      # Frontend
      docker compose exec frontend npm update

3. Apply migrations:

   .. code-block:: bash

      docker compose exec backend alembic upgrade head

4. Rebuild and restart:

   .. code-block:: bash

      docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

1. Database connection errors:

   * Check PostgreSQL logs
   * Verify credentials
   * Check network connectivity

2. Email sending failures:

   * Verify SMTP settings
   * Check email logs
   * Test email configuration

3. SSL certificate issues:

   * Verify DNS settings
   * Check Traefik logs
   * Ensure ports 80/443 are open

Security Considerations
-----------------------

1. Keep secrets secure:
   * Use environment variables
   * Never commit sensitive data
   * Rotate keys regularly

2. Regular updates:
   * Update dependencies
   * Apply security patches
   * Monitor security advisories

3. Access control:
   * Use strong passwords
   * Implement rate limiting
   * Monitor access logs

