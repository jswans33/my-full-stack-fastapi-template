@echo off
setlocal enabledelayedexpansion

:: Script to generate the frontend client from the OpenAPI schema

:: Check if the backend is running
curl -s http://localhost:8000/api/v1/openapi.json > nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Backend is not running or not accessible at http://localhost:8000
    echo Please start the backend first with 'docker compose up backend' or 'make up'
    exit /b 1
)

:: Create frontend directory if it doesn't exist
if not exist frontend mkdir frontend

:: Download the OpenAPI schema
echo Downloading OpenAPI schema from backend...
curl -s http://localhost:8000/api/v1/openapi.json > frontend\openapi.json

:: Check if the download was successful
for %%F in (frontend\openapi.json) do (
    if %%~zF equ 0 (
        echo Error: Failed to download OpenAPI schema or schema is empty
        exit /b 1
    )
)

:: Navigate to frontend directory
cd frontend

:: Check if npm is installed
where npm > nul 2>&1
if %errorlevel% neq 0 (
    echo Error: npm is not installed
    exit /b 1
)

:: Generate the client
echo Generating frontend client...
call npm run generate-client

echo Frontend client generated successfully!
exit /b 0