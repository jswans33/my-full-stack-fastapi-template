# Makefile Usage Guide

This project includes a Makefile to simplify common development tasks. The Makefile provides shortcuts for operations like starting the development environment, running tests, and managing the database.

## Prerequisites

- Make sure you have `make` installed on your system
  - On Windows, you can either:
    - Install it via [Chocolatey](https://chocolatey.org/): `choco install make`, or
    - Use the provided `make.bat` file which provides the same commands without requiring make installation
  - On macOS, it's included with the Xcode Command Line Tools: `xcode-select --install`
  - On Linux, install it via your package manager: `apt-get install make` or `yum install make`
- Docker and Docker Compose should be installed and running
- For local development without Docker, ensure you have Python and Node.js installed

## Windows Users

This project includes a `make.bat` file that provides the same functionality as the Makefile but works natively on Windows without requiring make installation. You can use it with the same commands:

```batch
make up
make test
make migrate
```

## Available Commands

### General Commands

- `make help` - Display available commands
- `make up` - Start the development environment with Docker Compose
- `make down` - Stop the development environment
- `make down-v` - Stop the development environment and remove volumes
- `make build` - Build all Docker images
- `make clean` - Remove Docker containers, volumes, and images

### Testing Commands

- `make test` - Run all tests (backend and frontend)
- `make test-backend` - Run backend tests
- `make test-frontend` - Run frontend tests
- `make test-e2e` - Run frontend end-to-end tests with Playwright

### Database Commands

- `make migrate` - Run database migrations
- `make migration` - Create a new migration (will prompt for a message)

### Development Commands

- `make generate-client` - Generate frontend API client from OpenAPI schema
- `make lint` - Run linters on backend and frontend code
- `make format` - Format code in backend and frontend
- `make backend-dev` - Run backend development server without Docker
- `make frontend-dev` - Run frontend development server without Docker
- `make backend-install` - Install backend dependencies
- `make frontend-install` - Install frontend dependencies
- `make create-superuser` - Create a new superuser

### Virtual Environment Commands

- `make setup-utils` - Set up the utils virtual environment
- `make setup-utils-clean` - Clean and set up the utils virtual environment
- `make setup-backend` - Set up the backend virtual environment
- `make utils-venv` - Show commands to activate the utils virtual environment
- `make backend-venv` - Show commands to activate the backend virtual environment

## Examples

### Starting the Development Environment

```bash
make up
```

This will start all services defined in the Docker Compose file and watch for changes.

### Running Tests

```bash
# Run all tests
make test

# Run only backend tests
make test-backend

# Run only frontend tests
make test-frontend
```

### Managing Database Migrations

```bash
# Apply all pending migrations
make migrate

# Create a new migration
make migration
# Enter a message when prompted, e.g., "Add user profile table"
```

### Development Without Docker

```bash
# Install dependencies
make backend-install
make frontend-install

# Start development servers
make backend-dev
make frontend-dev
```

### Working with Virtual Environments

```bash
# Set up the utils virtual environment
make setup-utils

# Clean and set up the utils virtual environment
make setup-utils-clean

# Set up the backend virtual environment
make setup-backend

# Get commands to activate the utils virtual environment
make utils-venv
# Then run the displayed command in your terminal, for example:
# On Windows CMD: utils\.venv\Scripts\activate
# On Windows Git Bash: source utils/.venv/Scripts/activate
# On Unix/Linux/Mac: source utils/.venv/bin/activate

# Get commands to activate the backend virtual environment
make backend-venv
# Then run the displayed command in your terminal, for example:
# On Windows CMD: backend\.venv\Scripts\activate
# On Windows Git Bash: source backend/.venv/Scripts/activate
# On Unix/Linux/Mac: source backend/.venv/bin/activate
```

The utils virtual environment is particularly useful for running utility scripts that need access to the backend code, such as sequence diagram generation and UML tools. The backend virtual environment is used for backend development without Docker.

## Customizing the Makefile

Feel free to modify the Makefile to add your own commands or customize existing ones. The Makefile is designed to be a helpful tool for your development workflow, so adapt it to your needs.