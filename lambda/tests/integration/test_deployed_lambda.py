"""
Integration tests for the deployed Lambda function.

AI-generated comment: These tests verify that the Lambda function works correctly
when deployed to AWS. They dynamically discover the deployed function name and
region so they do not rely on prior environment exports.
"""

import json
import os
from pathlib import Path
from typing import Optional

import boto3
import pytest


def _resolve_region() -> str:
    """Resolve AWS region for tests.

    AI-generated comment: Prefer environment, then `samconfig.toml`, then a sane default.

    Returns:
        The AWS region string.
    """
    # Environment override comes first
    env_region = os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION")
    if env_region:
        return env_region

    # Fall back to reading lambda/samconfig.toml next to this test file
    samconfig_path = Path(__file__).resolve().parents[2] / "samconfig.toml"
    if samconfig_path.exists():
        try:
            import tomllib  # Python 3.11+ standard library

            data = tomllib.loads(samconfig_path.read_text(encoding="utf-8"))
            region = (
                data.get("default", {})
                .get("global", {})
                .get("parameters", {})
                .get("region")
            )
            if isinstance(region, str) and region.strip():
                return region
        except Exception:
            # AI-generated comment: Non-fatal; fall through to default
            pass

    # Final fallback
    return "us-east-1"


def _resolve_stack_name() -> Optional[str]:
    """Resolve the CloudFormation stack name used by SAM deploy.

    AI-generated comment: Use env var first, then `samconfig.toml`. Returns None if unknown.

    Returns:
        The stack name or None.
    """
    env_stack = os.getenv("STACK_NAME") or os.getenv("SAM_STACK_NAME")
    if env_stack:
        return env_stack

    samconfig_path = Path(__file__).resolve().parents[2] / "samconfig.toml"
    if samconfig_path.exists():
        try:
            import tomllib

            data = tomllib.loads(samconfig_path.read_text(encoding="utf-8"))
            # Prefer prod if that is the active env; otherwise default
            prod_stack = (
                data.get("prod", {})
                .get("deploy", {})
                .get("parameters", {})
                .get("stack_name")
            )
            default_stack = (
                data.get("default", {})
                .get("global", {})
                .get("parameters", {})
                .get("stack_name")
            )
            return prod_stack or default_stack
        except Exception:
            return None

    return None


def _resolve_function_name(region_name: str) -> str:
    """Resolve the deployed function's physical name.

    AI-generated comment: Use env `LAMBDA_FUNCTION_NAME` if set; otherwise query
    CloudFormation for the physical resource id of logical resource `ProductSelectorFunction`.

    Args:
        region_name: The AWS region to use for the lookup.

    Returns:
        The deployed Lambda function name.

    Raises:
        AssertionError: If the function name cannot be determined.
    """
    env_name = os.getenv("LAMBDA_FUNCTION_NAME")
    if env_name:
        return env_name

    stack_name = _resolve_stack_name()
    assert (
        stack_name is not None
    ), "STACK_NAME/SAM_STACK_NAME not set and could not parse stack_name from samconfig.toml"

    cfn = boto3.client("cloudformation", region_name=region_name)
    resp = cfn.describe_stack_resources(StackName=stack_name)
    resources = resp.get("StackResources", [])
    for res in resources:
        if res.get("LogicalResourceId") == "ProductSelectorFunction":
            phys = res.get("PhysicalResourceId")
            if isinstance(phys, str) and phys.strip():
                return phys

    raise AssertionError(
        f"Could not resolve PhysicalResourceId for ProductSelectorFunction in stack {stack_name}"
    )


@pytest.fixture(scope="session")
def _region() -> str:
    """Session-scoped region resolved once for all tests."""
    return _resolve_region()


@pytest.fixture(scope="session")
def lambda_client(_region):
    """Create a boto3 Lambda client bound to the resolved region."""
    return boto3.client("lambda", region_name=_region)


@pytest.fixture(scope="session")
def function_name(_region) -> str:
    """Resolve the function name once per session."""
    return _resolve_function_name(_region)


class TestDeployedLambda:
    """Integration tests for the deployed Lambda function."""

    def test_lambda_get_gearboxes(self, lambda_client, function_name):
        """Test GET request to retrieve all gearboxes."""
        payload = {
            "body": None,
            "headers": {"x-api-key": "test-api-key-12345", "Content-Type": "application/json"},
            "httpMethod": "GET",
            "path": "/gearboxes",
            "queryStringParameters": None,
            "requestContext": {"requestId": "integration-test-request"},
        }

        try:
            response = lambda_client.invoke(
                FunctionName=function_name,
                InvocationType="RequestResponse",
                Payload=json.dumps(payload),
            )

            response_payload = json.loads(response["Payload"].read())

            assert response["StatusCode"] == 200
            assert response_payload["statusCode"] == 200

            body = json.loads(response_payload["body"])
            assert "message" in body
            assert "gearboxes" in body or "categories" in body

        except lambda_client.exceptions.ResourceNotFoundException:
            pytest.fail(
                f"Lambda function '{function_name}' not found in region {_resolve_region()} — ensure it is deployed"
            )
        except Exception as e:
            pytest.fail(f"Lambda invocation failed: {e}")

    def test_lambda_get_with_category_filter(self, lambda_client, function_name):
        """Test GET request with category filter."""
        payload = {
            "body": None,
            "headers": {"x-api-key": "test-api-key-12345", "Content-Type": "application/json"},
            "httpMethod": "GET",
            "path": "/gearboxes",
            "queryStringParameters": {"category": "automotive"},
            "requestContext": {"requestId": "integration-test-request"},
        }

        try:
            response = lambda_client.invoke(
                FunctionName=function_name,
                InvocationType="RequestResponse",
                Payload=json.dumps(payload),
            )

            response_payload = json.loads(response["Payload"].read())

            assert response["StatusCode"] == 200
            assert response_payload["statusCode"] == 200

            body = json.loads(response_payload["body"])
            assert "message" in body
            assert "category=automotive" in body["message"]
            assert body.get("filters_applied", {}).get("category") == "automotive"

        except lambda_client.exceptions.ResourceNotFoundException:
            pytest.fail(
                f"Lambda function '{function_name}' not found in region {_resolve_region()} — ensure it is deployed"
            )
        except Exception as e:
            pytest.fail(f"Lambda invocation failed: {e}")

    def test_lambda_get_with_type_filter(self, lambda_client, function_name):
        """Test GET request with gearbox type filter."""
        payload = {
            "body": None,
            "headers": {"x-api-key": "test-api-key-12345", "Content-Type": "application/json"},
            "httpMethod": "GET",
            "path": "/gearboxes",
            "queryStringParameters": {"type": "planetary"},
            "requestContext": {"requestId": "integration-test-request"},
        }

        try:
            response = lambda_client.invoke(
                FunctionName=function_name,
                InvocationType="RequestResponse",
                Payload=json.dumps(payload),
            )

            response_payload = json.loads(response["Payload"].read())

            assert response["StatusCode"] == 200
            assert response_payload["statusCode"] == 200

            body = json.loads(response_payload["body"])
            assert "message" in body
            assert "type=planetary" in body["message"]
            assert body.get("filters_applied", {}).get("type") == "planetary"

        except lambda_client.exceptions.ResourceNotFoundException:
            pytest.fail(
                f"Lambda function '{function_name}' not found in region {_resolve_region()} — ensure it is deployed"
            )
        except Exception as e:
            pytest.fail(f"Lambda invocation failed: {e}")

    def test_lambda_invoke_without_api_key(self, lambda_client, function_name):
        """Test Lambda invocation without API key - should work without authentication."""
        payload = {
            "body": None,
            "headers": {"Content-Type": "application/json"},
            "httpMethod": "GET",
            "path": "/gearboxes",
            "queryStringParameters": None,
            "requestContext": {"requestId": "integration-test-request"},
        }

        try:
            response = lambda_client.invoke(
                FunctionName=function_name,
                InvocationType="RequestResponse",
                Payload=json.dumps(payload),
            )

            response_payload = json.loads(response["Payload"].read())

            assert response["StatusCode"] == 200
            assert response_payload["statusCode"] == 200

            body = json.loads(response_payload["body"])
            assert "message" in body

        except lambda_client.exceptions.ResourceNotFoundException:
            pytest.fail(
                f"Lambda function '{function_name}' not found in region {_resolve_region()} — ensure it is deployed"
            )

    def test_lambda_invoke_malformed_json(self, lambda_client, function_name):
        """Test Lambda invocation with malformed JSON."""
        payload = {
            "body": '{"invalid": json}',
            "headers": {"x-api-key": "test-api-key-12345", "Content-Type": "application/json"},
            "httpMethod": "POST",
            "path": "/gearboxes",
            "queryStringParameters": None,
            "requestContext": {"requestId": "integration-test-request"},
        }

        try:
            response = lambda_client.invoke(
                FunctionName=function_name,
                InvocationType="RequestResponse",
                Payload=json.dumps(payload),
            )

            response_payload = json.loads(response["Payload"].read())

            assert response["StatusCode"] == 200
            assert response_payload["statusCode"] == 400

            body = json.loads(response_payload["body"])
            assert body["error"] == "Invalid JSON in request body."

        except lambda_client.exceptions.ResourceNotFoundException:
            pytest.fail(
                f"Lambda function '{function_name}' not found in region {_resolve_region()} — ensure it is deployed"
            )

    def test_lambda_performance(self, lambda_client, function_name):
        """Test that Lambda function responds within acceptable time limits."""
        payload = {
            "body": None,
            "headers": {"x-api-key": "test-api-key-12345"},
            "httpMethod": "GET",
            "path": "/gearboxes",
            "queryStringParameters": None,
            "requestContext": {"requestId": "performance-test-request"},
        }

        try:
            import time

            start_time = time.time()

            response = lambda_client.invoke(
                FunctionName=function_name,
                InvocationType="RequestResponse",
                Payload=json.dumps(payload),
            )

            end_time = time.time()
            duration = end_time - start_time

            assert duration < 5.0, f"Lambda function took too long: {duration}s"

            response_payload = json.loads(response["Payload"].read())
            assert response_payload["statusCode"] == 200

        except lambda_client.exceptions.ResourceNotFoundException:
            pytest.fail(
                f"Lambda function '{function_name}' not found in region {_resolve_region()} — ensure it is deployed"
            )

    def test_lambda_crud_operations(self, lambda_client, function_name):
        """Test complete CRUD operations on gearbox catalog."""
        test_gearbox_id = "GB-INTEGRATION-TEST-001"
        
        # Test CREATE operation
        create_payload = {
            "body": json.dumps({
                "operation": "create",
                "gearbox": {
                    "gearbox_id": test_gearbox_id,
                    "model_name": "Integration Test Gearbox",
                    "manufacturer": "Test Corp",
                    "gearbox_type": "planetary",
                    "torque_rating": 1000,
                    "performance_rating": 80
                },
                "timestamp": "2025-08-17T12:00:00Z"
            }),
            "headers": {"x-api-key": "test-api-key-12345", "Content-Type": "application/json"},
            "httpMethod": "POST",
            "path": "/gearboxes",
            "queryStringParameters": None,
            "requestContext": {"requestId": "integration-create-request"},
        }

        try:
            # CREATE
            response = lambda_client.invoke(
                FunctionName=function_name,
                InvocationType="RequestResponse",
                Payload=json.dumps(create_payload),
            )
            response_payload = json.loads(response["Payload"].read())
            assert response_payload["statusCode"] == 201

            # UPDATE
            update_payload = {
                "body": json.dumps({
                    "operation": "update",
                    "gearbox_id": test_gearbox_id,
                    "updates": {"torque_rating": 1200, "performance_rating": 85},
                    "timestamp": "2025-08-17T12:05:00Z"
                }),
                "headers": {"x-api-key": "test-api-key-12345", "Content-Type": "application/json"},
                "httpMethod": "POST",
                "path": "/gearboxes",
                "queryStringParameters": None,
                "requestContext": {"requestId": "integration-update-request"},
            }

            response = lambda_client.invoke(
                FunctionName=function_name,
                InvocationType="RequestResponse",
                Payload=json.dumps(update_payload),
            )
            response_payload = json.loads(response["Payload"].read())
            assert response_payload["statusCode"] == 200

            # DELETE
            delete_payload = {
                "body": json.dumps({
                    "operation": "delete",
                    "gearbox_id": test_gearbox_id
                }),
                "headers": {"x-api-key": "test-api-key-12345", "Content-Type": "application/json"},
                "httpMethod": "POST",
                "path": "/gearboxes",
                "queryStringParameters": None,
                "requestContext": {"requestId": "integration-delete-request"},
            }

            response = lambda_client.invoke(
                FunctionName=function_name,
                InvocationType="RequestResponse",
                Payload=json.dumps(delete_payload),
            )
            response_payload = json.loads(response["Payload"].read())
            assert response_payload["statusCode"] == 200

        except lambda_client.exceptions.ResourceNotFoundException:
            pytest.fail(
                f"Lambda function '{function_name}' not found in region {_resolve_region()} — ensure it is deployed"
            )
        except Exception as e:
            pytest.fail(f"CRUD operations test failed: {e}")

    def test_lambda_unsupported_method(self, lambda_client, function_name):
        """Test unsupported HTTP method returns 405."""
        payload = {
            "body": None,
            "headers": {"x-api-key": "test-api-key-12345", "Content-Type": "application/json"},
            "httpMethod": "DELETE",
            "path": "/gearboxes",
            "queryStringParameters": None,
            "requestContext": {"requestId": "integration-method-request"},
        }

        try:
            response = lambda_client.invoke(
                FunctionName=function_name,
                InvocationType="RequestResponse",
                Payload=json.dumps(payload),
            )

            response_payload = json.loads(response["Payload"].read())

            assert response["StatusCode"] == 200
            assert response_payload["statusCode"] == 405

            body = json.loads(response_payload["body"])
            assert "error" in body
            assert "DELETE" in body["error"]

        except lambda_client.exceptions.ResourceNotFoundException:
            pytest.fail(
                f"Lambda function '{function_name}' not found in region {_resolve_region()} — ensure it is deployed"
            )
        except Exception as e:
            pytest.fail(f"Unsupported method test failed: {e}")


class TestLambdaConfiguration:
    """Test Lambda function configuration and environment."""

    def test_lambda_configuration(self, lambda_client, function_name):
        """Test that Lambda function is configured correctly."""
        try:
            response = lambda_client.get_function_configuration(FunctionName=function_name)

            assert response["Runtime"].startswith("python")
            assert response["Handler"] == "app.lambda_handler"
            assert response["Timeout"] >= 30
            assert response["MemorySize"] >= 128

        except lambda_client.exceptions.ResourceNotFoundException:
            pytest.fail(
                f"Lambda function '{function_name}' not found in region {_resolve_region()} — ensure it is deployed"
            )

    def test_lambda_environment_variables(self, lambda_client, function_name):
        """Test Lambda function environment variables (if any)."""
        try:
            response = lambda_client.get_function_configuration(FunctionName=function_name)

            env_vars = response.get("Environment", {}).get("Variables", {})
            assert isinstance(env_vars, dict)

        except lambda_client.exceptions.ResourceNotFoundException:
            pytest.fail(
                f"Lambda function '{function_name}' not found in region {_resolve_region()} — ensure it is deployed"
            )


if __name__ == "__main__":
    pytest.main([__file__])
