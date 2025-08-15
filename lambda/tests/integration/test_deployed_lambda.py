"""
Integration tests for the deployed Lambda function.

AI-generated comment: These tests verify that the Lambda function works correctly
when deployed to AWS. They test the actual deployed function rather than local code,
ensuring that the deployment process and AWS configuration are working properly.
"""

import json
import boto3
import pytest
import os
from typing import Dict, Any


class TestDeployedLambda:
    """Integration tests for the deployed Lambda function."""
    
    @pytest.fixture(scope="class")
    def lambda_client(self):
        """Get AWS Lambda client for testing."""
        return boto3.client('lambda')
    
    @pytest.fixture(scope="class")
    def function_name(self):
        """Get the Lambda function name from environment or use default."""
        return os.getenv('LAMBDA_FUNCTION_NAME', 'product-selector')
    
    def test_lambda_invoke_success(self, lambda_client, function_name):
        """Test direct Lambda invocation with valid payload."""
        payload = {
            "body": json.dumps({"operation": "test", "data": "integration test"}),
            "headers": {
                "x-api-key": "test-api-key-12345",
                "Content-Type": "application/json"
            },
            "httpMethod": "POST",
            "path": "/",
            "requestContext": {
                "requestId": "integration-test-request"
            }
        }
        
        try:
            response = lambda_client.invoke(
                FunctionName=function_name,
                InvocationType='RequestResponse',
                Payload=json.dumps(payload)
            )
            
            # Parse the response
            response_payload = json.loads(response['Payload'].read())
            
            assert response['StatusCode'] == 200
            assert response_payload['statusCode'] == 200
            
            body = json.loads(response_payload['body'])
            assert 'message' in body
            
        except lambda_client.exceptions.ResourceNotFoundException:
            pytest.skip(f"Lambda function '{function_name}' not found - skipping integration test")
        except Exception as e:
            pytest.fail(f"Lambda invocation failed: {e}")
    
    def test_lambda_invoke_missing_api_key(self, lambda_client, function_name):
        """Test Lambda invocation with missing API key."""
        payload = {
            "body": json.dumps({"operation": "test"}),
            "headers": {
                "Content-Type": "application/json"
            },
            "httpMethod": "POST",
            "path": "/",
            "requestContext": {
                "requestId": "integration-test-request"
            }
        }
        
        try:
            response = lambda_client.invoke(
                FunctionName=function_name,
                InvocationType='RequestResponse',
                Payload=json.dumps(payload)
            )
            
            response_payload = json.loads(response['Payload'].read())
            
            assert response['StatusCode'] == 200
            assert response_payload['statusCode'] == 401
            
            body = json.loads(response_payload['body'])
            assert body['error'] == "API key is missing or invalid."
            
        except lambda_client.exceptions.ResourceNotFoundException:
            pytest.skip(f"Lambda function '{function_name}' not found - skipping integration test")
    
    def test_lambda_invoke_malformed_json(self, lambda_client, function_name):
        """Test Lambda invocation with malformed JSON."""
        payload = {
            "body": '{"invalid": json}',
            "headers": {
                "x-api-key": "test-api-key-12345",
                "Content-Type": "application/json"
            },
            "httpMethod": "POST",
            "path": "/",
            "requestContext": {
                "requestId": "integration-test-request"
            }
        }
        
        try:
            response = lambda_client.invoke(
                FunctionName=function_name,
                InvocationType='RequestResponse',
                Payload=json.dumps(payload)
            )
            
            response_payload = json.loads(response['Payload'].read())
            
            assert response['StatusCode'] == 200
            assert response_payload['statusCode'] == 400
            
            body = json.loads(response_payload['body'])
            assert body['error'] == "Invalid JSON in request body."
            
        except lambda_client.exceptions.ResourceNotFoundException:
            pytest.skip(f"Lambda function '{function_name}' not found - skipping integration test")
    
    def test_lambda_performance(self, lambda_client, function_name):
        """Test that Lambda function responds within acceptable time limits."""
        payload = {
            "body": json.dumps({"operation": "performance_test"}),
            "headers": {
                "x-api-key": "test-api-key-12345"
            },
            "httpMethod": "POST",
            "path": "/",
            "requestContext": {
                "requestId": "performance-test-request"
            }
        }
        
        try:
            import time
            start_time = time.time()
            
            response = lambda_client.invoke(
                FunctionName=function_name,
                InvocationType='RequestResponse',
                Payload=json.dumps(payload)
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Function should respond within 5 seconds for this simple operation
            assert duration < 5.0, f"Lambda function took too long: {duration}s"
            
            response_payload = json.loads(response['Payload'].read())
            assert response_payload['statusCode'] == 200
            
        except lambda_client.exceptions.ResourceNotFoundException:
            pytest.skip(f"Lambda function '{function_name}' not found - skipping integration test")


class TestLambdaConfiguration:
    """Test Lambda function configuration and environment."""
    
    @pytest.fixture(scope="class")
    def lambda_client(self):
        """Get AWS Lambda client for testing."""
        return boto3.client('lambda')
    
    @pytest.fixture(scope="class")
    def function_name(self):
        """Get the Lambda function name from environment or use default."""
        return os.getenv('LAMBDA_FUNCTION_NAME', 'product-selector')
    
    def test_lambda_configuration(self, lambda_client, function_name):
        """Test that Lambda function is configured correctly."""
        try:
            response = lambda_client.get_function_configuration(
                FunctionName=function_name
            )
            
            # Check basic configuration
            assert response['Runtime'].startswith('python')
            assert response['Handler'] == 'app.lambda_handler'
            assert response['Timeout'] >= 30  # Should have reasonable timeout
            assert response['MemorySize'] >= 128  # Should have sufficient memory
            
        except lambda_client.exceptions.ResourceNotFoundException:
            pytest.skip(f"Lambda function '{function_name}' not found - skipping configuration test")
    
    def test_lambda_environment_variables(self, lambda_client, function_name):
        """Test Lambda function environment variables (if any)."""
        try:
            response = lambda_client.get_function_configuration(
                FunctionName=function_name
            )
            
            # The simplified function doesn't require specific environment variables
            # but we can verify the environment is set up correctly
            env_vars = response.get('Environment', {}).get('Variables', {})
            
            # This is just a basic check that environment can be accessed
            assert isinstance(env_vars, dict)
            
        except lambda_client.exceptions.ResourceNotFoundException:
            pytest.skip(f"Lambda function '{function_name}' not found - skipping environment test")


if __name__ == "__main__":
    pytest.main([__file__])
