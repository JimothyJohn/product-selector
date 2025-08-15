"""
Unit tests for the Lambda handler function.

AI-generated comment: These tests verify the core Lambda handler functionality
including API key validation, request processing, error handling, and response
formatting. All tests use mocked inputs and can be run locally without AWS.
"""

import json
import pytest
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../app'))

from app import lambda_handler


class TestLambdaHandler:
    """Test suite for the lambda_handler function."""
    
    @pytest.fixture
    def valid_event(self):
        """Provide a valid API Gateway event for testing."""
        return {
            "body": '{"operation": "test", "data": "sample data"}',
            "headers": {
                "x-api-key": "test-api-key-12345",
                "Content-Type": "application/json"
            },
            "httpMethod": "POST",
            "path": "/",
            "requestContext": {
                "requestId": "test-request-id"
            }
        }
    
    @pytest.fixture
    def lambda_context(self):
        """Provide a mock Lambda context for testing."""
        from unittest.mock import Mock
        
        context = Mock()
        context.function_name = "product-selector"
        context.request_id = "test-request-id"
        context.remaining_time_in_millis = lambda: 30000
        return context
    
    def test_successful_request(self, valid_event, lambda_context):
        """Test successful request processing."""
        result = lambda_handler(valid_event, lambda_context)
        
        assert result["statusCode"] == 200
        assert result["headers"]["Content-Type"] == "application/json"
        
        body = json.loads(result["body"])
        assert "message" in body
        assert body["message"] == "DynamoDB operation placeholder - implement your logic here"
    
    def test_missing_api_key(self, valid_event, lambda_context):
        """Test request with missing API key."""
        del valid_event["headers"]["x-api-key"]
        
        result = lambda_handler(valid_event, lambda_context)
        
        assert result["statusCode"] == 401
        body = json.loads(result["body"])
        assert body["error"] == "API key is missing or invalid."
    
    def test_empty_api_key(self, valid_event, lambda_context):
        """Test request with empty API key."""
        valid_event["headers"]["x-api-key"] = ""
        
        result = lambda_handler(valid_event, lambda_context)
        
        assert result["statusCode"] == 401
        body = json.loads(result["body"])
        assert body["error"] == "API key is missing or invalid."
    
    def test_whitespace_api_key(self, valid_event, lambda_context):
        """Test request with whitespace-only API key."""
        valid_event["headers"]["x-api-key"] = "   \t\n   "
        
        result = lambda_handler(valid_event, lambda_context)
        
        assert result["statusCode"] == 401
        body = json.loads(result["body"])
        assert body["error"] == "API key is missing or invalid."
    
    def test_missing_headers(self, valid_event, lambda_context):
        """Test request with missing headers."""
        del valid_event["headers"]
        
        result = lambda_handler(valid_event, lambda_context)
        
        assert result["statusCode"] == 401
        body = json.loads(result["body"])
        assert body["error"] == "API key is missing or invalid."
    
    def test_malformed_json_body(self, valid_event, lambda_context):
        """Test request with malformed JSON body."""
        valid_event["body"] = '{"invalid": json}'
        
        result = lambda_handler(valid_event, lambda_context)
        
        assert result["statusCode"] == 400
        body = json.loads(result["body"])
        assert body["error"] == "Invalid JSON in request body."
    
    def test_none_body(self, valid_event, lambda_context):
        """Test request with None body."""
        valid_event["body"] = None
        
        result = lambda_handler(valid_event, lambda_context)
        
        # Should still succeed since API key is valid
        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert "message" in body
    
    def test_dict_body(self, valid_event, lambda_context):
        """Test request with body already as dict."""
        valid_event["body"] = {"operation": "test", "data": "dict data"}
        
        result = lambda_handler(valid_event, lambda_context)
        
        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert "message" in body
    
    def test_empty_string_body(self, valid_event, lambda_context):
        """Test request with empty string body."""
        valid_event["body"] = ""
        
        result = lambda_handler(valid_event, lambda_context)
        
        assert result["statusCode"] == 400
        body = json.loads(result["body"])
        assert body["error"] == "Invalid JSON in request body."
    
    def test_complex_json_body(self, valid_event, lambda_context):
        """Test request with complex nested JSON body."""
        complex_data = {
            "operation": "query",
            "table": "products",
            "key": {"id": "product-123"},
            "filters": {
                "category": "electronics",
                "price_range": {"min": 100, "max": 500}
            },
            "options": {
                "limit": 10,
                "sort": "name",
                "projection": ["id", "name", "price"]
            }
        }
        valid_event["body"] = json.dumps(complex_data)
        
        result = lambda_handler(valid_event, lambda_context)
        
        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert "message" in body
    
    def test_case_sensitive_headers(self, valid_event, lambda_context):
        """Test that header lookup is case-sensitive."""
        # Remove lowercase and add uppercase
        del valid_event["headers"]["x-api-key"]
        valid_event["headers"]["X-API-KEY"] = "test-api-key"
        
        result = lambda_handler(valid_event, lambda_context)
        
        # Should fail because implementation looks for lowercase
        assert result["statusCode"] == 401
        body = json.loads(result["body"])
        assert body["error"] == "API key is missing or invalid."
    
    def test_internal_server_error(self, lambda_context):
        """Test handling of unexpected internal errors."""
        # Pass None as event to trigger AttributeError
        result = lambda_handler(None, lambda_context)
        
        assert result["statusCode"] == 500
        body = json.loads(result["body"])
        assert body["error"] == "Internal server error."
    
    def test_minimal_valid_event(self, lambda_context):
        """Test with minimal valid event structure."""
        minimal_event = {
            "headers": {"x-api-key": "test-key"},
            "body": "{}"
        }
        
        result = lambda_handler(minimal_event, lambda_context)
        
        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert "message" in body


class TestResponseFormat:
    """Test the response format consistency."""
    
    def test_success_response_format(self):
        """Test that success responses have consistent format."""
        event = {
            "headers": {"x-api-key": "test-key"},
            "body": '{"test": "data"}'
        }
        
        result = lambda_handler(event, None)
        
        # Check response structure
        assert "statusCode" in result
        assert "headers" in result
        assert "body" in result
        assert result["headers"]["Content-Type"] == "application/json"
        
        # Verify body is valid JSON
        body = json.loads(result["body"])
        assert isinstance(body, dict)
    
    def test_error_response_format(self):
        """Test that error responses have consistent format."""
        event = {
            "headers": {},  # Missing API key
            "body": '{"test": "data"}'
        }
        
        result = lambda_handler(event, None)
        
        # Check response structure
        assert "statusCode" in result
        assert "headers" in result
        assert "body" in result
        assert result["headers"]["Content-Type"] == "application/json"
        
        # Verify error body structure
        body = json.loads(result["body"])
        assert "error" in body
        assert isinstance(body["error"], str)


if __name__ == "__main__":
    pytest.main([__file__])
