"""
Pytest configuration and shared fixtures for product-selector tests.

AI-generated comment: Updated configuration for the simplified product-selector
application. This configuration supports both the main test suite and the
lambda-specific tests in the lambda/tests directory.

This module contains pytest configuration, markers, and fixtures
that are shared across all test modules.
"""

import pytest
import os


def pytest_configure(config):
    """
    Configure pytest with custom markers.
    
    AI-generated comment: Updated markers to reflect the new simplified
    application structure and testing requirements.
    """
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")
    config.addinivalue_line(
        "markers", "security: marks tests as security-focused tests"
    )
    config.addinivalue_line("markers", "performance: marks tests as performance tests")
    config.addinivalue_line("markers", "aws_lambda: marks tests for Lambda function")
    config.addinivalue_line("markers", "api_gateway: marks tests for API Gateway integration")


@pytest.fixture(scope="session")
def test_api_key():
    """
    Test API key for integration tests.
    
    AI-generated comment: Updated to use a generic test API key since the
    simplified interface doesn't require a specific external service key.
    """
    return os.getenv("TEST_API_KEY", "test-api-key-12345")


@pytest.fixture(scope="session")
def aws_stack_name():
    """
    AWS stack name for integration tests.
    
    AI-generated comment: Updated default stack name to match the new
    product-selector application.
    """
    return os.getenv("AWS_SAM_STACK_NAME", "product-selector")


@pytest.fixture(autouse=True)
def reset_environment():
    """Reset environment variables after each test."""
    original_env = os.environ.copy()
    yield
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def mock_lambda_context():
    """
    Mock AWS Lambda context for testing.
    
    AI-generated comment: Updated context to reflect the new product-selector
    function name and adjusted memory settings for the simplified implementation.
    """
    from unittest.mock import Mock

    context = Mock()
    context.function_name = "product-selector"
    context.function_version = "$LATEST"
    context.invoked_function_arn = (
        "arn:aws:lambda:us-east-1:123456789012:function:product-selector"
    )
    context.memory_limit_in_mb = 512
    context.remaining_time_in_millis = Mock(return_value=30000)
    context.request_id = "test-request-id"
    context.log_group_name = "/aws/lambda/product-selector"
    context.log_stream_name = "2024/01/01/[$LATEST]test123"
    context.aws_request_id = "test-aws-request-id"

    return context


# Pytest collection modifications
def pytest_collection_modifyitems(config, items):
    """
    Modify test collection to add markers based on file paths.
    
    AI-generated comment: Updated to handle both main tests and lambda tests,
    and added markers for the new simplified application structure.
    """
    for item in items:
        # Add markers based on test file location
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "performance" in str(item.fspath):
            item.add_marker(pytest.mark.performance)
            item.add_marker(pytest.mark.slow)  # Performance tests are typically slow

        # Add aws_lambda marker for tests in lambda directory
        if "/lambda/" in str(item.fspath):
            item.add_marker(pytest.mark.aws_lambda)
        
        # Add API Gateway marker for API Gateway tests
        if "api_gateway" in str(item.fspath) or "api_gateway" in item.name:
            item.add_marker(pytest.mark.api_gateway)

        # Add security marker for security tests
        if "security" in str(item.fspath) or "security" in item.name:
            item.add_marker(pytest.mark.security)

        # Add slow marker for tests with "slow" in the name
        if "slow" in item.name or "timeout" in item.name or "large" in item.name:
            item.add_marker(pytest.mark.slow)


@pytest.fixture(scope="session")
def lambda_function_name():
    """
    Lambda function name for integration tests.
    
    AI-generated comment: Provides the Lambda function name for direct
    Lambda invocation tests, separate from API Gateway tests.
    """
    return os.getenv("LAMBDA_FUNCTION_NAME", "product-selector")
