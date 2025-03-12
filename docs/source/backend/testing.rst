Testing Documentation
=====================

This section covers the testing strategy and implementation for the backend.

Test Structure
--------------

Directory Layout
~~~~~~~~~~~~~~~~

.. code-block:: text

    backend/app/tests/
    ├── __init__.py
    ├── conftest.py           # Shared fixtures
    ├── api/                  # API tests
    │   └── routes/          # Route-specific tests
    ├── core/                # Core module tests
    ├── crud/                # CRUD operation tests
    └── utils/               # Test utilities

Test Configuration
------------------

pytest Configuration
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    # conftest.py
    import pytest
    from fastapi.testclient import TestClient
    from sqlmodel import Session, SQLModel, create_engine
    from sqlalchemy.pool import StaticPool

    @pytest.fixture(scope="session")
    def engine():
        """Create test database engine."""
        return create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )

    @pytest.fixture(scope="function")
    def db(engine):
        """Create test database session."""
        SQLModel.metadata.create_all(engine)
        with Session(engine) as session:
            yield session
            session.rollback()
        SQLModel.metadata.drop_all(engine)

    @pytest.fixture(scope="module")
    def client():
        """Create test client."""
        from app.main import app
        with TestClient(app) as c:
            yield c

Test Types
----------

Unit Tests
~~~~~~~~~~

Testing individual components in isolation:

.. code-block:: python

    def test_create_user(db: Session):
        """Test user creation."""
        user_in = UserCreate(
            email="test@example.com",
            password="password123"
        )
        user = crud.user.create(db, obj_in=user_in)
        assert user.email == user_in.email
        assert hasattr(user, "hashed_password")

Integration Tests
~~~~~~~~~~~~~~~~~

Testing component interactions:

.. code-block:: python

    def test_create_user_api(client: TestClient):
        """Test user creation via API."""
        response = client.post(
            "/api/v1/users/",
            json={
                "email": "test@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "test@example.com"

API Tests
~~~~~~~~~

Testing API endpoints:

.. code-block:: python

    def test_read_users(client: TestClient, superuser_token_headers):
        """Test get users endpoint."""
        response = client.get(
            "/api/v1/users/",
            headers=superuser_token_headers,
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)

Test Fixtures
-------------

Common Fixtures
~~~~~~~~~~~~~~~

.. code-block:: python

    @pytest.fixture
    def normal_user(db: Session) -> User:
        """Create test user."""
        user_in = UserCreate(
            email="user@example.com",
            password="password123"
        )
        return crud.user.create(db, obj_in=user_in)

    @pytest.fixture
    def superuser(db: Session) -> User:
        """Create test superuser."""
        user_in = UserCreate(
            email="admin@example.com",
            password="admin123",
            is_superuser=True
        )
        return crud.user.create(db, obj_in=user_in)

Authentication Fixtures
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    @pytest.fixture
    def user_token_headers(client: TestClient, normal_user: User):
        """Get user authentication headers."""
        return get_user_authentication_headers(client, normal_user)

    @pytest.fixture
    def superuser_token_headers(client: TestClient, superuser: User):
        """Get superuser authentication headers."""
        return get_user_authentication_headers(client, superuser)

Test Utilities
--------------

Helper Functions
~~~~~~~~~~~~~~~~

.. code-block:: python

    def random_email() -> str:
        """Generate random email."""
        return f"test{random.randint(1, 100000)}@example.com"

    def random_lower_string(k: int = 32) -> str:
        """Generate random string."""
        return "".join(random.choices(string.ascii_lowercase, k=k))

Test Data Generation
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    def create_random_item(db: Session, owner_id: int) -> Item:
        """Create random test item."""
        title = random_lower_string()
        description = random_lower_string()
        item_in = ItemCreate(title=title, description=description)
        return crud.item.create_with_owner(
            db=db, obj_in=item_in, owner_id=owner_id
        )

Running Tests
-------------

Command Line
~~~~~~~~~~~~

.. code-block:: bash

    # Run all tests
    pytest

    # Run specific test file
    pytest tests/api/test_users.py

    # Run specific test function
    pytest tests/api/test_users.py::test_create_user

    # Run with coverage
    pytest --cov=app --cov-report=term-missing

Configuration Options
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: ini

    # pytest.ini
    [pytest]
    testpaths = tests
    python_files = test_*.py
    python_functions = test_*
    filterwarnings =
        ignore::DeprecationWarning
        ignore::UserWarning

Coverage Configuration
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: ini

    # .coveragerc
    [run]
    source = app
    omit =
        app/tests/*
        app/alembic/*
        app/core/config.py

    [report]
    exclude_lines =
        pragma: no cover
        def __repr__
        raise NotImplementedError

Continuous Integration
----------------------

GitHub Actions
~~~~~~~~~~~~~~

.. code-block:: yaml

    name: Tests
    on: [push, pull_request]
    jobs:
      test:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v2
          - name: Set up Python
            uses: actions/setup-python@v2
            with:
              python-version: "3.10"
          - name: Install dependencies
            run: |
              python -m pip install --upgrade pip
              pip install -e ".[dev]"
          - name: Run tests
            run: |
              pytest --cov=app --cov-report=xml
          - name: Upload coverage
            uses: codecov/codecov-action@v2

Best Practices
--------------

1. Test Organization
~~~~~~~~~~~~~~~~~~~~

* Group related tests
* Use descriptive names
* Follow naming conventions
* Maintain test isolation

2. Test Coverage
~~~~~~~~~~~~~~~~

* Aim for high coverage
* Test edge cases
* Test error conditions
* Test security features

3. Test Performance
~~~~~~~~~~~~~~~~~~~

* Use test databases
* Clean up test data
* Optimize test runs
* Use appropriate scopes

4. Test Maintenance
~~~~~~~~~~~~~~~~~~~

* Keep tests up to date
* Refactor when needed
* Document complex tests
* Review test results

