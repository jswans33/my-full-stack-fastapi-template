#!/bin/bash

# Script to generate the frontend client from the OpenAPI schema

set -e

# Check if the backend is running
if ! curl -s http://localhost:8000/api/v1/openapi.json > /dev/null; then
    echo "Error: Backend is not running or not accessible at http://localhost:8000"
    echo "Please start the backend first with 'docker compose up backend' or 'make up'"
    exit 1
fi

# Create frontend directory if it doesn't exist
mkdir -p frontend

# Download the OpenAPI schema
echo "Downloading OpenAPI schema from backend..."
curl -s http://localhost:8000/api/v1/openapi.json > frontend/openapi.json

# Check if the download was successful
if [ ! -s frontend/openapi.json ]; then
    echo "Error: Failed to download OpenAPI schema or schema is empty"
    exit 1
fi

# Navigate to frontend directory
cd frontend

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "Error: npm is not installed"
    exit 1
fi

# Generate the client
echo "Generating frontend client..."
npm run generate-client

echo "Frontend client generated successfully!"
