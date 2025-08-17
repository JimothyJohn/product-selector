# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AWS SAM-based serverless application that provides a gearbox catalog API with filtering capabilities. The application manages gearbox product data stored in DynamoDB and exposes REST endpoints through API Gateway. The main Lambda function handles CRUD operations and supports filtering by category, type, manufacturer, torque rating, performance rating, and price range.

## Architecture

- **Lambda Function**: `ProductSelectorFunction` (app.py) - Main handler for API requests
- **Database**: DynamoDB table `gearbox_catalog` with GSI `GSI1-PerformanceIndex` for querying by type
- **API**: REST API with `/gearboxes` endpoint supporting GET/POST operations
- **Auth**: API key authentication via `x-api-key` header
- **Data Model**: Gearboxes have attributes like gearbox_id, model_name, manufacturer, gearbox_type, torque_rating, performance_rating

## Development Commands

### Local Development
```bash
# Install dependencies
uv sync

# Format code
cd lambda && uv run ruff format app

# Run unit tests
cd lambda && PYTHONPATH="app" uv run pytest tests/unit

# Run integration tests (requires deployed stack)
cd lambda && PYTHONPATH="app" uv run pytest tests/integration

# Run all tests
PYTHONPATH="app" uv run pytest  # From root
cd lambda && PYTHONPATH="app" uv run pytest  # From lambda dir

# Test Lambda function locally with filtering
cd lambda && PYTHONPATH="app" uv run python -m app
cd lambda && PYTHONPATH="app" uv run python -m app --category automotive
cd lambda && PYTHONPATH="app" uv run python -m app --type planetary --min-torque 3000

# Set logging level for troubleshooting
export LOG_LEVEL=DEBUG  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
cd lambda && PYTHONPATH="app" uv run python -m app --verbose
```

### AWS SAM Operations
```bash
# Validate template
cd lambda && sam validate --lint

# Build
cd lambda && sam build

# Deploy
cd lambda && sam deploy

# Local API (requires build first)
cd lambda && sam local start-api

# Full deployment pipeline (use Quickstart script)
./Quickstart
```

## Testing

- **Unit tests**: `lambda/tests/unit/` - Mock-based tests for Lambda function logic
- **Integration tests**: `lambda/tests/integration/` - Tests against deployed AWS resources
- **Root tests**: `tests/` - Additional test utilities and fixtures
- **Test markers**: unit, integration, slow, security, aws_lambda, api_gateway
- **API Key**: Tests use `TEST_API_KEY` environment variable or default test key

## Key Files

- `lambda/app/app.py` - Main Lambda handler with CRUD operations
- `lambda/template.yaml` - SAM template defining AWS resources
- `lambda/samconfig.toml` - SAM deployment configuration
- `pyproject.toml` - Python project configuration and dependencies
- `gearbox_client_example.py` - Reference client implementation
- `Quickstart` - Full deployment script with validation, build, and deploy

## Development Notes

- Use `uv` for Python dependency management
- Lambda function uses Python 3.11 runtime
- DynamoDB operations use native boto3 client (not resource)
- API responses include CORS headers for cross-origin requests
- Error handling includes specific status codes and structured error messages
- The application maintains backward compatibility with `/hello` endpoint