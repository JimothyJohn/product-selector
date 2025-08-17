"""
Integration tests that can run against both deployed Lambda and local SAM API.

These tests automatically detect whether to use:
1. sam local start-api (http://localhost:3000) for local testing
2. Deployed AWS Lambda function for integration testing

To run against local SAM API:
1. In one terminal: cd lambda && sam build && sam local start-api
2. In another terminal: cd lambda && PYTHONPATH="app" uv run pytest tests/integration/test_local_api.py

To run against deployed AWS:
Export environment variables or ensure samconfig.toml is configured, then run the tests.
"""

import json
import os
import time
from typing import Optional, Dict, Any
from urllib.parse import urljoin

import pytest
import requests
import boto3
from botocore.exceptions import ClientError

from .test_deployed_lambda import _resolve_region, _resolve_function_name


def _is_local_api_running() -> bool:
    """Check if SAM local API is running on localhost:3000."""
    try:
        response = requests.get("http://localhost:3000", timeout=2)
        return response.status_code in [200, 404]  # 404 is fine, means API is running but no root route
    except requests.RequestException:
        return False


def _get_test_api_key() -> str:
    """Get the API key to use for testing."""
    return os.getenv("TEST_API_KEY", "test-api-key-12345")


class TestModeSelector:
    """Base class that determines test execution mode."""
    
    @pytest.fixture(scope="session")
    def test_mode(self) -> str:
        """Determine whether to run tests against local API or deployed Lambda."""
        if _is_local_api_running():
            return "local"
        else:
            return "deployed"
    
    @pytest.fixture(scope="session")
    def api_base_url(self, test_mode) -> Optional[str]:
        """Get base URL for API calls based on test mode."""
        if test_mode == "local":
            return "http://localhost:3000"
        else:
            return None  # Will use Lambda direct invoke
    
    @pytest.fixture(scope="session")
    def lambda_client(self, test_mode):
        """Create Lambda client for deployed mode."""
        if test_mode == "deployed":
            region = _resolve_region()
            return boto3.client("lambda", region_name=region)
        return None
    
    @pytest.fixture(scope="session")
    def function_name(self, test_mode):
        """Get function name for deployed mode."""
        if test_mode == "deployed":
            region = _resolve_region()
            return _resolve_function_name(region)
        return None


class TestAPIEndpoints(TestModeSelector):
    """Test API endpoints in both local and deployed modes."""
    
    def _make_request(self, test_mode, api_base_url, lambda_client, function_name, 
                     method="GET", path="/gearboxes", headers=None, data=None, 
                     query_params=None) -> Dict[str, Any]:
        """Make API request in either local or deployed mode."""
        headers = headers or {}
        
        if test_mode == "local":
            # Use HTTP requests against local SAM API
            url = urljoin(api_base_url, path)
            
            try:
                if method == "GET":
                    response = requests.get(url, headers=headers, params=query_params, timeout=30)
                elif method == "POST":
                    response = requests.post(url, headers=headers, json=data, timeout=30)
                else:
                    raise ValueError(f"Unsupported method: {method}")
                
                return {
                    "statusCode": response.status_code,
                    "headers": dict(response.headers),
                    "body": response.text
                }
            except requests.RequestException as e:
                pytest.fail(f"Local API request failed: {e}")
        
        elif test_mode == "deployed":
            # Use Lambda direct invoke
            payload = {
                "body": json.dumps(data) if data else None,
                "headers": headers,
                "httpMethod": method,
                "path": path,
                "queryStringParameters": query_params,
                "requestContext": {"requestId": f"test-request-{int(time.time())}"}
            }
            
            try:
                response = lambda_client.invoke(
                    FunctionName=function_name,
                    InvocationType="RequestResponse",
                    Payload=json.dumps(payload)
                )
                
                response_payload = json.loads(response["Payload"].read())
                return response_payload
                
            except Exception as e:
                pytest.fail(f"Lambda invocation failed: {e}")
        
        else:
            pytest.fail(f"Unknown test mode: {test_mode}")
    
    def test_get_all_gearboxes(self, test_mode, api_base_url, lambda_client, function_name):
        """Test GET request for all gearboxes."""
        headers = {"x-api-key": _get_test_api_key(), "Content-Type": "application/json"}
        
        response = self._make_request(
            test_mode, api_base_url, lambda_client, function_name,
            method="GET", headers=headers
        )
        
        assert response["statusCode"] == 200
        
        body = json.loads(response["body"])
        assert "message" in body
        assert "gearboxes" in body
        assert "categories" in body
        assert "summary" in body
        
        # Verify response structure
        assert isinstance(body["gearboxes"], list)
        assert isinstance(body["categories"], list)
        assert isinstance(body["summary"], dict)
    
    def test_get_with_category_filter(self, test_mode, api_base_url, lambda_client, function_name):
        """Test GET request with category filter."""
        headers = {"x-api-key": _get_test_api_key(), "Content-Type": "application/json"}
        
        response = self._make_request(
            test_mode, api_base_url, lambda_client, function_name,
            method="GET", headers=headers, query_params={"category": "automotive"}
        )
        
        assert response["statusCode"] == 200
        
        body = json.loads(response["body"])
        assert "category=automotive" in body["message"]
        assert body.get("filters_applied", {}).get("category") == "automotive"
    
    def test_get_with_type_filter(self, test_mode, api_base_url, lambda_client, function_name):
        """Test GET request with type filter."""
        headers = {"x-api-key": _get_test_api_key(), "Content-Type": "application/json"}
        
        response = self._make_request(
            test_mode, api_base_url, lambda_client, function_name,
            method="GET", headers=headers, query_params={"type": "planetary"}
        )
        
        assert response["statusCode"] == 200
        
        body = json.loads(response["body"])
        assert "type=planetary" in body["message"]
        assert body.get("filters_applied", {}).get("type") == "planetary"
    
    def test_get_with_multiple_filters(self, test_mode, api_base_url, lambda_client, function_name):
        """Test GET request with multiple filters."""
        headers = {"x-api-key": _get_test_api_key(), "Content-Type": "application/json"}
        
        response = self._make_request(
            test_mode, api_base_url, lambda_client, function_name,
            method="GET", headers=headers, 
            query_params={"category": "automotive", "min_torque": "1000"}
        )
        
        assert response["statusCode"] == 200
        
        body = json.loads(response["body"])
        assert body.get("filters_applied", {}).get("category") == "automotive"
        assert body.get("filters_applied", {}).get("min_torque") == "1000"
    
    def test_get_without_api_key(self, test_mode, api_base_url, lambda_client, function_name):
        """Test GET request without API key - should work."""
        headers = {"Content-Type": "application/json"}
        
        response = self._make_request(
            test_mode, api_base_url, lambda_client, function_name,
            method="GET", headers=headers
        )
        
        assert response["statusCode"] == 200
        
        body = json.loads(response["body"])
        assert "message" in body
    
    def test_post_create_gearbox(self, test_mode, api_base_url, lambda_client, function_name):
        """Test POST request to create a gearbox."""
        headers = {"x-api-key": _get_test_api_key(), "Content-Type": "application/json"}
        
        test_gearbox_id = f"GB-API-TEST-{int(time.time())}"
        create_data = {
            "operation": "create",
            "gearbox": {
                "gearbox_id": test_gearbox_id,
                "model_name": "API Test Gearbox",
                "manufacturer": "Test Corp",
                "gearbox_type": "planetary",
                "torque_rating": 2000,
                "performance_rating": 75
            },
            "timestamp": "2025-08-17T12:00:00Z"
        }
        
        response = self._make_request(
            test_mode, api_base_url, lambda_client, function_name,
            method="POST", headers=headers, data=create_data
        )
        
        assert response["statusCode"] == 201
        
        body = json.loads(response["body"])
        assert body["gearbox_id"] == test_gearbox_id
        assert "created successfully" in body["message"]
        
        # Clean up - delete the created gearbox
        delete_data = {
            "operation": "delete",
            "gearbox_id": test_gearbox_id
        }
        
        cleanup_response = self._make_request(
            test_mode, api_base_url, lambda_client, function_name,
            method="POST", headers=headers, data=delete_data
        )
        
        # Don't assert on cleanup - it's best effort
        if cleanup_response["statusCode"] != 200:
            print(f"Warning: Failed to clean up test gearbox {test_gearbox_id}")
    
    def test_post_invalid_json(self, test_mode, api_base_url, lambda_client, function_name):
        """Test POST request with invalid JSON."""
        headers = {"x-api-key": _get_test_api_key(), "Content-Type": "application/json"}
        
        if test_mode == "local":
            # For local API, send malformed JSON directly
            try:
                response = requests.post(
                    urljoin(api_base_url, "/gearboxes"), 
                    headers=headers,
                    data='{"invalid": json}',  # Invalid JSON
                    timeout=30
                )
                
                result = {
                    "statusCode": response.status_code,
                    "headers": dict(response.headers),
                    "body": response.text
                }
            except requests.RequestException as e:
                pytest.fail(f"Local API request failed: {e}")
        else:
            # For deployed Lambda, simulate malformed JSON in the event
            payload = {
                "body": '{"invalid": json}',
                "headers": headers,
                "httpMethod": "POST",
                "path": "/gearboxes",
                "queryStringParameters": None,
                "requestContext": {"requestId": "test-invalid-json"}
            }
            
            try:
                response = lambda_client.invoke(
                    FunctionName=function_name,
                    InvocationType="RequestResponse",
                    Payload=json.dumps(payload)
                )
                
                result = json.loads(response["Payload"].read())
            except Exception as e:
                pytest.fail(f"Lambda invocation failed: {e}")
        
        assert result["statusCode"] == 400
        body = json.loads(result["body"])
        assert "error" in body
    
    def test_unsupported_method(self, test_mode, api_base_url, lambda_client, function_name):
        """Test unsupported HTTP method."""
        headers = {"x-api-key": _get_test_api_key(), "Content-Type": "application/json"}
        
        if test_mode == "local":
            try:
                response = requests.delete(
                    urljoin(api_base_url, "/gearboxes"),
                    headers=headers,
                    timeout=30
                )
                
                result = {
                    "statusCode": response.status_code,
                    "body": response.text
                }
            except requests.RequestException as e:
                pytest.fail(f"Local API request failed: {e}")
        else:
            # For deployed Lambda
            payload = {
                "body": None,
                "headers": headers,
                "httpMethod": "DELETE",
                "path": "/gearboxes",
                "queryStringParameters": None,
                "requestContext": {"requestId": "test-unsupported-method"}
            }
            
            try:
                response = lambda_client.invoke(
                    FunctionName=function_name,
                    InvocationType="RequestResponse",
                    Payload=json.dumps(payload)
                )
                
                result = json.loads(response["Payload"].read())
            except Exception as e:
                pytest.fail(f"Lambda invocation failed: {e}")
        
        assert result["statusCode"] == 405
        body = json.loads(result["body"])
        assert "error" in body
    
    def test_api_performance(self, test_mode, api_base_url, lambda_client, function_name):
        """Test API performance in both modes."""
        headers = {"x-api-key": _get_test_api_key(), "Content-Type": "application/json"}
        
        start_time = time.time()
        
        response = self._make_request(
            test_mode, api_base_url, lambda_client, function_name,
            method="GET", headers=headers
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Allow more time for local API due to potential cold starts
        max_duration = 10.0 if test_mode == "local" else 5.0
        assert duration < max_duration, f"API took too long: {duration}s (max: {max_duration}s)"
        
        assert response["statusCode"] == 200
    
    def test_cors_headers(self, test_mode, api_base_url, lambda_client, function_name):
        """Test CORS headers are present."""
        headers = {"x-api-key": _get_test_api_key(), "Content-Type": "application/json"}
        
        response = self._make_request(
            test_mode, api_base_url, lambda_client, function_name,
            method="GET", headers=headers
        )
        
        assert response["statusCode"] == 200
        
        # Check for CORS headers in response
        response_headers = response.get("headers", {})
        
        # Convert header names to lowercase for case-insensitive comparison
        lower_headers = {k.lower(): v for k, v in response_headers.items()}
        
        assert "access-control-allow-origin" in lower_headers
        assert lower_headers["access-control-allow-origin"] == "*"


class TestTestConfiguration:
    """Test the test configuration itself."""
    
    def test_mode_detection(self):
        """Test that test mode detection works correctly."""
        is_local = _is_local_api_running()
        
        if is_local:
            # If local API is running, we should be able to get a response
            try:
                response = requests.get("http://localhost:3000", timeout=2)
                assert response.status_code in [200, 404]
            except requests.RequestException:
                pytest.fail("Local API detected but not responding")
    
    def test_api_key_configuration(self):
        """Test API key configuration."""
        api_key = _get_test_api_key()
        assert isinstance(api_key, str)
        assert len(api_key) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])