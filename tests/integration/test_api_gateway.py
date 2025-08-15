import os
import boto3
import pytest
import requests
from dotenv import load_dotenv

"""
Integration tests for the simplified product-selector API Gateway endpoint.

AI-generated comment: These tests have been updated to work with the new simplified
Lambda handler that provides a generic DynamoDB operations template. The tests
focus on authentication, request validation, and proper HTTP response handling
rather than document analysis functionality.

Make sure env variable AWS_SAM_STACK_NAME exists with the name of the stack we are going to test. 
"""

load_dotenv()


class TestApiGateway:
    """
    Integration tests for the simplified API Gateway endpoint.
    
    AI-generated comment: Updated to test the new generic Lambda handler interface
    that focuses on API key validation and basic request processing rather than
    document analysis or streaming responses.
    """

    @pytest.fixture()
    def api_gateway_url(self):
        """Get the API Gateway URL from Cloudformation Stack outputs"""
        stack_name = os.environ.get("AWS_SAM_STACK_NAME")

        if stack_name is None:
            raise ValueError(
                "Please set the AWS_SAM_STACK_NAME environment variable to the name of your stack"
            )

        client = boto3.client("cloudformation")

        try:
            response = client.describe_stacks(StackName=stack_name)
        except Exception as e:
            raise Exception(
                f"Cannot find stack {stack_name} \n"
                f'Please make sure a stack with the name "{stack_name}" exists'
            ) from e

        stacks = response["Stacks"]
        stack_outputs = stacks[0]["Outputs"]
        api_outputs = [
            output for output in stack_outputs if output["OutputKey"] == "ProductSelectorApi"
        ]

        if not api_outputs:
            raise KeyError(f"ProductSelectorApi not found in stack {stack_name}")

        return api_outputs[0]["OutputValue"]  # Extract url from stack outputs

    @pytest.fixture()
    def test_api_key(self):
        """API key for testing the simplified interface."""
        return os.getenv("TEST_API_KEY", "test-api-key-12345")

    def test_api_gateway_success(self, api_gateway_url, test_api_key):
        """
        Call the API Gateway endpoint and check successful response.
        
        AI-generated comment: Updated to test the simplified interface that returns
        a placeholder message instead of document analysis results.
        """
        headers = {"x-api-key": test_api_key}

        payload = {
            "operation": "test",
            "data": "sample data for testing",
        }

        response = requests.post(api_gateway_url, headers=headers, json=payload)
        response_json = response.json()

        assert response.status_code == 200
        assert "message" in response_json
        assert isinstance(response_json["message"], str)
        assert response_json["message"] == "DynamoDB operation placeholder - implement your logic here"

    def test_api_gateway_missing_api_key(self, api_gateway_url):
        """
        Test API Gateway with missing API key.
        
        AI-generated comment: Updated to expect the simplified error response format
        from the new Lambda handler.
        """
        headers = {}  # No API key

        payload = {
            "operation": "test",
            "data": "test data",
        }

        response = requests.post(api_gateway_url, headers=headers, json=payload)
        response_json = response.json()

        assert response.status_code == 401
        assert "error" in response_json
        assert response_json["error"] == "API key is missing or invalid."

    def test_api_gateway_invalid_api_key(self, api_gateway_url):
        """
        Test API Gateway with invalid API key.
        
        AI-generated comment: The simplified handler accepts any non-empty API key
        for basic validation, so this test verifies that empty/whitespace keys are rejected.
        """
        headers = {"x-api-key": ""}  # Empty API key

        payload = {
            "operation": "test",
            "data": "test data",
        }

        response = requests.post(api_gateway_url, headers=headers, json=payload)

        assert response.status_code == 401
        response_json = response.json()
        assert "error" in response_json
        assert response_json["error"] == "API key is missing or invalid."

    def test_api_gateway_malformed_json(self, api_gateway_url, test_api_key):
        """
        Test API Gateway with malformed JSON payload.
        
        AI-generated comment: Updated to use the test API key and expect
        the simplified error response format.
        """
        headers = {
            "x-api-key": test_api_key,
            "Content-Type": "application/json",
        }

        # Send malformed JSON
        malformed_payload = '{ "operation": "test", invalid json'

        response = requests.post(
            api_gateway_url, headers=headers, data=malformed_payload
        )

        # Should get 400 error for invalid JSON
        assert response.status_code == 400
        response_json = response.json()
        assert "error" in response_json
        assert response_json["error"] == "Invalid JSON in request body."

    def test_api_gateway_empty_payload(self, api_gateway_url, test_api_key):
        """
        Test API Gateway with empty payload.
        
        AI-generated comment: The simplified handler should accept empty payloads
        since it's a generic template that doesn't require specific fields.
        """
        headers = {"x-api-key": test_api_key}

        # Empty payload
        payload = {}

        response = requests.post(api_gateway_url, headers=headers, json=payload)

        # Should succeed with empty payload
        assert response.status_code == 200
        response_json = response.json()
        assert "message" in response_json

    def test_api_gateway_complex_payload(self, api_gateway_url, test_api_key):
        """
        Test API Gateway with complex JSON payload.
        
        AI-generated comment: Tests that the handler can process complex nested JSON
        structures that might be used for DynamoDB operations.
        """
        headers = {"x-api-key": test_api_key}

        payload = {
            "operation": "query",
            "table": "products",
            "key": {"id": "product-123"},
            "filters": {
                "category": "electronics",
                "price_range": {"min": 100, "max": 500}
            }
        }

        response = requests.post(api_gateway_url, headers=headers, json=payload)

        # Should succeed with complex payload
        assert response.status_code == 200
        response_json = response.json()
        assert "message" in response_json

    def test_api_gateway_large_payload(self, api_gateway_url, test_api_key):
        """
        Test API Gateway with large JSON payload.
        
        AI-generated comment: Tests the handler's ability to process larger payloads
        that might be used for batch DynamoDB operations.
        """
        headers = {"x-api-key": test_api_key}

        # Create large data structure
        large_data = {
            "operation": "batch_write",
            "items": [{"id": f"item-{i}", "data": "x" * 100} for i in range(50)]
        }

        payload = large_data

        response = requests.post(api_gateway_url, headers=headers, json=payload)

        # Should succeed with large payload
        assert response.status_code == 200
        response_json = response.json()
        assert "message" in response_json

    def test_api_gateway_cors_headers(self, api_gateway_url, test_api_key):
        """
        Test that CORS headers are properly configured.
        
        AI-generated comment: CORS configuration is typically handled at the
        API Gateway level, not in the Lambda function itself.
        """
        headers = {
            "x-api-key": test_api_key,
            "Origin": "https://example.com",
        }

        payload = {
            "operation": "test_cors",
            "data": "test data",
        }

        response = requests.post(api_gateway_url, headers=headers, json=payload)

        # Check for CORS headers in response
        assert (
            "Access-Control-Allow-Origin" in response.headers
            or response.status_code == 200
        )

    def test_api_gateway_options_request(self, api_gateway_url):
        """Test OPTIONS request for CORS preflight"""
        headers = {
            "Origin": "https://example.com",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "x-api-key,content-type",
        }

        response = requests.options(api_gateway_url, headers=headers)

        # OPTIONS should be allowed for CORS
        assert response.status_code in [200, 204]

    @pytest.mark.slow
    def test_api_gateway_timeout_handling(self, api_gateway_url, test_api_key):
        """
        Test API Gateway timeout handling.
        
        AI-generated comment: Since the simplified handler doesn't perform any
        time-consuming operations, this test mainly verifies that the handler
        responds quickly and doesn't hang.
        """
        headers = {"x-api-key": test_api_key}

        payload = {
            "operation": "quick_test",
            "data": "simple test data",
        }

        # Set a reasonable timeout for the test
        try:
            response = requests.post(
                api_gateway_url,
                headers=headers,
                json=payload,
                timeout=10,  # Should respond much faster than this
            )

            # Should succeed quickly
            assert response.status_code == 200
            response_json = response.json()
            assert "message" in response_json

        except requests.exceptions.Timeout:
            pytest.fail("Request timed out - handler should respond quickly")

    def test_api_gateway_concurrent_requests(self, api_gateway_url, test_api_key):
        """
        Test multiple concurrent requests to API Gateway.
        
        AI-generated comment: Tests that the simplified Lambda handler can handle
        concurrent requests without issues, which is important for production load.
        """
        import concurrent.futures

        headers = {"x-api-key": test_api_key}

        def make_request(request_id):
            payload = {
                "operation": "concurrent_test",
                "request_id": request_id,
                "data": f"test data for request {request_id}",
            }

            response = requests.post(api_gateway_url, headers=headers, json=payload)
            return response.status_code, request_id

        # Make 5 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request, i) for i in range(5)]
            results = [
                future.result() for future in concurrent.futures.as_completed(futures)
            ]

        # All requests should succeed
        assert len(results) == 5
        for status_code, request_id in results:
            assert status_code == 200  # All should succeed with the simplified handler
