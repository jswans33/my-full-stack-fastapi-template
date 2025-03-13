UML Diagrams Structure
====================

This page documents the structure of generated UML diagrams in the project.

Directory Structure
------------------

The following directory structure is created in ``docs/source/_generated_uml/`` when running the UML generator:

.. code-block:: text

    _generated_uml/
    ├── all.puml                   # Combined diagram with all components
    ├── plantuml_generator.puml    # Main generator diagram
    ├── api/                       # API components
    │   ├── api_deps.py.puml
    │   ├── api_routes_items.py.puml
    │   ├── api_routes_login.py.puml
    │   ├── api_routes_private.py.puml
    │   ├── api_routes_users.py.puml
    │   └── api_routes_utils.py.puml
    ├── core/                      # Core components
    │   ├── core_config.py.puml
    │   ├── core_db.py.puml
    │   ├── core_logging_logging.py.puml
    │   └── core_security.py.puml
    ├── examples/                  # Example components
    │   ├── examples_logging_example.py.puml
    │   └── examples_run_logging_example.py.puml
    ├── models/                    # Data models
    │   ├── _models.py.puml
    │   └── alembic_versions_e2412789c190_initialize_models.py.puml
    ├── tests/                     # Test components
    │   ├── _conftest.py.puml
    │   ├── api_routes_test_items.py.puml
    │   ├── api_routes_test_login.py.puml
    │   ├── api_routes_test_private.py.puml
    │   ├── api_routes_test_users.py.puml
    │   ├── core_test_logging.py.puml
    │   ├── crud_test_user.py.puml
    │   ├── scripts_test_backend_pre_start.py.puml
    │   ├── scripts_test_test_pre_start.py.puml
    │   ├── utils_item.py.puml
    │   ├── utils_user.py.puml
    │   └── utils_utils.py.puml
    ├── uml_generator/            # UML generator components
    │   ├── cli.puml
    │   ├── config.puml
    │   ├── exceptions.puml
    │   ├── factories.puml
    │   ├── filesystem.puml
    │   ├── interfaces.puml
    │   ├── models.puml
    │   ├── path_resolver.puml
    │   ├── service.puml
    │   ├── test_uml_gen.puml
    │   ├── config/               # Config components
    │   │   └── loader.puml
    │   ├── generator/            # Generator components
    │   │   └── plantuml_generator.puml
    │   ├── models/               # Model components
    │   │   └── models.puml
    │   ├── parsers/              # Parser components
    │   │   ├── ast_parser.puml
    │   │   ├── base_parser.puml
    │   │   ├── class_parser.puml
    │   │   ├── function_parser.puml
    │   │   ├── import_parser.puml
    │   │   ├── relationship_parser.puml
    │   │   ├── type_parser.puml
    │   │   └── python/          # Python-specific parsers
    │   │       ├── ast_parser.puml
    │   │       ├── class_parser.puml
    │   │       ├── function_parser.puml
    │   │       ├── import_parser.puml
    │   │       ├── relationship_parser.puml
    │   │       └── type_parser.puml
    │   └── tests/               # UML generator tests
    │       ├── conftest.puml
    │       ├── test_cli.puml
    │       ├── test_config.puml
    │       ├── test_generator.puml
    │       ├── test_integration.puml
    │       ├── test_models.puml
    │       └── test_parser.puml
    └── utils/                   # Utility components
        ├── _backend_pre_start.py.puml
        ├── _crud.py.puml
        ├── _initial_data.py.puml
        ├── _main.py.puml
        ├── _tests_pre_start.py.puml
        ├── _utils.py.puml
        ├── alembic_env.py.puml
        ├── alembic_versions_1a31ce608336_add_cascade_delete_relationships.py.puml
        ├── alembic_versions_9c0a54914c78_add_max_length_for_string_varchar_.py.puml
        └── alembic_versions_d98dd8ec85a3_edit_replace_id_integers_in_all_models_.py.puml

Running the Generator
--------------------

To generate the UML diagrams, run:

.. code-block:: bash

    python utils/run_uml_generator.py

This will process Python files in the project and create PlantUML diagrams in the structure shown above.