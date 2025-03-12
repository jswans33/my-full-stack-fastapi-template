API Documentation
=================

This section documents the REST API endpoints provided by the backend.

Authentication
--------------

JWT Authentication
~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from fastapi import Depends
    from app.api.deps import get_current_user

    @app.get("/protected")
    def protected_route(current_user = Depends(get_current_user)):
        return {"message": "Access granted"}

Login
~~~~~

.. code-block:: text

    POST /api/v1/login/access-token

Request body:

.. code-block:: json

    {
        "username": "user@example.com",
        "password": "password123"
    }

Response:

.. code-block:: json

    {
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "token_type": "bearer"
    }

User Endpoints
--------------

Get Current User
~~~~~~~~~~~~~~~~

.. code-block:: text

    GET /api/v1/users/me

Response:

.. code-block:: json

    {
        "id": 1,
        "email": "user@example.com",
        "is_active": true,
        "is_superuser": false
    }

Create User
~~~~~~~~~~~

.. code-block:: text

    POST /api/v1/users/

Request body:

.. code-block:: json

    {
        "email": "new@example.com",
        "password": "newpassword123"
    }

Update User
~~~~~~~~~~~

.. code-block:: text

    PUT /api/v1/users/{user_id}

Request body:

.. code-block:: json

    {
        "email": "updated@example.com",
        "password": "newpassword123"
    }

Item Endpoints
--------------

List Items
~~~~~~~~~~

.. code-block:: text

    GET /api/v1/items/

Response:

.. code-block:: json

    {
        "items": [
            {
                "id": 1,
                "title": "Item 1",
                "description": "Description 1",
                "owner_id": 1
            }
        ],
        "total": 1
    }

Create Item
~~~~~~~~~~~

.. code-block:: text

    POST /api/v1/items/

Request body:

.. code-block:: json

    {
        "title": "New Item",
        "description": "Item description"
    }

Update Item
~~~~~~~~~~~

.. code-block:: text

    PUT /api/v1/items/{item_id}

Request body:

.. code-block:: json

    {
        "title": "Updated Item",
        "description": "Updated description"
    }

Delete Item
~~~~~~~~~~~

.. code-block:: text

    DELETE /api/v1/items/{item_id}

Utility Endpoints
-----------------

Test Email
~~~~~~~~~~

.. code-block:: text

    POST /api/v1/utils/test-email

Request body:

.. code-block:: json

    {
        "email_to": "test@example.com"
    }

Error Responses
---------------

Common error responses follow this format:

.. code-block:: json

    {
        "detail": "Error message"
    }

HTTP Status Codes
-----------------

* 200: Successful operation
* 201: Resource created
* 400: Bad request
* 401: Unauthorized
* 403: Forbidden
* 404: Not found
* 422: Validation error
* 500: Server error

Rate Limiting
-------------

The API implements rate limiting:

* 100 requests per minute per IP
* 1000 requests per hour per IP

Headers returned:

.. code-block:: text

    X-RateLimit-Limit: 100
    X-RateLimit-Remaining: 99
    X-RateLimit-Reset: 1616161616

API Versioning
--------------

The API is versioned in the URL:

* ``/api/v1/`` - Current stable version
* ``/api/latest/`` - Latest development version

OpenAPI Documentation
---------------------

Interactive API documentation is available at:

* Swagger UI: ``/docs``
* ReDoc: ``/redoc``
* OpenAPI JSON: ``/openapi.json``

