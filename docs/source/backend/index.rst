Backend Documentation
=====================

This section covers the backend implementation of the FastAPI Full Stack Template.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   architecture
   api
   models
   security
   testing

Architecture Overview
---------------------

The backend is built with FastAPI and follows a clean architecture pattern:

* Core Layer - Business logic and domain models
* API Layer - REST endpoints and request/response models
* Infrastructure Layer - Database, external services, etc.

Key Components
--------------

* FastAPI - Modern, fast web framework
* SQLModel - SQL database ORM
* Alembic - Database migrations
* Pydantic - Data validation
* JWT - Authentication
* Pytest - Testing framework

Getting Started
---------------

1. Set up the development environment:

.. code-block:: bash

   # Create virtual environment
   cd backend
   python -m venv .venv
   source .venv/Scripts/activate  # Windows
   # source .venv/bin/activate   # Linux/Mac

   # Install dependencies
   uv pip install -e ".[dev]"

2. Configure environment variables:

.. code-block:: bash

   cp .env.example .env
   # Edit .env with your settings

3. Run development server:

.. code-block:: bash

   docker compose up -d

The API will be available at ``http://localhost:8000``.

API Documentation
-----------------

Interactive API documentation is available at:

* Swagger UI: ``http://localhost:8000/docs``
* ReDoc: ``http://localhost:8000/redoc``


