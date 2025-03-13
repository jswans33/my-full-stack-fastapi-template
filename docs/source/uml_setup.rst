UML Setup Guide
==============

Dependencies
-----------

The project uses PlantUML for generating UML diagrams. The following dependencies are required:

Java Runtime Environment (JRE)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Required for running PlantUML
* Verify installation: ``java -version``

PlantUML
~~~~~~~~
Install via package manager:

.. code-block:: bash

   # Windows (Chocolatey)
   choco install plantuml

   # macOS (Homebrew)
   brew install plantuml

   # Linux (Ubuntu/Debian)
   sudo apt-get install plantuml

Verify installation: ``plantuml -version``

Python Dependencies
~~~~~~~~~~~~~~~~~
Already included in pyproject.toml:

.. code-block:: toml

   [tool.uv]
   dev-dependencies = [
       # ... other dependencies ...
       "sphinx==7.2.6",
       "sphinx-rtd-theme==2.0.0",
       "sphinxcontrib-plantuml==0.29",
   ]

Configuration
------------

The PlantUML configuration is set in ``docs/source/conf.py``:

.. code-block:: python

   extensions = [
       # ... other extensions ...
       'sphinxcontrib.plantuml',
   ]

   # PlantUML configuration
   plantuml = 'java -jar /path/to/plantuml.jar'
   plantuml_output_format = 'svg'
   plantuml_latex_output_format = 'pdf'

Verification
-----------

You can verify the UML setup using:

.. code-block:: bash

   python backend/scripts/utils/verify_uml_setup.py

This script checks:

* Required directories exist and are writable
* UML files are readable and have valid syntax
* Sphinx configuration is correct
* PlantUML path is properly configured

Generating UML Diagrams
----------------------

Use the UML generator utility:

.. code-block:: bash

   # Generate UML for all Python files in the app directory
   python backend/scripts/utils/generate_uml.py --app-dir

   # Generate UML for a specific file
   python backend/scripts/utils/generate_uml.py -f path/to/file.py

   # Generate UML for a directory recursively
   python backend/scripts/utils/generate_uml.py -d path/to/directory --recursive

For more detailed usage instructions, see ``backend/scripts/utils/README.md``.

Troubleshooting
--------------

PlantUML Not Found
~~~~~~~~~~~~~~~~~
* Verify PlantUML is installed
* Check the plantuml.jar path in conf.py
* Ensure Java is installed and accessible

Documentation Build Issues
~~~~~~~~~~~~~~~~~~~~~~~~~
* Verify PlantUML installation: ``plantuml -version``
* Check Java installation: ``java -version``
* Update dependencies: ``uv pip install -e ".[dev]"``

UML Generation Issues
~~~~~~~~~~~~~~~~~~~
* Run the verification script
* Check the logs for specific errors
* Ensure all paths are correctly configured