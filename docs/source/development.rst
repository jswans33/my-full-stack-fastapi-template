Development Guide
=================

This guide covers the development setup and workflow for the FastAPI Full Stack Template.

Development Environment
-----------------------

Prerequisites
~~~~~~~~~~~~~

* Python 3.10+
* Node.js 18+
* Docker and Docker Compose
* Git
* Make (optional, but recommended)

Initial Setup
~~~~~~~~~~~~~

1. Clone the repository:

   .. code-block:: bash

      git clone https://github.com/fastapi/full-stack-fastapi-template.git
      cd full-stack-fastapi-template

2. Configure environment:

   .. code-block:: bash

      # Copy example environment files
      cp .env.example .env
      cp frontend/.env.example frontend/.env

      # Edit .env files with your settings
      # Generate a secret key:
      python -c "import secrets; print(secrets.token_urlsafe(32))"

3. Install dependencies:

   .. code-block:: bash

      # Backend
      cd backend
      python -m venv .venv
      source .venv/Scripts/activate  # Windows
      # source .venv/bin/activate   # Linux/Mac
      uv pip install -e ".[dev]"

      # Frontend
      cd ../frontend
      npm install

Development Workflow
--------------------

Starting Development Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use Docker Compose:

.. code-block:: bash

   make up

Or start services individually:

.. code-block:: bash

   # Backend
   cd backend
   uvicorn app.main:app --reload

   # Frontend
   cd frontend
   npm run dev

Code Formatting
~~~~~~~~~~~~~~~

The project uses automated formatters:

* Backend: Ruff
* Frontend: Biome

Format code with:

.. code-block:: bash

   make format

Linting
~~~~~~~

Run linters with:

.. code-block:: bash

   make lint

Testing
~~~~~~~

Run all tests:

.. code-block:: bash

   make test

Or run specific test suites:

.. code-block:: bash

   make test-backend
   make test-frontend
   make test-e2e

Database Migrations
~~~~~~~~~~~~~~~~~~~

Create a new migration:

.. code-block:: bash

   make migration

Apply migrations:

.. code-block:: bash

   make migrate

API Client Generation
~~~~~~~~~~~~~~~~~~~~~

After changing API endpoints, regenerate the frontend client:

.. code-block:: bash

   make generate-client

Documentation
~~~~~~~~~~~~~

Build documentation:

.. code-block:: bash

   make docs

The documentation will be available in ``docs/build/html/``.

Git Workflow
------------

1. Create a feature branch:

   .. code-block:: bash

      git checkout -b feature/your-feature-name

2. Make changes and commit:

   .. code-block:: bash

      git add .
      git commit -m "feat: your feature description"

3. Push changes:

   .. code-block:: bash

      git push origin feature/your-feature-name

4. Create a pull request

5. After review and approval, merge to main branch

Deployment
----------

See the :doc:`deployment` guide for detailed deployment instructions.

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

1. Database connection errors:

   * Check PostgreSQL is running
   * Verify database credentials in .env
   * Run ``python backend/check_postgres.py``

2. Frontend build errors:

   * Clear node_modules: ``rm -rf frontend/node_modules``
   * Reinstall: ``cd frontend && npm install``

3. Docker issues:

   * Clean containers: ``make clean``
   * Rebuild: ``make build``

Getting Help
~~~~~~~~~~~~

* Check the project documentation
* Search existing GitHub issues
* Create a new issue if needed


