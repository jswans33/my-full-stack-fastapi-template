Database Models
===============

The application uses SQLModel for database models, combining the best of SQLAlchemy and Pydantic.

Base Models
-----------

User Model
~~~~~~~~~~

.. code-block:: python

    class User(SQLModel, table=True):
        """User model."""
        id: Optional[int] = Field(default=None, primary_key=True)
        email: str = Field(..., unique=True, index=True)
        hashed_password: str = Field(...)
        is_active: bool = Field(default=True)
        is_superuser: bool = Field(default=False)

        # Relationships
        items: List["Item"] = Relationship(back_populates="owner")

Item Model
~~~~~~~~~~

.. code-block:: python

    class Item(SQLModel, table=True):
        """Item model."""
        id: Optional[int] = Field(default=None, primary_key=True)
        title: str = Field(..., index=True)
        description: str = Field(default=None)
        owner_id: int = Field(foreign_key="user.id")

        # Relationships
        owner: User = Relationship(back_populates="items")

Model Relationships
-------------------

.. mermaid::

    erDiagram
        User ||--o{ Item : owns
        User {
            int id PK
            string email
            string hashed_password
            boolean is_active
            boolean is_superuser
        }
        Item {
            int id PK
            string title
            string description
            int owner_id FK
        }

Field Types
-----------

Common Field Types
~~~~~~~~~~~~~~~~~~

* ``int``: Integer values
* ``str``: String values
* ``bool``: Boolean values
* ``datetime``: Date and time
* ``date``: Date only
* ``float``: Floating point numbers
* ``UUID``: Unique identifiers

Field Options
~~~~~~~~~~~~~

* ``primary_key``: Primary key field
* ``foreign_key``: Foreign key reference
* ``unique``: Unique constraint
* ``index``: Create database index
* ``default``: Default value
* ``nullable``: Allow NULL values

Example:

.. code-block:: python

    class Example(SQLModel, table=True):
        id: Optional[int] = Field(default=None, primary_key=True)
        unique_code: str = Field(..., unique=True)
        indexed_field: str = Field(..., index=True)
        nullable_field: Optional[str] = Field(default=None)
        default_value: str = Field(default="default")

Relationships
-------------

One-to-Many
~~~~~~~~~~~

.. code-block:: python

    class Parent(SQLModel, table=True):
        id: Optional[int] = Field(default=None, primary_key=True)
        children: List["Child"] = Relationship(back_populates="parent")

    class Child(SQLModel, table=True):
        id: Optional[int] = Field(default=None, primary_key=True)
        parent_id: int = Field(foreign_key="parent.id")
        parent: Parent = Relationship(back_populates="children")

Many-to-Many
~~~~~~~~~~~~

.. code-block:: python

    class TagLink(SQLModel, table=True):
        item_id: int = Field(foreign_key="item.id", primary_key=True)
        tag_id: int = Field(foreign_key="tag.id", primary_key=True)

    class Item(SQLModel, table=True):
        id: Optional[int] = Field(default=None, primary_key=True)
        tags: List["Tag"] = Relationship(
            back_populates="items",
            link_model=TagLink
        )

    class Tag(SQLModel, table=True):
        id: Optional[int] = Field(default=None, primary_key=True)
        items: List[Item] = Relationship(
            back_populates="tags",
            link_model=TagLink
        )

Model Configuration
-------------------

Table Configuration
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    class CustomModel(SQLModel, table=True):
        __tablename__ = "custom_table_name"
        __table_args__ = {
            "mysql_engine": "InnoDB",
            "mysql_charset": "utf8mb4"
        }

Indexes and Constraints
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from sqlalchemy import Index, UniqueConstraint

    class IndexedModel(SQLModel, table=True):
        __table_args__ = (
            Index("idx_field1_field2", "field1", "field2"),
            UniqueConstraint("field1", "field2", name="unique_fields")
        )

Model Methods
-------------

Common Methods
~~~~~~~~~~~~~~

.. code-block:: python

    class User(SQLModel, table=True):
        id: Optional[int] = Field(default=None, primary_key=True)
        email: str
        hashed_password: str

        def verify_password(self, password: str) -> bool:
            """Verify password."""
            return verify_password(password, self.hashed_password)

        @property
        def full_name(self) -> str:
            """Get full name."""
            return f"{self.first_name} {self.last_name}"

Model Mixins
------------

.. code-block:: python

    class TimestampMixin(SQLModel):
        created_at: datetime = Field(default_factory=datetime.utcnow)
        updated_at: datetime = Field(
            default_factory=datetime.utcnow,
            sa_column_kwargs={"onupdate": datetime.utcnow}
        )

    class User(TimestampMixin, SQLModel, table=True):
        id: Optional[int] = Field(default=None, primary_key=True)
        # ... other fields


