Architecture Documentation
=======================

This section provides C4 model diagrams explaining the architecture of the FastAPI Full Stack Template.

System Context (Level 1)
----------------------

.. uml::

    @startuml C4_Context
    !include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml

    LAYOUT_WITH_LEGEND()

    Person(user, "User", "A user of the application")
    Person(admin, "Administrator", "System administrator")

    System(app, "FastAPI Full Stack Application", "Web application providing user management and data handling capabilities")

    System_Ext(email_system, "Email System", "External email service for notifications")
    System_Ext(auth_provider, "Authentication Provider", "External authentication service")

    Rel(user, app, "Uses", "HTTPS")
    Rel(admin, app, "Manages", "HTTPS")
    Rel(app, email_system, "Sends emails", "SMTP")
    Rel(app, auth_provider, "Authenticates users", "OAuth2")

    @enduml

Container (Level 2)
-----------------

.. uml::

    @startuml C4_Container
    !include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml

    LAYOUT_WITH_LEGEND()

    Person(user, "User", "A user of the application")
    Person(admin, "Administrator", "System administrator")

    System_Boundary(app, "FastAPI Full Stack Application") {
        Container(web_app, "Frontend Application", "React, TypeScript", "Provides web interface")
        Container(api, "Backend API", "FastAPI, Python", "Handles business logic and data access")
        ContainerDb(db, "Database", "PostgreSQL", "Stores user and application data")
        Container(cache, "Cache", "Redis", "Caches frequently accessed data")
    }

    System_Ext(email_system, "Email System", "External email service")
    System_Ext(auth_provider, "Authentication Provider", "External auth service")

    Rel(user, web_app, "Uses", "HTTPS")
    Rel(admin, web_app, "Manages", "HTTPS")
    Rel(web_app, api, "Makes API calls", "JSON/HTTPS")
    Rel(api, db, "Reads/Writes data", "SQL")
    Rel(api, cache, "Reads/Writes data", "Redis Protocol")
    Rel(api, email_system, "Sends emails", "SMTP")
    Rel(api, auth_provider, "Authenticates", "OAuth2")

    @enduml

Component (Level 3)
-----------------

Backend Components
~~~~~~~~~~~~~~~~

.. uml::

    @startuml C4_Components_Backend
    !include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Component.puml

    LAYOUT_WITH_LEGEND()

    Container(web_app, "Frontend Application", "React", "")
    ContainerDb(db, "Database", "PostgreSQL", "")

    System_Boundary(api, "Backend API") {
        Component(api_routes, "API Routes", "FastAPI Routers", "Handles HTTP requests and responses")
        Component(auth_service, "Auth Service", "Python", "Handles authentication and authorization")
        Component(crud_service, "CRUD Service", "Python", "Handles data operations")
        Component(email_service, "Email Service", "Python", "Handles email notifications")
        Component(models, "Data Models", "SQLModel", "Defines database schema and relationships")
    }

    Rel(web_app, api_routes, "Makes API calls", "JSON/HTTPS")
    Rel(api_routes, auth_service, "Uses")
    Rel(api_routes, crud_service, "Uses")
    Rel(api_routes, email_service, "Uses")
    Rel(crud_service, models, "Uses")
    Rel(models, db, "Reads/Writes", "SQL")

    @enduml

Frontend Components
~~~~~~~~~~~~~~~~~

.. uml::

    @startuml C4_Components_Frontend
    !include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Component.puml

    LAYOUT_WITH_LEGEND()

    Container(api, "Backend API", "FastAPI", "")

    System_Boundary(web_app, "Frontend Application") {
        Component(router, "Router", "TanStack Router", "Handles client-side routing")
        Component(api_client, "API Client", "TypeScript", "Auto-generated API client")
        Component(auth_store, "Auth Store", "React Context", "Manages authentication state")
        Component(components, "UI Components", "React", "Reusable UI components")
        Component(pages, "Pages", "React", "Page components")
    }

    Rel(pages, router, "Uses")
    Rel(pages, components, "Uses")
    Rel(pages, api_client, "Uses")
    Rel(pages, auth_store, "Uses")
    Rel(api_client, api, "Makes API calls", "JSON/HTTPS")

    @enduml

Database Schema
-------------

.. uml::

    @startuml C4_Database
    !include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Component.puml

    LAYOUT_WITH_LEGEND()

    Component(user_table, "User", "Table", "Stores user information")
    Component(item_table, "Item", "Table", "Stores item information")
    Component(token_table, "Token", "Table", "Stores authentication tokens")

    Rel(item_table, user_table, "owner_id")
    Rel(token_table, user_table, "user_id")

    @enduml

Deployment Architecture
--------------------

.. uml::

    @startuml C4_Deployment
    !include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Deployment.puml

    LAYOUT_WITH_LEGEND()

    Deployment_Node(client, "Client", "Web Browser") {
        Container(spa, "Single Page Application", "React")
    }

    Deployment_Node(cloud, "Cloud Platform", "Docker Swarm/Kubernetes") {
        Deployment_Node(frontend, "Frontend Service") {
            Container(web_server, "Web Server", "Nginx")
        }
        
        Deployment_Node(backend, "Backend Service") {
            Container(api_server, "API Server", "FastAPI")
        }
        
        Deployment_Node(db_server, "Database Server") {
            ContainerDb(db, "Database", "PostgreSQL")
        }
        
        Deployment_Node(cache_server, "Cache Server") {
            Container(cache, "Cache", "Redis")
        }
    }

    Rel(client, frontend, "HTTPS")
    Rel(frontend, backend, "HTTPS")
    Rel(backend, db_server, "PostgreSQL Protocol")
    Rel(backend, cache_server, "Redis Protocol")

    @enduml