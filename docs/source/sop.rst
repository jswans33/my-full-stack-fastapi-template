Standard Operating Procedures
==========================

This section outlines the standard operating procedures (SOPs) for common tasks in the FastAPI Full Stack Template.

Creating a New Project
--------------------

1. Initialize Project
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    # Using Copier (recommended)
    pipx run copier copy https://github.com/fastapi/full-stack-fastapi-template my-new-project --trust

    # Or using Git
    git clone https://github.com/fastapi/full-stack-fastapi-template my-new-project
    cd my-new-project
    rm -rf .git
    git init

2. Configure Environment
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    # Generate secret key
    python -c "import secrets; print(secrets.token_urlsafe(32))"

    # Update .env files with your settings
    cp .env.example .env
    cp frontend/.env.example frontend/.env

    # Edit .env with:
    # - Generated secret key
    # - Database credentials
    # - Email settings
    # - Other configuration

3. Initialize Database
~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    # Create fresh database
    createdb my_project_db

    # Update database name in .env
    POSTGRES_DB=my_project_db

    # Initialize schema
    cd backend
    alembic revision --autogenerate -m "initial"
    alembic upgrade head

4. Setup Development Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    # Backend setup
    cd backend
    python -m venv .venv
    source .venv/Scripts/activate  # Windows
    # source .venv/bin/activate   # Linux/Mac
    uv pip install -e ".[dev]"

    # Frontend setup
    cd ../frontend
    npm install

5. Start Development Servers
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    # Using Docker Compose
    make up

    # Or individually:
    # Terminal 1 (Backend)
    cd backend
    uvicorn app.main:app --reload

    # Terminal 2 (Frontend)
    cd frontend
    npm run dev

Updating Existing Project
-----------------------

1. Database Schema Updates
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    # 1. Update models in backend/app/models.py
    
    # 2. Generate migration
    cd backend
    alembic revision --autogenerate -m "describe_your_changes"
    
    # 3. Review migration in backend/app/alembic/versions/
    
    # 4. Apply migration
    alembic upgrade head
    
    # 5. Update initial data if needed
    python -m app.initial_data
    
    # 6. Generate new API client
    ./scripts/generate-client.sh

2. API Updates
~~~~~~~~~~~~

1. Update routes in ``backend/app/api/routes/``
2. Update CRUD operations in ``backend/app/crud.py``
3. Update tests in ``backend/app/tests/``
4. Generate new API client for frontend
5. Update frontend components to use new endpoints

3. Frontend Updates
~~~~~~~~~~~~~~~~

1. Update components in ``frontend/src/components/``
2. Update routes in ``frontend/src/routes/``
3. Update tests in ``frontend/tests/``
4. Run frontend tests: ``cd frontend && npm test``

4. Documentation Updates
~~~~~~~~~~~~~~~~~~~~~

1. Update relevant RST files in ``docs/source/``
2. Build and verify documentation: ``make docs``
3. Review changes in browser: ``make docs-open``

Project Maintenance
-----------------

Regular Updates
~~~~~~~~~~~~~

.. code-block:: bash

    # 1. Update dependencies
    cd backend
    uv pip install -e ".[dev]" --upgrade
    
    cd ../frontend
    npm update

    # 2. Run tests
    make test

    # 3. Check for formatting/lint issues
    make format
    make lint

    # 4. Update documentation
    make docs

Version Control
~~~~~~~~~~~~~

.. code-block:: bash

    # Create feature branch
    git checkout -b feature/your-feature

    # Make changes and commit
    git add .
    git commit -m "feat: your feature description"

    # Push changes
    git push origin feature/your-feature

    # Create pull request and merge after review

Deployment Updates
~~~~~~~~~~~~~~~

1. Backup production database
2. Test migrations on staging environment
3. Apply updates using deployment scripts
4. Verify application functionality
5. Monitor for any issues

Troubleshooting
-------------

Common Issues
~~~~~~~~~~~

1. Database connection issues:
   - Check PostgreSQL service
   - Verify credentials in .env
   - Run connection test: ``python backend/check_postgres.py``

2. Migration issues:
   - Backup database
   - Reset migrations if needed
   - Generate fresh migration

3. Frontend build issues:
   - Clear node_modules and reinstall
   - Check for TypeScript errors
   - Verify API client generation

Best Practices
------------

1. Version Control
   - Use feature branches
   - Write clear commit messages
   - Review changes before committing

2. Testing
   - Write tests for new features
   - Run full test suite before commits
   - Test in staging environment

3. Documentation
   - Update docs with code changes
   - Include examples for new features
   - Keep SOPs current

4. Code Quality
   - Follow style guides
   - Use type hints
   - Write clear comments