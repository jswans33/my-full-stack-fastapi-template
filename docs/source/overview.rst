Project Overview
================

The FastAPI Full Stack Template is a modern web application template that combines a FastAPI backend with a React frontend.

Key Features
------------

* FastAPI backend with SQLModel ORM
* React frontend with TypeScript
* PostgreSQL database
* Docker Compose setup
* JWT authentication
* Email integration
* Automated testing
* CI/CD with GitHub Actions

Architecture
------------

The project follows a clean architecture pattern with clear separation of concerns:

Backend
~~~~~~~

* FastAPI for REST API
* SQLModel for database ORM
* Alembic for migrations
* Pydantic for validation
* JWT for authentication

Frontend
~~~~~~~~

* React with TypeScript
* Chakra UI components
* TanStack Router
* Auto-generated API client
* End-to-end testing with Playwright

Infrastructure
~~~~~~~~~~~~~~

* PostgreSQL database
* Docker Compose
* Traefik reverse proxy
* GitHub Actions CI/CD
* Email service integration

Getting Started
---------------

1. Clone the repository
2. Configure environment variables
3. Start development environment:

   .. code-block:: bash

      make up

4. Access services:

   * Backend API: http://localhost:8000
   * Frontend: http://localhost:3000
   * API docs: http://localhost:8000/docs

Development Workflow
--------------------

The project includes several make commands to help with development:

* ``make up`` - Start development environment
* ``make test`` - Run all tests
* ``make format`` - Format code
* ``make lint`` - Run linters
* ``make migrate`` - Run database migrations
* ``make docs`` - Build documentation

