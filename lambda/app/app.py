"""
DynamoDB Gearbox Catalog Lambda handler.

This module provides API endpoints for retrieving items from the gearbox_catalog
DynamoDB table in us-east-1. It supports filtering by categories and other parameters
via query parameters, or returns all items if no filters are specified.

The lambda_handler function takes two arguments:
    - event: The event object from the API Gateway
    - context: The context object from the API Gateway
"""

import json
import logging
import os
import boto3
from botocore.exceptions import ClientError
from typing import Dict, Any, List, Optional


# Configure logging with environment variable support
def configure_logging():
    """Configure logging with environment variable support for LOG_LEVEL."""
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    # Map string levels to logging constants
    level_mapping = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }

    # Get the numeric level, default to INFO if invalid
    numeric_level = level_mapping.get(log_level, logging.INFO)

    logger = logging.getLogger()
    logger.setLevel(numeric_level)

    # Create formatter for better log messages
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
    )

    # Update existing handlers or create new one
    if logger.handlers:
        for handler in logger.handlers:
            handler.setFormatter(formatter)
    else:
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


# Configure logging
logger = configure_logging()
logger.info(f"Logging configured with level: {os.getenv('LOG_LEVEL', 'INFO')}")

# AI-generated comment: Initialize DynamoDB client for table operations
dynamodb = boto3.client("dynamodb")
TABLE_NAME = "gearbox_catalog"


def get_all_gearboxes() -> List[Dict[str, Any]]:
    """
    Retrieve all gearbox items from the DynamoDB table.

    AI-generated comment: This function scans the entire gearbox_catalog table
    and formats the DynamoDB response into a more readable JSON structure.
    It handles pagination automatically by continuing to scan if there are more items.

    Returns:
        List[Dict[str, Any]]: List of gearbox items with simplified attribute structure

    Raises:
        ClientError: If DynamoDB operation fails
    """
    try:
        items = []
        scan_kwargs = {"TableName": TABLE_NAME}

        # AI-generated comment: Handle pagination by continuing to scan
        # until all items are retrieved from the table
        while True:
            response = dynamodb.scan(**scan_kwargs)
            items.extend(response.get("Items", []))

            # Check if there are more items to scan
            if "LastEvaluatedKey" not in response:
                break
            scan_kwargs["ExclusiveStartKey"] = response["LastEvaluatedKey"]

        # AI-generated comment: Convert DynamoDB format to simplified JSON
        simplified_items = []
        for item in items:
            simplified_item = {}
            for key, value in item.items():
                simplified_item[key] = _convert_dynamodb_item(value)
            simplified_items.append(simplified_item)

        return simplified_items

    except ClientError as e:
        logger.error(f"Failed to scan gearbox_catalog table: {e}")
        raise


def _convert_dynamodb_item(value: Dict[str, Any]) -> Any:
    """
    Convert DynamoDB attribute value format to standard Python types.

    AI-generated comment: DynamoDB returns items in a specific format with type
    indicators (S for string, N for number, etc.). This function recursively
    converts these to standard Python types for easier JSON serialization.

    Args:
        value (Dict[str, Any]): DynamoDB attribute value with type indicator

    Returns:
        Any: Converted value in standard Python type
    """
    if "S" in value:
        return value["S"]
    elif "N" in value:
        # AI-generated comment: Convert string numbers to appropriate numeric type
        num_str = value["N"]
        return int(num_str) if "." not in num_str else float(num_str)
    elif "BOOL" in value:
        return value["BOOL"]
    elif "NULL" in value:
        return None
    elif "L" in value:
        # AI-generated comment: Handle list type by recursively converting items
        return [_convert_dynamodb_item(item) for item in value["L"]]
    elif "M" in value:
        # AI-generated comment: Handle map/dict type by recursively converting values
        return {k: _convert_dynamodb_item(v) for k, v in value["M"].items()}
    elif "SS" in value:
        return list(value["SS"])
    elif "NS" in value:
        return [int(n) if "." not in n else float(n) for n in value["NS"]]
    elif "BS" in value:
        return list(value["BS"])
    else:
        # AI-generated comment: Return raw value if type is not recognized
        return value


def filter_items(
    items: List[Dict[str, Any]], filters: Dict[str, str]
) -> List[Dict[str, Any]]:
    """
    Filter items based on provided filter criteria.

    Args:
        items: List of items to filter
        filters: Dictionary of filter criteria (e.g., {'category': 'automotive'})

    Returns:
        Filtered list of items
    """
    if not filters:
        return items

    filtered_items = []

    for item in items:
        include_item = True

        # Category filter - matches category name in PK
        if "category" in filters:
            category_filter = filters["category"].lower()
            pk = item.get("PK", "").lower()

            # For category items, check if PK contains the category
            if pk.startswith("category#"):
                if category_filter not in pk:
                    include_item = False
            # For gearbox items, check application_type or other category-related fields
            elif pk.startswith("gearbox#"):
                app_type = item.get("application_type", "").lower()
                gearbox_type = item.get("gearbox_type", "").lower()
                if (
                    category_filter not in app_type
                    and category_filter not in gearbox_type
                ):
                    include_item = False

        # Gearbox type filter
        if "type" in filters and include_item:
            type_filter = filters["type"].lower()
            gearbox_type = item.get("gearbox_type", "").lower()
            if type_filter != gearbox_type:
                include_item = False

        # Manufacturer filter
        if "manufacturer" in filters and include_item:
            manufacturer_filter = filters["manufacturer"].lower()
            manufacturer = item.get("manufacturer", "").lower()
            if manufacturer_filter not in manufacturer:
                include_item = False

        # Price range filter
        if "price_range" in filters and include_item:
            price_filter = filters["price_range"].lower()
            price_range = item.get("price_range", "").lower()
            if price_filter != price_range:
                include_item = False

        # Torque rating filter (minimum torque)
        if "min_torque" in filters and include_item:
            try:
                min_torque = float(filters["min_torque"])
                item_torque = float(item.get("torque_rating", 0))
                if item_torque < min_torque:
                    include_item = False
            except (ValueError, TypeError):
                # Skip invalid torque values
                pass

        # Performance rating filter (minimum performance)
        if "min_performance" in filters and include_item:
            try:
                min_perf = float(filters["min_performance"])
                item_perf = float(item.get("performance_rating", 0))
                if item_perf < min_perf:
                    include_item = False
            except (ValueError, TypeError):
                # Skip invalid performance values
                pass

        if include_item:
            filtered_items.append(item)

    return filtered_items


def lambda_handler(event, context) -> dict:
    """
    Handles incoming API requests for gearbox catalog operations.

    Supports filtering by query parameters or returns all items from the gearbox_catalog DynamoDB table.
    Supported filters: category, type, manufacturer, price_range, min_torque, min_performance.

    Args:
        event (dict): The event object from API Gateway.
        context: The context object from API Gateway.

    Returns:
        dict: Standard API Gateway response format with statusCode, headers, and body.
    """
    logger.info(f"Received event: {json.dumps(event)}")

    try:
        # Extract request information
        headers = event.get("headers", {})
        http_method = event.get("httpMethod", "GET")
        body_raw = event.get("body", "{}")
        body = json.loads(body_raw) if isinstance(body_raw, str) and body_raw else {}

        # AI-generated comment: Optional API key validation - log if missing but don't block
        api_key = headers.get("x-api-key")
        if not api_key or not api_key.strip():
            logger.info(
                "API key not provided in 'x-api-key' header - proceeding without authentication."
            )

        # AI-generated comment: Route requests based on HTTP method
        if http_method == "GET":
            # Extract query parameters for filtering
            query_params = event.get("queryStringParameters") or {}

            if query_params:
                logger.info(f"Fetching filtered items with parameters: {query_params}")
                message_suffix = f" (Filtered by: {', '.join(f'{k}={v}' for k, v in query_params.items())})"
            else:
                logger.info("Fetching all items from gearbox_catalog table")
                message_suffix = " - All Items"

            # Get all items from DynamoDB
            all_items = get_all_gearboxes()

            # Apply filters if any
            filtered_items = filter_items(all_items, query_params)

            # AI-generated comment: Separate items by type for better organization
            categories = []
            gearbox_items = []

            for item in filtered_items:
                if item.get("PK", "").startswith("category#"):
                    categories.append(item)
                elif item.get("PK", "").startswith("gearbox#"):
                    gearbox_items.append(item)

            result = {
                "message": f"Gearbox Catalog{message_suffix}",
                "filters_applied": query_params if query_params else None,
                "summary": {
                    "total_items": len(filtered_items),
                    "categories": len(categories),
                    "gearbox_products": len(gearbox_items),
                },
                "categories": categories,
                "gearboxes": gearbox_items,
            }

            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type,Authorization,x-api-key",
                },
                "body": json.dumps(result, default=str),
            }

        elif http_method == "POST":
            # AI-generated comment: Handle POST requests for creating new gearbox entries
            if not body:
                return {
                    "statusCode": 400,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps(
                        {"error": "Request body is required for POST operations"}
                    ),
                }

            operation = body.get("operation", "create")

            if operation == "create":
                return create_gearbox(body)
            elif operation == "update":
                return update_gearbox(body)
            elif operation == "delete":
                return delete_gearbox(body)
            else:
                return {
                    "statusCode": 400,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps({"error": f"Unknown operation: {operation}"}),
                }

        else:
            return {
                "statusCode": 405,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": f"Method {http_method} not allowed"}),
            }

    except ClientError as e:
        logger.error(f"DynamoDB error: {e}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Database operation failed"}),
        }

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in request body: {e}")
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Invalid JSON in request body."}),
        }

    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Internal server error."}),
        }


def create_gearbox(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new gearbox entry in the catalog.

    AI-generated comment: This function creates a new gearbox item with proper
    primary key generation and validation. It uses put_item with condition
    expression to prevent overwriting existing items.

    Args:
        data (Dict[str, Any]): The request data containing gearbox details

    Returns:
        Dict[str, Any]: Standard API Gateway response
    """
    try:
        # AI-generated comment: Extract and validate required fields
        gearbox_data = data.get("gearbox", {})
        required_fields = ["gearbox_id", "model_name", "manufacturer", "gearbox_type"]

        for field in required_fields:
            if not gearbox_data.get(field):
                return {
                    "statusCode": 400,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps({"error": f"Missing required field: {field}"}),
                }

        # AI-generated comment: Construct DynamoDB item with proper attribute types
        item = {
            "PK": {"S": f"gearbox#{gearbox_data['gearbox_id']}"},
            "SK": {"S": "metadata"},
            "gearbox_id": {"S": gearbox_data["gearbox_id"]},
            "model_name": {"S": gearbox_data["model_name"]},
            "manufacturer": {"S": gearbox_data["manufacturer"]},
            "gearbox_type": {"S": gearbox_data["gearbox_type"]},
            "created_at": {"S": data.get("timestamp", "2025-01-14T17:00:00Z")},
        }

        # AI-generated comment: Add optional fields if provided
        if "torque_rating" in gearbox_data:
            item["torque_rating"] = {"N": str(gearbox_data["torque_rating"])}
        if "performance_rating" in gearbox_data:
            item["performance_rating"] = {"N": str(gearbox_data["performance_rating"])}
        if "application_type" in gearbox_data:
            item["application_type"] = {"S": gearbox_data["application_type"]}
        if "price_range" in gearbox_data:
            item["price_range"] = {"S": gearbox_data["price_range"]}

        # AI-generated comment: Use condition expression to prevent overwrites
        dynamodb.put_item(
            TableName=TABLE_NAME,
            Item=item,
            ConditionExpression="attribute_not_exists(PK)",
        )

        return {
            "statusCode": 201,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps(
                {
                    "message": "Gearbox created successfully",
                    "gearbox_id": gearbox_data["gearbox_id"],
                }
            ),
        }

    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "ConditionalCheckFailedException":
            return {
                "statusCode": 409,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Gearbox with this ID already exists"}),
            }
        else:
            logger.error(f"DynamoDB error during create: {e}")
            return {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Failed to create gearbox"}),
            }
    except Exception as e:
        logger.error(f"Unexpected error during create: {e}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Internal server error"}),
        }


def update_gearbox(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update an existing gearbox entry.

    AI-generated comment: This function updates specific attributes of an existing
    gearbox while preserving other fields. It uses update_item with condition
    expression to ensure the item exists before updating.

    Args:
        data (Dict[str, Any]): The request data containing gearbox ID and updates

    Returns:
        Dict[str, Any]: Standard API Gateway response
    """
    try:
        gearbox_id = data.get("gearbox_id")
        updates = data.get("updates", {})

        if not gearbox_id:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "gearbox_id is required for updates"}),
            }

        if not updates:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "No updates provided"}),
            }

        # AI-generated comment: Build update expression dynamically
        update_expressions = []
        expression_values = {}
        expression_names = {}

        for field, value in updates.items():
            if field in ["PK", "SK", "gearbox_id"]:  # Don't allow key updates
                continue

            attr_name = f"#{field}"
            attr_value = f":{field}"
            update_expressions.append(f"{attr_name} = {attr_value}")
            expression_names[attr_name] = field

            # AI-generated comment: Determine correct DynamoDB type
            if isinstance(value, (int, float)):
                expression_values[attr_value] = {"N": str(value)}
            else:
                expression_values[attr_value] = {"S": str(value)}

        if not update_expressions:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "No valid fields to update"}),
            }

        # Add updated timestamp
        update_expressions.append("#updated_at = :updated_at")
        expression_names["#updated_at"] = "updated_at"
        expression_values[":updated_at"] = {
            "S": data.get("timestamp", "2025-01-14T17:00:00Z")
        }

        dynamodb.update_item(
            TableName=TABLE_NAME,
            Key={"PK": {"S": f"gearbox#{gearbox_id}"}, "SK": {"S": "metadata"}},
            UpdateExpression=f"SET {', '.join(update_expressions)}",
            ExpressionAttributeNames=expression_names,
            ExpressionAttributeValues=expression_values,
            ConditionExpression="attribute_exists(PK)",
        )

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps(
                {
                    "message": "Gearbox updated successfully",
                    "gearbox_id": gearbox_id,
                    "updated_fields": list(updates.keys()),
                }
            ),
        }

    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "ConditionalCheckFailedException":
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Gearbox not found"}),
            }
        else:
            logger.error(f"DynamoDB error during update: {e}")
            return {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Failed to update gearbox"}),
            }
    except Exception as e:
        logger.error(f"Unexpected error during update: {e}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Internal server error"}),
        }


def delete_gearbox(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Delete a gearbox entry from the catalog.

    AI-generated comment: This function safely deletes a gearbox item using
    condition expression to ensure the item exists before deletion.

    Args:
        data (Dict[str, Any]): The request data containing gearbox ID

    Returns:
        Dict[str, Any]: Standard API Gateway response
    """
    try:
        gearbox_id = data.get("gearbox_id")

        if not gearbox_id:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "gearbox_id is required for deletion"}),
            }

        dynamodb.delete_item(
            TableName=TABLE_NAME,
            Key={"PK": {"S": f"gearbox#{gearbox_id}"}, "SK": {"S": "metadata"}},
            ConditionExpression="attribute_exists(PK)",
        )

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps(
                {"message": "Gearbox deleted successfully", "gearbox_id": gearbox_id}
            ),
        }

    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "ConditionalCheckFailedException":
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Gearbox not found"}),
            }
        else:
            logger.error(f"DynamoDB error during delete: {e}")
            return {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Failed to delete gearbox"}),
            }
    except Exception as e:
        logger.error(f"Unexpected error during delete: {e}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Internal server error"}),
        }
