Security Documentation
======================

This section covers the security features and implementations in the FastAPI Full Stack Template.

Authentication
--------------

JWT Implementation
~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from jose import jwt
    from datetime import datetime, timedelta

    def create_access_token(data: dict, expires_delta: timedelta) -> str:
        """Create JWT access token."""
        expire = datetime.utcnow() + expires_delta
        to_encode = data.copy()
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

Password Hashing
~~~~~~~~~~~~~~~~

.. code-block:: python

    from passlib.context import CryptContext

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def get_password_hash(password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)

    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password."""
        return pwd_context.verify(plain_password, hashed_password)

Authorization
-------------

Role-Based Access Control
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from fastapi import Depends, HTTPException
    from app.api.deps import get_current_user

    def get_current_active_superuser(
        current_user = Depends(get_current_user),
    ):
        """Check if current user is superuser."""
        if not current_user.is_superuser:
            raise HTTPException(403, "Not enough privileges")
        return current_user

Permission System
~~~~~~~~~~~~~~~~~

.. code-block:: python

    from enum import Enum
    from typing import List

    class Permission(str, Enum):
        READ = "read"
        WRITE = "write"
        DELETE = "delete"
        ADMIN = "admin"

    def check_permissions(user: User, required: List[Permission]) -> bool:
        """Check if user has required permissions."""
        return all(perm in user.permissions for perm in required)

CORS Configuration
------------------

.. code-block:: python

    from fastapi.middleware.cors import CORSMiddleware

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

Rate Limiting
-------------

.. code-block:: python

    from fastapi import Request
    from fastapi.middleware import Middleware
    from slowapi import Limiter
    from slowapi.util import get_remote_address

    limiter = Limiter(key_func=get_remote_address)

    @app.get("/api/limited")
    @limiter.limit("5/minute")
    async def limited_route(request: Request):
        return {"message": "rate limited endpoint"}

Input Validation
----------------

Request Validation
~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from pydantic import BaseModel, EmailStr, constr

    class UserCreate(BaseModel):
        email: EmailStr
        password: constr(min_length=8)
        full_name: constr(max_length=50)

SQL Injection Prevention
~~~~~~~~~~~~~~~~~~~~~~~~

* Using SQLModel/SQLAlchemy ORM
* Parameterized queries
* Input sanitization

XSS Prevention
~~~~~~~~~~~~~~

* Content-Security-Policy headers
* HTML escaping
* Sanitized template rendering

CSRF Protection
---------------

.. code-block:: python

    from fastapi import FastAPI, Request
    from fastapi.middleware.csrf import CSRFMiddleware

    app.add_middleware(
        CSRFMiddleware,
        secret="your-secret-key",
        safe_methods={"GET", "HEAD", "OPTIONS"}
    )

Security Headers
----------------

.. code-block:: python

    from fastapi.middleware.security import SecurityMiddleware

    app.add_middleware(
        SecurityMiddleware,
        headers={
            "X-Frame-Options": "DENY",
            "X-Content-Type-Options": "nosniff",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains"
        }
    )

Secure File Uploads
-------------------

.. code-block:: python

    import aiofiles
    from fastapi import UploadFile
    from pathlib import Path

    async def save_upload_file(upload_file: UploadFile, destination: Path):
        """Securely save uploaded file."""
        try:
            async with aiofiles.open(destination, 'wb') as out_file:
                content = await upload_file.read()
                await out_file.write(content)
        finally:
            await upload_file.close()

Audit Logging
-------------

.. code-block:: python

    from datetime import datetime
    from typing import Optional

    class AuditLog(SQLModel, table=True):
        id: Optional[int] = Field(default=None, primary_key=True)
        timestamp: datetime = Field(default_factory=datetime.utcnow)
        user_id: Optional[int] = Field(default=None, foreign_key="user.id")
        action: str
        resource: str
        details: Optional[dict]

Security Best Practices
-----------------------

1. Password Policies
~~~~~~~~~~~~~~~~~~~~

* Minimum length requirements
* Complexity requirements
* Password history
* Regular password changes

2. Session Management
~~~~~~~~~~~~~~~~~~~~~

* Secure session storage
* Session timeout
* Session invalidation
* Concurrent session control

3. Error Handling
~~~~~~~~~~~~~~~~~

* Generic error messages
* Detailed internal logging
* Secure error pages
* No sensitive data in errors

4. Data Protection
~~~~~~~~~~~~~~~~~~

* Encryption at rest
* Encryption in transit
* Secure key management
* Data backup and recovery

5. Access Control
~~~~~~~~~~~~~~~~~

* Principle of least privilege
* Role-based access control
* Regular access reviews
* Audit trails

6. Monitoring and Alerts
~~~~~~~~~~~~~~~~~~~~~~~~

* Security event logging
* Real-time alerts
* Performance monitoring
* Anomaly detection

7. Compliance
~~~~~~~~~~~~~

* GDPR compliance
* Data privacy
* Security standards
* Regular audits

