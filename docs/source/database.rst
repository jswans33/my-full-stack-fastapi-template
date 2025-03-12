Database Documentation
======================

Database Schema Management
--------------------------

This guide provides step-by-step instructions for managing the database schema in the FastAPI template project.

.. mermaid::

   flowchart TD
       A[1. Environment Setup] --> B[2. Clean Schema]
       B --> C[3. Update Models]
       C --> D[4. Generate Migration]
       D --> E[5. Update Seed Data]
       E --> F[6. Test]

Environment Setup
~~~~~~~~~~~~~~~~~

1. Ensure PostgreSQL is running
2. Update ``.env`` in project root:

.. code-block:: env

   POSTGRES_SERVER=localhost
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=changethis
   POSTGRES_DB=app

3. Copy ``.env`` to frontend:

.. code-block:: bash

   cp .env frontend/.env

Clean Schema Setup
~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Navigate to backend directory
   cd backend

   # Clear existing migrations (keep .keep file)
   rm -f app/alembic/versions/*.py
   touch app/alembic/versions/.keep

   # Reset database
   dropdb app
   createdb app

Database Models
~~~~~~~~~~~~~~~

The project uses SQLModel for database models. Example model structure:

.. code-block:: python

   from sqlmodel import Field, Relationship, SQLModel
   from typing import Optional, List
   from datetime import date

   class Tournament(SQLModel, table=True):
       """Tournament model."""
       __tablename__ = "tournaments"

       tournament_id: Optional[int] = Field(default=None, primary_key=True)
       name: str = Field(...)
       start_date: date = Field(...)
       location: Optional[str] = Field(default=None)
       notes: Optional[str] = Field(default=None)

       # Relationships
       registrations: List["Registration"] = Relationship(back_populates="tournament")

Migration Management
~~~~~~~~~~~~~~~~~~~~

Generate and apply migrations:

.. code-block:: bash

   # From backend directory
   cd backend

   # Generate initial migration
   alembic revision --autogenerate -m "initialize_schema"

   # Apply migration
   alembic upgrade head

   # Verify current migration
   alembic current

Testing
~~~~~~~

.. code-block:: bash

   # From backend directory
   ./scripts/test.sh

   # Start development servers
   docker compose up -d

Common Issues & Solutions
~~~~~~~~~~~~~~~~~~~~~~~~~

Migration Conflicts
^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # Reset migrations
   cd backend
   rm -f app/alembic/versions/*.py
   touch app/alembic/versions/.keep
   alembic revision --autogenerate -m "fresh_start"
   alembic upgrade head

Database Connection Issues
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # Check database connection
   python backend/check_postgres.py

   # Verify environment variables
   cat .env

   # Check PostgreSQL status
   docker compose ps

Data Inconsistencies
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # Full reset
   cd backend
   dropdb app
   createdb app
   alembic upgrade head
   python -m app.initial_data

Best Practices
~~~~~~~~~~~~~~

1. Model Organization
   - Keep models in ``backend/app/models.py``
   - Use type hints for all fields
   - Document relationships between models
   - Use appropriate SQLModel field types

2. Migration Management
   - Use descriptive migration names
   - One logical change per migration
   - Test migrations both up and down
   - Keep migrations in version control

3. Seed Data
   - Maintain minimal but functional test data
   - Update ``initial_data.py`` for each schema change
   - Include example of each model relationship
   - Add superuser account for testing

4. Testing
   - Update tests in ``backend/app/tests/``
   - Add model-specific tests
   - Test API endpoints after schema changes
   - Verify frontend compatibility

API Updates
~~~~~~~~~~~

When changing the schema, remember to update:

1. API Routes (``backend/app/api/routes/``)
2. CRUD Operations (``backend/app/crud.py``)
3. API Tests (``backend/app/tests/api/``)
4. Frontend Types (will be auto-generated)

Frontend Integration
~~~~~~~~~~~~~~~~~~~~

After schema changes:

1. Generate new API client:

.. code-block:: bash

   ./scripts/generate-client.sh

2. Update frontend components to match new schema
3. Update frontend tests
4. Test all affected features

Deployment Considerations
~~~~~~~~~~~~~~~~~~~~~~~~~

1. Always backup production database before migrations
2. Test migrations on staging environment first
3. Plan for backward compatibility
4. Document breaking changes
5. Update deployment scripts if needed

Quick Reference
~~~~~~~~~~~~~~~

.. code-block:: bash

   # Full Reset
   cd backend
   rm -f app/alembic/versions/*.py
   touch app/alembic/versions/.keep
   dropdb app
   createdb app
   alembic revision --autogenerate -m "fresh_start"
   alembic upgrade head
   python -m app.initial_data

   # Development Setup
   docker compose up -d

   # Generate Frontend Client
   ./scripts/generate-client.sh


