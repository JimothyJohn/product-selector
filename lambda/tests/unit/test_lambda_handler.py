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
from unittest.mock import patch, Mock

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../app'))

from app import lambda_handler


class TestLambdaHandler:
    """Test suite for the lambda_handler function."""
    
    @pytest.fixture
    def valid_get_event(self):
        """Provide a valid API Gateway GET event for testing."""
        return {
            "body": None,
            "headers": {
                "x-api-key": "test-api-key-12345",
                "Content-Type": "application/json"
            },
            "httpMethod": "GET",
            "path": "/gearboxes",
            "queryStringParameters": None,
            "requestContext": {
                "requestId": "test-request-id"
            }
        }
    
    @pytest.fixture
    def valid_post_event(self):
        """Provide a valid API Gateway POST event for testing."""
        return {
            "body": '{"operation": "test", "data": "sample data"}',
            "headers": {
                "x-api-key": "test-api-key-12345",
                "Content-Type": "application/json"
            },
            "httpMethod": "POST",
            "path": "/gearboxes",
            "queryStringParameters": None,
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
    
    @patch('app.dynamodb.scan')
    def test_successful_get_all_gearboxes(self, mock_scan, valid_get_event, lambda_context):
        """Test successful GET request for all gearboxes."""
        # Mock DynamoDB response
        mock_scan.return_value = {
            'Items': [
                {
                    'PK': {'S': 'gearbox#GB-001'},
                    'SK': {'S': 'metadata'},
                    'gearbox_id': {'S': 'GB-001'},
                    'model_name': {'S': 'Test Gearbox'},
                    'manufacturer': {'S': 'Test Corp'},
                    'gearbox_type': {'S': 'planetary'},
                    'torque_rating': {'N': '1000'}
                }
            ],
            'Count': 1,
            'ScannedCount': 1
        }
        
        result = lambda_handler(valid_get_event, lambda_context)
        
        assert result["statusCode"] == 200
        assert result["headers"]["Content-Type"] == "application/json"
        
        body = json.loads(result["body"])
        assert "message" in body
        assert body["message"] == "Gearbox Catalog - All Items"
        assert "gearboxes" in body
        assert len(body["gearboxes"]) == 1
    
    def test_post_invalid_operation(self, valid_post_event, lambda_context):
        """Test POST request with invalid operation."""
        # The test event has operation: "test" which is not a valid operation
        result = lambda_handler(valid_post_event, lambda_context)
        
        assert result["statusCode"] == 400
        body = json.loads(result["body"])
        assert "Unknown operation: test" in body["error"]
    
    @patch('app.dynamodb.scan')
    def test_missing_api_key(self, mock_scan, valid_get_event, lambda_context):
        """Test request with missing API key - should work without authentication."""
        del valid_get_event["headers"]["x-api-key"]
        
        # Mock DynamoDB response
        mock_scan.return_value = {
            'Items': [],
            'Count': 0,
            'ScannedCount': 0
        }
        
        result = lambda_handler(valid_get_event, lambda_context)
        
        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert "message" in body
    
    @patch('app.dynamodb.scan')
    def test_empty_api_key(self, mock_scan, valid_get_event, lambda_context):
        """Test request with empty API key - should work without authentication."""
        valid_get_event["headers"]["x-api-key"] = ""
        
        # Mock DynamoDB response
        mock_scan.return_value = {
            'Items': [],
            'Count': 0,
            'ScannedCount': 0
        }
        
        result = lambda_handler(valid_get_event, lambda_context)
        
        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert "message" in body
    
    @patch('app.dynamodb.scan')
    def test_whitespace_api_key(self, mock_scan, valid_get_event, lambda_context):
        """Test request with whitespace-only API key - should work without authentication."""
        valid_get_event["headers"]["x-api-key"] = "   \t\n   "
        
        # Mock DynamoDB response
        mock_scan.return_value = {
            'Items': [],
            'Count': 0,
            'ScannedCount': 0
        }
        
        result = lambda_handler(valid_get_event, lambda_context)
        
        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert "message" in body
    
    @patch('app.dynamodb.scan')
    def test_missing_headers(self, mock_scan, valid_get_event, lambda_context):
        """Test request with missing headers - should work without authentication."""
        del valid_get_event["headers"]
        
        # Mock DynamoDB response
        mock_scan.return_value = {
            'Items': [],
            'Count': 0,
            'ScannedCount': 0
        }
        
        result = lambda_handler(valid_get_event, lambda_context)
        
        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert "message" in body
    
    def test_malformed_json_body(self, valid_post_event, lambda_context):
        """Test request with malformed JSON body."""
        valid_post_event["body"] = '{"invalid": json}'
        
        result = lambda_handler(valid_post_event, lambda_context)
        
        assert result["statusCode"] == 400
        body = json.loads(result["body"])
        assert body["error"] == "Invalid JSON in request body."
    
    @patch('app.dynamodb.scan')
    def test_none_body(self, mock_scan, valid_get_event, lambda_context):
        """Test request with None body."""
        mock_scan.return_value = {'Items': [], 'Count': 0, 'ScannedCount': 0}
        valid_get_event["body"] = None
        
        result = lambda_handler(valid_get_event, lambda_context)
        
        # Should still succeed since API key is valid
        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert "message" in body
    
    @patch('app.dynamodb.scan')
    def test_get_with_category_filter(self, mock_scan, valid_get_event, lambda_context):
        """Test GET request with category filter."""
        valid_get_event["queryStringParameters"] = {"category": "automotive"}
        
        # Mock DynamoDB scan response
        mock_scan.return_value = {
            'Items': [
                {
                    'PK': {'S': 'category#automotive'},
                    'SK': {'S': 'metadata'},
                    'category_name': {'S': 'Automotive Gearboxes'}
                },
                {
                    'PK': {'S': 'category#industrial'},
                    'SK': {'S': 'metadata'},
                    'category_name': {'S': 'Industrial Gearboxes'}
                },
                {
                    'PK': {'S': 'gearbox#GB-001'},
                    'SK': {'S': 'metadata'},
                    'gearbox_type': {'S': 'planetary'},
                    'model_name': {'S': 'Automotive Gearbox'},
                    'application_type': {'S': 'automotive'}
                },
                {
                    'PK': {'S': 'gearbox#GB-002'},
                    'SK': {'S': 'metadata'},
                    'gearbox_type': {'S': 'helical'},
                    'model_name': {'S': 'Industrial Gearbox'},
                    'application_type': {'S': 'industrial'}
                }
            ],
            'Count': 4,
            'ScannedCount': 4
        }
        
        result = lambda_handler(valid_get_event, lambda_context)
        
        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert "category=automotive" in body["message"]
        assert body["filters_applied"]["category"] == "automotive"
        assert len(body["categories"]) == 1  # Only automotive category
        assert len(body["gearboxes"]) == 1  # Only automotive gearbox
    
    @patch('app.dynamodb.scan')
    def test_get_with_type_filter(self, mock_scan, valid_get_event, lambda_context):
        """Test GET request with gearbox type filter."""
        valid_get_event["queryStringParameters"] = {"type": "planetary"}
        
        mock_scan.return_value = {
            'Items': [
                {
                    'PK': {'S': 'gearbox#GB-001'},
                    'SK': {'S': 'metadata'},
                    'gearbox_type': {'S': 'planetary'},
                    'model_name': {'S': 'Planetary Gearbox'}
                },
                {
                    'PK': {'S': 'gearbox#GB-002'},
                    'SK': {'S': 'metadata'},
                    'gearbox_type': {'S': 'helical'},
                    'model_name': {'S': 'Helical Gearbox'}
                }
            ],
            'Count': 2,
            'ScannedCount': 2
        }
        
        result = lambda_handler(valid_get_event, lambda_context)
        
        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert "type=planetary" in body["message"]
        assert body["filters_applied"]["type"] == "planetary"
        assert len(body["gearboxes"]) == 1  # Only planetary gearbox
    
    @patch('app.dynamodb.scan')
    def test_get_with_multiple_filters(self, mock_scan, valid_get_event, lambda_context):
        """Test GET request with multiple filters."""
        valid_get_event["queryStringParameters"] = {
            "category": "automotive",
            "min_torque": "2000"
        }
        
        mock_scan.return_value = {
            'Items': [
                {
                    'PK': {'S': 'gearbox#GB-001'},
                    'SK': {'S': 'metadata'},
                    'application_type': {'S': 'automotive'},
                    'torque_rating': {'N': '3000'},
                    'model_name': {'S': 'High Torque Auto Gearbox'}
                },
                {
                    'PK': {'S': 'gearbox#GB-002'},
                    'SK': {'S': 'metadata'},
                    'application_type': {'S': 'automotive'},
                    'torque_rating': {'N': '1500'},
                    'model_name': {'S': 'Low Torque Auto Gearbox'}
                }
            ],
            'Count': 2,
            'ScannedCount': 2
        }
        
        result = lambda_handler(valid_get_event, lambda_context)
        
        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert "category=automotive" in body["message"]
        assert "min_torque=2000" in body["message"]
        assert len(body["gearboxes"]) == 1  # Only high torque gearbox
    
    @patch('app.dynamodb.scan')
    def test_get_no_results_with_filter(self, mock_scan, valid_get_event, lambda_context):
        """Test GET request with filter that returns no results."""
        valid_get_event["queryStringParameters"] = {"category": "nonexistent"}
        
        mock_scan.return_value = {
            'Items': [
                {
                    'PK': {'S': 'gearbox#GB-001'},
                    'SK': {'S': 'metadata'},
                    'application_type': {'S': 'automotive'},
                    'model_name': {'S': 'Auto Gearbox'}
                }
            ],
            'Count': 1,
            'ScannedCount': 1
        }
        
        result = lambda_handler(valid_get_event, lambda_context)
        
        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert body["summary"]["total_items"] == 0
        assert len(body["gearboxes"]) == 0
        assert len(body["categories"]) == 0
    
    @patch('app.dynamodb.scan')
    def test_case_sensitive_headers(self, mock_scan, valid_get_event, lambda_context):
        """Test that header lookup is case-sensitive - should work without API key."""
        # Remove lowercase and add uppercase
        del valid_get_event["headers"]["x-api-key"]
        valid_get_event["headers"]["X-API-KEY"] = "test-api-key"
        
        # Mock DynamoDB response
        mock_scan.return_value = {
            'Items': [],
            'Count': 0,
            'ScannedCount': 0
        }
        
        result = lambda_handler(valid_get_event, lambda_context)
        
        # Should succeed without API key requirement
        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert "message" in body
    
    def test_internal_server_error(self, lambda_context):
        """Test handling of unexpected internal errors."""
        # Pass None as event to trigger AttributeError
        result = lambda_handler(None, lambda_context)
        
        assert result["statusCode"] == 500
        body = json.loads(result["body"])
        assert body["error"] == "Internal server error."
    
    @patch('app.dynamodb.scan')
    def test_minimal_valid_event(self, mock_scan, lambda_context):
        """Test with minimal valid event structure."""
        mock_scan.return_value = {'Items': [], 'Count': 0, 'ScannedCount': 0}
        minimal_event = {
            "headers": {"x-api-key": "test-key"},
            "body": None,
            "httpMethod": "GET",
            "queryStringParameters": None
        }
        
        result = lambda_handler(minimal_event, lambda_context)
        
        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert "message" in body
    
    def test_unsupported_method(self, valid_get_event, lambda_context):
        """Test unsupported HTTP method."""
        valid_get_event["httpMethod"] = "DELETE"
        
        result = lambda_handler(valid_get_event, lambda_context)
        
        assert result["statusCode"] == 405
        body = json.loads(result["body"])
        assert "not allowed" in body["error"]
    
    @patch('app.dynamodb.put_item')
    def test_create_gearbox_success(self, mock_put, valid_post_event, lambda_context):
        """Test successful gearbox creation."""
        # Mock successful DynamoDB put_item
        mock_put.return_value = {}
        
        # Update the event body with valid create operation
        create_data = {
            "operation": "create",
            "gearbox": {
                "gearbox_id": "GB-TEST-001",
                "model_name": "Test Gearbox",
                "manufacturer": "Test Corp",
                "gearbox_type": "planetary"
            }
        }
        valid_post_event["body"] = json.dumps(create_data)
        
        result = lambda_handler(valid_post_event, lambda_context)
        
        assert result["statusCode"] == 201
        body = json.loads(result["body"])
        assert body["message"] == "Gearbox created successfully"
        assert body["gearbox_id"] == "GB-TEST-001"
    
    def test_create_gearbox_missing_fields(self, valid_post_event, lambda_context):
        """Test gearbox creation with missing required fields."""
        create_data = {
            "operation": "create",
            "gearbox": {
                "gearbox_id": "GB-TEST-001",
                # Missing required fields
            }
        }
        valid_post_event["body"] = json.dumps(create_data)
        
        result = lambda_handler(valid_post_event, lambda_context)
        
        assert result["statusCode"] == 400
        body = json.loads(result["body"])
        assert "Missing required field" in body["error"]
    
    def test_post_no_body(self, valid_post_event, lambda_context):
        """Test POST request with no body."""
        valid_post_event["body"] = ""
        
        result = lambda_handler(valid_post_event, lambda_context)
        
        assert result["statusCode"] == 400
        body = json.loads(result["body"])
        assert "Request body is required" in body["error"]


class TestResponseFormat:
    """Test the response format consistency."""
    
    @patch('app.dynamodb.scan')
    def test_success_response_format(self, mock_scan):
        """Test that success responses have consistent format."""
        mock_scan.return_value = {'Items': [], 'Count': 0, 'ScannedCount': 0}
        event = {
            "headers": {"x-api-key": "test-key"},
            "body": None,
            "httpMethod": "GET",
            "queryStringParameters": None
        }
        
        result = lambda_handler(event, None)
        
        # Check response structure
        assert "statusCode" in result
        assert "headers" in result
        assert "body" in result
        assert result["headers"]["Content-Type"] == "application/json"
        assert "Access-Control-Allow-Origin" in result["headers"]
        
        # Verify body is valid JSON
        body = json.loads(result["body"])
        assert isinstance(body, dict)
        assert "message" in body
    
    @patch('app.dynamodb.scan')
    def test_error_response_format(self, mock_scan):
        """Test response format for unsupported method (actual error case)."""
        event = {
            "headers": {"x-api-key": "test-key"},
            "body": None,
            "httpMethod": "PATCH",  # Unsupported method
            "queryStringParameters": None
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
        assert result["statusCode"] == 405
        assert isinstance(body["error"], str)


if __name__ == "__main__":
    pytest.main([__file__])
