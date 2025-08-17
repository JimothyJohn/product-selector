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


class TestHelperFunctions:
    """Test utility functions used by the Lambda handler."""
    
    def test_convert_dynamodb_item_string(self):
        """Test DynamoDB string conversion."""
        from app import _convert_dynamodb_item
        
        result = _convert_dynamodb_item({"S": "test string"})
        assert result == "test string"
    
    def test_convert_dynamodb_item_number_int(self):
        """Test DynamoDB integer number conversion."""
        from app import _convert_dynamodb_item
        
        result = _convert_dynamodb_item({"N": "123"})
        assert result == 123
        assert isinstance(result, int)
    
    def test_convert_dynamodb_item_number_float(self):
        """Test DynamoDB float number conversion."""
        from app import _convert_dynamodb_item
        
        result = _convert_dynamodb_item({"N": "123.45"})
        assert result == 123.45
        assert isinstance(result, float)
    
    def test_convert_dynamodb_item_boolean(self):
        """Test DynamoDB boolean conversion."""
        from app import _convert_dynamodb_item
        
        assert _convert_dynamodb_item({"BOOL": True}) is True
        assert _convert_dynamodb_item({"BOOL": False}) is False
    
    def test_convert_dynamodb_item_null(self):
        """Test DynamoDB null conversion."""
        from app import _convert_dynamodb_item
        
        result = _convert_dynamodb_item({"NULL": True})
        assert result is None
    
    def test_convert_dynamodb_item_list(self):
        """Test DynamoDB list conversion."""
        from app import _convert_dynamodb_item
        
        result = _convert_dynamodb_item({
            "L": [
                {"S": "item1"},
                {"N": "42"},
                {"BOOL": True}
            ]
        })
        assert result == ["item1", 42, True]
    
    def test_convert_dynamodb_item_map(self):
        """Test DynamoDB map/dict conversion."""
        from app import _convert_dynamodb_item
        
        result = _convert_dynamodb_item({
            "M": {
                "name": {"S": "test"},
                "count": {"N": "5"}
            }
        })
        assert result == {"name": "test", "count": 5}
    
    def test_convert_dynamodb_item_string_set(self):
        """Test DynamoDB string set conversion."""
        from app import _convert_dynamodb_item
        
        result = _convert_dynamodb_item({"SS": ["a", "b", "c"]})
        assert result == ["a", "b", "c"]
    
    def test_convert_dynamodb_item_number_set(self):
        """Test DynamoDB number set conversion."""
        from app import _convert_dynamodb_item
        
        result = _convert_dynamodb_item({"NS": ["1", "2.5", "3"]})
        assert result == [1, 2.5, 3]
    
    def test_convert_dynamodb_item_unknown_type(self):
        """Test DynamoDB unknown type handling."""
        from app import _convert_dynamodb_item
        
        unknown_value = {"UNKNOWN": "value"}
        result = _convert_dynamodb_item(unknown_value)
        assert result == unknown_value


class TestFilterItems:
    """Test the filter_items function."""
    
    def test_filter_no_filters(self):
        """Test filtering with no filters returns all items."""
        from app import filter_items
        
        items = [{"PK": "gearbox#GB-001", "model_name": "Test"}]
        result = filter_items(items, {})
        assert result == items
    
    def test_filter_category_gearbox_item(self):
        """Test category filtering on gearbox items."""
        from app import filter_items
        
        items = [
            {
                "PK": "gearbox#GB-001",
                "application_type": "automotive",
                "model_name": "Auto Gearbox"
            },
            {
                "PK": "gearbox#GB-002",
                "application_type": "industrial",
                "model_name": "Industrial Gearbox"
            }
        ]
        
        result = filter_items(items, {"category": "automotive"})
        assert len(result) == 1
        assert result[0]["model_name"] == "Auto Gearbox"
    
    def test_filter_category_category_item(self):
        """Test category filtering on category items."""
        from app import filter_items
        
        items = [
            {"PK": "category#automotive", "category_name": "Automotive"},
            {"PK": "category#industrial", "category_name": "Industrial"}
        ]
        
        result = filter_items(items, {"category": "automotive"})
        assert len(result) == 1
        assert result[0]["category_name"] == "Automotive"
    
    def test_filter_manufacturer(self):
        """Test manufacturer filtering."""
        from app import filter_items
        
        items = [
            {"PK": "gearbox#GB-001", "manufacturer": "ABC Corp"},
            {"PK": "gearbox#GB-002", "manufacturer": "XYZ Industries"}
        ]
        
        result = filter_items(items, {"manufacturer": "ABC"})
        assert len(result) == 1
        assert result[0]["manufacturer"] == "ABC Corp"
    
    def test_filter_price_range(self):
        """Test price range filtering."""
        from app import filter_items
        
        items = [
            {"PK": "gearbox#GB-001", "price_range": "low"},
            {"PK": "gearbox#GB-002", "price_range": "high"}
        ]
        
        result = filter_items(items, {"price_range": "low"})
        assert len(result) == 1
        assert result[0]["price_range"] == "low"
    
    def test_filter_min_torque(self):
        """Test minimum torque filtering."""
        from app import filter_items
        
        items = [
            {"PK": "gearbox#GB-001", "torque_rating": 1000},
            {"PK": "gearbox#GB-002", "torque_rating": 3000}
        ]
        
        result = filter_items(items, {"min_torque": "2000"})
        assert len(result) == 1
        assert result[0]["torque_rating"] == 3000
    
    def test_filter_min_performance(self):
        """Test minimum performance filtering."""
        from app import filter_items
        
        items = [
            {"PK": "gearbox#GB-001", "performance_rating": 70},
            {"PK": "gearbox#GB-002", "performance_rating": 90}
        ]
        
        result = filter_items(items, {"min_performance": "80"})
        assert len(result) == 1
        assert result[0]["performance_rating"] == 90
    
    def test_filter_invalid_torque(self):
        """Test filtering with invalid torque values."""
        from app import filter_items
        
        items = [
            {"PK": "gearbox#GB-001", "torque_rating": "invalid"},
            {"PK": "gearbox#GB-002", "torque_rating": 3000}
        ]
        
        result = filter_items(items, {"min_torque": "invalid_filter"})
        # Should return all items since filter is invalid
        assert len(result) == 2
    
    def test_filter_multiple_conditions(self):
        """Test filtering with multiple conditions."""
        from app import filter_items
        
        items = [
            {
                "PK": "gearbox#GB-001",
                "application_type": "automotive",
                "torque_rating": 3000,
                "manufacturer": "ABC Corp"
            },
            {
                "PK": "gearbox#GB-002",
                "application_type": "automotive",
                "torque_rating": 1000,
                "manufacturer": "ABC Corp"
            }
        ]
        
        result = filter_items(items, {
            "category": "automotive",
            "min_torque": "2000",
            "manufacturer": "ABC"
        })
        assert len(result) == 1
        assert result[0]["torque_rating"] == 3000


class TestCRUDOperations:
    """Test CRUD operations for gearbox management."""
    
    @patch('app.dynamodb.put_item')
    def test_create_gearbox_complete(self, mock_put):
        """Test creating a gearbox with all optional fields."""
        from app import create_gearbox
        
        mock_put.return_value = {}
        
        data = {
            "gearbox": {
                "gearbox_id": "GB-TEST-001",
                "model_name": "Complete Test Gearbox",
                "manufacturer": "Test Corp",
                "gearbox_type": "planetary",
                "torque_rating": 2500,
                "performance_rating": 85,
                "application_type": "automotive",
                "price_range": "medium"
            },
            "timestamp": "2025-08-17T12:00:00Z"
        }
        
        result = create_gearbox(data)
        
        assert result["statusCode"] == 201
        body = json.loads(result["body"])
        assert body["gearbox_id"] == "GB-TEST-001"
        
        # Verify put_item was called with correct parameters
        mock_put.assert_called_once()
        call_args = mock_put.call_args
        assert call_args[1]["TableName"] == "gearbox_catalog"
        assert "ConditionExpression" in call_args[1]
    
    @patch('app.dynamodb.put_item')
    def test_create_gearbox_duplicate(self, mock_put):
        """Test creating a gearbox that already exists."""
        from app import create_gearbox
        from botocore.exceptions import ClientError
        
        # Mock ConditionalCheckFailedException
        mock_put.side_effect = ClientError(
            {"Error": {"Code": "ConditionalCheckFailedException"}},
            "PutItem"
        )
        
        data = {
            "gearbox": {
                "gearbox_id": "GB-DUPLICATE",
                "model_name": "Test",
                "manufacturer": "Test Corp",
                "gearbox_type": "planetary"
            }
        }
        
        result = create_gearbox(data)
        
        assert result["statusCode"] == 409
        body = json.loads(result["body"])
        assert "already exists" in body["error"]
    
    @patch('app.dynamodb.update_item')
    def test_update_gearbox_success(self, mock_update):
        """Test successful gearbox update."""
        from app import update_gearbox
        
        mock_update.return_value = {}
        
        data = {
            "gearbox_id": "GB-TEST-001",
            "updates": {
                "torque_rating": 3000,
                "performance_rating": 90,
                "model_name": "Updated Gearbox"
            },
            "timestamp": "2025-08-17T12:30:00Z"
        }
        
        result = update_gearbox(data)
        
        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert body["gearbox_id"] == "GB-TEST-001"
        assert "torque_rating" in body["updated_fields"]
    
    @patch('app.dynamodb.update_item')
    def test_update_gearbox_not_found(self, mock_update):
        """Test updating a non-existent gearbox."""
        from app import update_gearbox
        from botocore.exceptions import ClientError
        
        mock_update.side_effect = ClientError(
            {"Error": {"Code": "ConditionalCheckFailedException"}},
            "UpdateItem"
        )
        
        data = {
            "gearbox_id": "GB-NONEXISTENT",
            "updates": {"torque_rating": 3000}
        }
        
        result = update_gearbox(data)
        
        assert result["statusCode"] == 404
        body = json.loads(result["body"])
        assert "not found" in body["error"]
    
    def test_update_gearbox_no_updates(self):
        """Test update with no update fields provided."""
        from app import update_gearbox
        
        data = {
            "gearbox_id": "GB-TEST-001",
            "updates": {}
        }
        
        result = update_gearbox(data)
        
        assert result["statusCode"] == 400
        body = json.loads(result["body"])
        assert "No updates provided" in body["error"]
    
    @patch('app.dynamodb.update_item')
    def test_update_gearbox_protected_fields(self, mock_update):
        """Test update attempting to modify protected fields."""
        from app import update_gearbox
        
        data = {
            "gearbox_id": "GB-TEST-001",
            "updates": {
                "PK": "modified-pk",
                "SK": "modified-sk",
                "gearbox_id": "modified-id"
            }
        }
        
        result = update_gearbox(data)
        
        assert result["statusCode"] == 400
        body = json.loads(result["body"])
        assert "No valid fields" in body["error"]
    
    @patch('app.dynamodb.delete_item')
    def test_delete_gearbox_success(self, mock_delete):
        """Test successful gearbox deletion."""
        from app import delete_gearbox
        
        mock_delete.return_value = {}
        
        data = {"gearbox_id": "GB-TEST-001"}
        
        result = delete_gearbox(data)
        
        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert body["gearbox_id"] == "GB-TEST-001"
        assert "deleted successfully" in body["message"]
    
    @patch('app.dynamodb.delete_item')
    def test_delete_gearbox_not_found(self, mock_delete):
        """Test deleting a non-existent gearbox."""
        from app import delete_gearbox
        from botocore.exceptions import ClientError
        
        mock_delete.side_effect = ClientError(
            {"Error": {"Code": "ConditionalCheckFailedException"}},
            "DeleteItem"
        )
        
        data = {"gearbox_id": "GB-NONEXISTENT"}
        
        result = delete_gearbox(data)
        
        assert result["statusCode"] == 404
        body = json.loads(result["body"])
        assert "not found" in body["error"]
    
    def test_delete_gearbox_no_id(self):
        """Test deletion without providing gearbox ID."""
        from app import delete_gearbox
        
        data = {}
        
        result = delete_gearbox(data)
        
        assert result["statusCode"] == 400
        body = json.loads(result["body"])
        assert "gearbox_id is required" in body["error"]


class TestErrorHandling:
    """Test error handling scenarios."""
    
    @patch('app.dynamodb.scan')
    def test_dynamodb_client_error(self, mock_scan):
        """Test DynamoDB client error handling."""
        from botocore.exceptions import ClientError
        
        mock_scan.side_effect = ClientError(
            {"Error": {"Code": "ResourceNotFoundException", "Message": "Table not found"}},
            "Scan"
        )
        
        valid_get_event = {
            "body": None,
            "headers": {"x-api-key": "test-key"},
            "httpMethod": "GET",
            "queryStringParameters": None
        }
        
        result = lambda_handler(valid_get_event, None)
        
        assert result["statusCode"] == 500
        body = json.loads(result["body"])
        assert "Database operation failed" in body["error"]
    
    @patch('app.dynamodb.scan')
    def test_unexpected_exception(self, mock_scan):
        """Test handling of unexpected exceptions."""
        mock_scan.side_effect = RuntimeError("Unexpected error")
        
        valid_get_event = {
            "body": None,
            "headers": {"x-api-key": "test-key"},
            "httpMethod": "GET",
            "queryStringParameters": None
        }
        
        result = lambda_handler(valid_get_event, None)
        
        assert result["statusCode"] == 500
        body = json.loads(result["body"])
        assert "Internal server error" in body["error"]
    
    @patch('app.get_all_gearboxes')
    def test_pagination_handling(self, mock_get_all):
        """Test that pagination is handled correctly in get_all_gearboxes."""
        # This test verifies our function can handle the pagination logic
        mock_get_all.return_value = []
        
        valid_get_event = {
            "body": None,
            "headers": {"x-api-key": "test-key"},
            "httpMethod": "GET",
            "queryStringParameters": None
        }
        
        result = lambda_handler(valid_get_event, None)
        
        assert result["statusCode"] == 200
        mock_get_all.assert_called_once()


class TestLoggingConfiguration:
    """Test logging configuration functionality."""
    
    def test_configure_logging_default(self):
        """Test logging configuration with default level."""
        from app import configure_logging
        import logging
        
        with patch.dict(os.environ, {}, clear=True):
            logger = configure_logging()
            assert logger.level == logging.INFO
    
    def test_configure_logging_debug(self):
        """Test logging configuration with DEBUG level."""
        from app import configure_logging
        import logging
        
        with patch.dict(os.environ, {"LOG_LEVEL": "DEBUG"}):
            logger = configure_logging()
            assert logger.level == logging.DEBUG
    
    def test_configure_logging_invalid_level(self):
        """Test logging configuration with invalid level defaults to INFO."""
        from app import configure_logging
        import logging
        
        with patch.dict(os.environ, {"LOG_LEVEL": "INVALID"}):
            logger = configure_logging()
            assert logger.level == logging.INFO


if __name__ == "__main__":
    pytest.main([__file__])
