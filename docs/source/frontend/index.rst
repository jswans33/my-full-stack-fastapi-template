Frontend Documentation
======================

This section covers the frontend implementation of the FastAPI Full Stack Template.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   architecture
   components
   routing
   state
   testing

Architecture Overview
---------------------

The frontend is built with React and modern web technologies:

* React - UI library
* TypeScript - Type safety
* Vite - Build tool
* Chakra UI - Component library
* TanStack Router - Type-safe routing
* Playwright - E2E testing

Key Features
------------

* Modern React with hooks
* Type-safe API client (auto-generated)
* Dark mode support
* Responsive design
* End-to-end testing
* Component-based architecture

Getting Started
---------------

1. Set up the development environment:

.. code-block:: bash

   cd frontend
   npm install

2. Configure environment:

.. code-block:: bash

   cp .env.example .env
   # Edit .env with your settings

3. Run development server:

.. code-block:: bash

   npm run dev

The frontend will be available at ``http://localhost:3000``.

Project Structure
-----------------

.. code-block:: text

   frontend/
   ├── src/
   │   ├── components/    # Reusable UI components
   │   ├── hooks/        # Custom React hooks
   │   ├── routes/       # Application routes
   │   ├── client/       # Auto-generated API client
   │   └── theme/        # Chakra UI theme customization
   ├── tests/            # E2E tests
   └── public/           # Static assets

Component Library
-----------------

The project uses Chakra UI for components:

* Consistent styling
* Dark mode support
* Accessible by default
* Responsive design
* Customizable theme

Testing
-------

End-to-end tests use Playwright:

.. code-block:: bash

   # Run tests
   npm run test

   # Open Playwright UI
   npx playwright test --ui

Development Tools
-----------------

* Biome - Formatting and linting
* TypeScript - Static type checking
* Vite - Fast development server
* Chrome DevTools - Debugging


