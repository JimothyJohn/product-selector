"""
Unit tests for the lambda handler.

This module contains comprehensive tests for the simplified lambda_handler function.
It focuses on API key validation, request processing, and error handling for the
generic DynamoDB operations template.

AI-generated comment: These tests have been rewritten to work with the new simplified
interface that doesn't use streaming responses or external AI services. The tests
focus on the core Lambda functionality: authentication, request validation, and 
proper HTTP response formatting.
"""

import pytest
import json
import sys
import os

# Add the lambda app directory to the Python path for importing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lambda/app'))

from app import lambda_handler


@pytest.fixture()
def apigw_event():
    """
    Generates API Gateway Event for testing.

    AI-generated comment:
    This fixture provides a sample API Gateway event compatible with the new
    simplified interface. The body contains generic JSON data that can be used
    for testing the handler's request processing logic.
    """
    return {
        "body": '{"data": "test data", "operation": "test"}',
        "headers": {
            "x-api-key": "test-api-key-12345",
            "Content-Type": "application/json"
        },
        "httpMethod": "POST",
        "path": "/test",
        "queryStringParameters": None,
        "requestContext": {
            "requestId": "test-request-id",
            "stage": "test"
        },
    }


@pytest.fixture
def lambda_context():
    """
    Creates a mock AWS Lambda context object for testing.

    AI-generated comment:
    This fixture creates a mock AWS Lambda context object with the standard
    attributes and methods that AWS Lambda provides. The simplified handler
    doesn't use streaming, so this is a basic context mock.
    """
    from unittest.mock import Mock
    
    context = Mock()
    context.function_name = "product-selector"
    context.function_version = "$LATEST"
    context.invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:product-selector"
    context.memory_limit_in_mb = 128
    context.remaining_time_in_millis = lambda: 30000
    context.request_id = "test-request-id"
    context.log_group_name = "/aws/lambda/product-selector"
    context.log_stream_name = "2024/01/01/[$LATEST]test123"
    
    return context


def test_lambda_handler_success(apigw_event, lambda_context):
    """
    Tests the lambda_handler's happy path with valid API key and request.
    
    AI-generated comment:
    This test verifies that the handler correctly processes a valid request
    with proper API key authentication and returns the expected success response
    in the standard API Gateway format.
    """
    result = lambda_handler(apigw_event, lambda_context)
    
    # Verify the response structure
    assert result["statusCode"] == 200
    assert result["headers"]["Content-Type"] == "application/json"
    
    # Parse and verify the response body
    body = json.loads(result["body"])
    assert "message" in body
    assert body["message"] == "DynamoDB operation placeholder - implement your logic here"


def test_lambda_handler_missing_api_key(apigw_event, lambda_context):
    """
    Tests the lambda_handler with a missing API key.
    
    AI-generated comment:
    This test simulates a request where the 'x-api-key' header is missing.
    The handler should return a 401 Unauthorized response with appropriate error message.
    """
    del apigw_event["headers"]["x-api-key"]
    
    result = lambda_handler(apigw_event, lambda_context)
    
    assert result["statusCode"] == 401
    assert result["headers"]["Content-Type"] == "application/json"
    
    body = json.loads(result["body"])
    assert body["error"] == "API key is missing or invalid."


def test_lambda_handler_empty_api_key(apigw_event, lambda_context):
    """
    Tests the lambda_handler with an empty API key.
    
    AI-generated comment:
    This test simulates a request with an empty 'x-api-key' header.
    The handler should return a 401 error since an empty API key is invalid.
    """
    apigw_event["headers"]["x-api-key"] = ""
    
    result = lambda_handler(apigw_event, lambda_context)
    
    assert result["statusCode"] == 401
    assert result["headers"]["Content-Type"] == "application/json"
    
    body = json.loads(result["body"])
    assert body["error"] == "API key is missing or invalid."


def test_lambda_handler_whitespace_api_key(apigw_event, lambda_context):
    """
    Tests the lambda_handler with whitespace-only API key.
    
    AI-generated comment:
    This test provides an API key that contains only whitespace. The handler should
    correctly identify this as an invalid key and return a 401 error.
    """
    apigw_event["headers"]["x-api-key"] = "   \n\t   "
    
    result = lambda_handler(apigw_event, lambda_context)
    
    assert result["statusCode"] == 401
    assert result["headers"]["Content-Type"] == "application/json"
    
    body = json.loads(result["body"])
    assert body["error"] == "API key is missing or invalid."


def test_lambda_handler_valid_body_processing(apigw_event, lambda_context):
    """
    Tests that the lambda_handler correctly processes request body.
    
    AI-generated comment:
    This test verifies that the handler can successfully parse and process
    the JSON body from the API Gateway event, which is essential for
    DynamoDB operations that will be implemented.
    """
    # Modify the body to include more complex data
    test_data = {
        "operation": "query",
        "table": "test-table",
        "key": {"id": "test-id"}
    }
    apigw_event["body"] = json.dumps(test_data)
    
    result = lambda_handler(apigw_event, lambda_context)
    
    assert result["statusCode"] == 200
    assert result["headers"]["Content-Type"] == "application/json"
    
    body = json.loads(result["body"])
    assert "message" in body


def test_lambda_handler_malformed_json(apigw_event, lambda_context):
    """
    Tests the lambda_handler with malformed JSON in the request body.
    
    AI-generated comment:
    This test provides a malformed JSON string in the body. The handler
    should catch the JSONDecodeError and return a 400 Bad Request response.
    """
    apigw_event["body"] = "{ invalid json syntax"
    
    result = lambda_handler(apigw_event, lambda_context)
    
    assert result["statusCode"] == 400
    assert result["headers"]["Content-Type"] == "application/json"
    
    body = json.loads(result["body"])
    assert body["error"] == "Invalid JSON in request body."


def test_lambda_handler_none_body(apigw_event, lambda_context):
    """
    Tests the lambda_handler with None as the request body.
    
    AI-generated comment:
    This test simulates a request with a None body. The handler should
    handle this gracefully and still perform basic API key validation.
    """
    apigw_event["body"] = None
    
    result = lambda_handler(apigw_event, lambda_context)
    
    # Should still succeed because API key is valid, even with None body
    assert result["statusCode"] == 200
    assert result["headers"]["Content-Type"] == "application/json"


def test_lambda_handler_missing_headers(apigw_event, lambda_context):
    """
    Tests the lambda_handler with missing headers entirely.
    
    AI-generated comment:
    Simulates a request where the 'headers' object is missing. The handler should
    handle this gracefully and return a 401 error since it cannot find the required API key.
    """
    del apigw_event["headers"]
    
    result = lambda_handler(apigw_event, lambda_context)
    
    assert result["statusCode"] == 401
    assert result["headers"]["Content-Type"] == "application/json"
    
    body = json.loads(result["body"])
    assert body["error"] == "API key is missing or invalid."


def test_lambda_handler_dict_body(apigw_event, lambda_context):
    """
    Tests the lambda_handler when body is already a dict (not string).
    
    AI-generated comment:
    This test provides the body as a dictionary instead of a JSON string. The handler
    should be able to process this without trying to parse it as JSON.
    """
    test_data = {"operation": "test", "data": "test_value"}
    apigw_event["body"] = test_data
    
    result = lambda_handler(apigw_event, lambda_context)
    
    assert result["statusCode"] == 200
    assert result["headers"]["Content-Type"] == "application/json"
    
    body = json.loads(result["body"])
    assert "message" in body


def test_lambda_handler_case_sensitive_headers(apigw_event, lambda_context):
    """
    Tests that API key lookup is case-sensitive.
    
    AI-generated comment:
    API Gateway typically normalizes headers to lowercase, but direct Lambda invocations
    might not. This test ensures the handler correctly handles case sensitivity.
    """
    # Remove the lowercase version and add uppercase
    del apigw_event["headers"]["x-api-key"]
    apigw_event["headers"]["X-API-KEY"] = "test-api-key"
    
    result = lambda_handler(apigw_event, lambda_context)
    
    # The current implementation `headers.get("x-api-key")` is case-sensitive
    assert result["statusCode"] == 401
    
    body = json.loads(result["body"])
    assert body["error"] == "API key is missing or invalid."


def test_lambda_handler_minimal_event(lambda_context):
    """
    Tests the lambda_handler with minimal required event structure.
    
    AI-generated comment:
    This test uses the absolute minimum event structure required for the handler
    to operate successfully, ensuring robust handling of various invocation methods.
    """
    minimal_event = {
        "body": '{"operation": "test"}',
        "headers": {"x-api-key": "test-key-12345"},
    }
    
    result = lambda_handler(minimal_event, lambda_context)
    
    assert result["statusCode"] == 200
    assert result["headers"]["Content-Type"] == "application/json"
    
    body = json.loads(result["body"])
    assert "message" in body

def test_lambda_handler_empty_string_body(apigw_event, lambda_context):
    """
    Tests the lambda_handler with empty string body.
    
    AI-generated comment:
    An empty string body should be treated as invalid JSON and result in a 400 error,
    since it cannot be parsed as valid JSON.
    """
    apigw_event["body"] = ""
    
    result = lambda_handler(apigw_event, lambda_context)
    
    assert result["statusCode"] == 400
    assert result["headers"]["Content-Type"] == "application/json"
    
    body = json.loads(result["body"])
    assert body["error"] == "Invalid JSON in request body."

def test_lambda_handler_internal_server_error():
    """
    Tests the lambda_handler's exception handling for unexpected errors.
    
    AI-generated comment:
    This test simulates an unexpected internal error to verify that the handler
    properly catches all exceptions and returns a 500 Internal Server Error response.
    """
    # Create an invalid event that will cause an exception
    invalid_event = None  # This will cause an AttributeError
    invalid_context = None
    
    result = lambda_handler(invalid_event, invalid_context)
    
    assert result["statusCode"] == 500
    assert result["headers"]["Content-Type"] == "application/json"
    
    body = json.loads(result["body"])
    assert body["error"] == "Internal server error."
