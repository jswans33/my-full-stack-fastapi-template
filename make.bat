@echo off
setlocal enabledelayedexpansion

:: Default target
if "%1"=="" goto help

:: Process the command
if "%1"=="help" goto help
if "%1"=="up" goto up
if "%1"=="down" goto down
if "%1"=="down-v" goto down-v
if "%1"=="build" goto build
if "%1"=="test" goto test
if "%1"=="test-backend" goto test-backend
if "%1"=="test-frontend" goto test-frontend
if "%1"=="test-e2e" goto test-e2e
if "%1"=="clean" goto clean
if "%1"=="migrate" goto migrate
if "%1"=="migration" goto migration
if "%1"=="generate-client" goto generate-client
if "%1"=="lint" goto lint
if "%1"=="format" goto format
if "%1"=="backend-dev" goto backend-dev
if "%1"=="frontend-dev" goto frontend-dev
if "%1"=="backend-install" goto backend-install
if "%1"=="frontend-install" goto frontend-install
if "%1"=="create-superuser" goto create-superuser

echo Unknown command: %1
goto help

:help
echo Available commands:
echo   make up              - Start the development environment with Docker Compose
echo   make down            - Stop the development environment
echo   make build           - Build all Docker images
echo   make test            - Run all tests (backend and frontend)
echo   make test-backend    - Run backend tests
echo   make test-frontend   - Run frontend tests
echo   make clean           - Remove Docker containers, volumes, and images
echo   make migrate         - Run database migrations
echo   make generate-client - Generate frontend API client from OpenAPI schema
echo   make lint            - Run linters on backend and frontend code
echo   make format          - Format code in backend and frontend
goto end

:up
docker compose watch
goto end

:down
docker compose down
goto end

:down-v
docker compose down -v
goto end

:build
docker compose build
goto end

:test
call :test-backend
call :test-frontend
goto end

:test-backend
docker compose exec backend bash scripts/tests-start.sh
goto end

:test-frontend
cd frontend && npm test
goto end

:test-e2e
cd frontend && npx playwright test
goto end

:clean
docker compose down -v --rmi local
goto end

:migrate
docker compose exec backend alembic upgrade head
goto end

:migration
set /p message="Enter migration message: "
docker compose exec backend alembic revision --autogenerate -m "%message%"
goto end

:generate-client
call scripts\generate-client.bat
goto end

:lint
echo Running backend linters...
docker compose exec backend ruff check app
echo Running frontend linters...
cd frontend && npm run lint
goto end

:format
echo Formatting backend code...
docker compose exec backend ruff format app
echo Formatting frontend code...
cd frontend && npm run format
goto end

:backend-dev
cd backend && call .venv\Scripts\activate.bat && fastapi run --reload app/main.py
goto end

:frontend-dev
cd frontend && npm run dev
goto end

:backend-install
cd backend && uv sync
goto end

:frontend-install
cd frontend && npm install
goto end

:create-superuser
docker compose exec backend python -m app.initial_data
goto end

:end
endlocal