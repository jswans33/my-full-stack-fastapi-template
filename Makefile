.PHONY: help up down build test clean clean-py migrate generate-client lint format render-diagrams render-diagrams-png view-diagrams docs sequence-docs

# Default target
help:
	@echo "Available commands:"
	@echo "  make up              - Start the development environment with Docker Compose"
	@echo "  make down            - Stop the development environment"
	@echo "  make build           - Build all Docker images"
	@echo "  make test            - Run all tests (backend and frontend)"
	@echo "  make test-backend    - Run backend tests"
	@echo "  make test-frontend   - Run frontend tests"
	@echo "  make clean           - Remove Docker containers, volumes, and images"
	@echo "  make clean-py        - Remove Python generated files (__pycache__, .pyc, etc.)"
	@echo "  make migrate         - Run database migrations"
	@echo "  make generate-client - Generate frontend API client from OpenAPI schema"
	@echo "  make lint            - Run linters on backend and frontend code"
	@echo "  make format          - Format code in backend and frontend"
	@echo "  make docs            - Build Sphinx documentation"
	@echo "  make sequence-docs   - Generate sequence diagrams and build documentation"


# Start the development environment
up:
	docker compose watch

# Stop the development environment
down:
	docker compose down

# Stop and remove volumes
down-v:
	docker compose down -v

# Build all Docker images
build:
	docker compose build

# Run all tests
test: 
	test-backend test-frontend

# Run backend tests
test-backend:
	docker compose exec backend bash scripts/tests-start.sh

# Run frontend tests
test-frontend:
	cd frontend && npm test

# Run frontend end-to-end tests
test-e2e:
	cd frontend && npx playwright test

# Clean up Docker resources
clean:
	docker compose down -v --rmi local

# Clean up generated Python files
clean-py:
	python -c "import os, shutil; [shutil.rmtree(os.path.join(root, d)) for root, dirs, _ in os.walk('.') for d in dirs if d == '__pycache__' or d.endswith('.egg-info') or d.endswith('.egg') or d == '.pytest_cache' or d == 'htmlcov' or d == '.mypy_cache']"
	python -c "import os; [os.remove(os.path.join(root, f)) for root, _, files in os.walk('.') for f in files if f.endswith('.pyc') or f.endswith('.pyo') or f.endswith('.pyd') or f == '.coverage']"

# Run database migrations
migrate:
	docker compose exec backend alembic upgrade head

# Create a new migration
migration:
	@read -p "Enter migration message: " message; \
	docker compose exec backend alembic revision --autogenerate -m "$$message"

# Generate frontend API client from OpenAPI schema
generate-client:
	./scripts/generate-client.sh

# Run linters
lint:
	@echo "Running backend linters..."
	docker compose exec backend ruff check app
	@echo "Running frontend linters..."
	cd frontend && npm run lint

# Format code
format:
	@echo "Formatting backend code..."
	docker compose exec backend ruff format app
	@echo "Formatting frontend code..."
	cd frontend && npm run format

# Development without Docker - Backend
backend-dev:
	cd backend && source .venv/bin/activate && fastapi run --reload app/main.py

# Development without Docker - Frontend
frontend-dev:
	cd frontend && npm run dev

# Install backend dependencies
backend-install:
	cd backend && uv sync

# Install frontend dependencies
frontend-install:
	cd frontend && npm install

# Create a new superuser
create-superuser:
	docker compose exec backend python -m app.initial_data

# Build documentation
docs:
	cd docs && python -m sphinx source build/html

# Build and open documentation
docs-open: docs
	start docs/build/html/index.html || xdg-open docs/build/html/index.html || open docs/build/html/index.html

generate-uml:
	cd docs && ../backend/.venv/Scripts/python ../scripts/ast_to_plantuml.py

docs-f:
	cd docs && python -m sphinx source build/html

docs-full:
	make uml && make docs-open

uml:
	python backend/scripts/utils/generate_uml.py --app-dir --recursive --show-imports --output docs/source/_generated_uml

# Generate sequence diagrams and build documentation
sequence-docs:
	python -m utils.run_uml_generator
	cd docs && make html
	@echo "Documentation built with sequence diagrams. Open docs/build/html/index.html to view."
