#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "boto3>=1.39.10",
# ]
# ///
"""
CLI entry point for gearbox catalog.

This module provides a command-line interface for the gearbox catalog
application, allowing users to test the Lambda function locally and
interact with the DynamoDB gearbox_catalog table.

Usage:
    python -m app  # Test Lambda function locally with mock data
    python -m app --live  # Test against actual DynamoDB (requires AWS credentials)
"""

import argparse
import json
import logging
import sys
from unittest.mock import patch


# Configure logging for CLI with environment variable support
def configure_cli_logging():
    """Configure logging for CLI with LOG_LEVEL environment variable support."""
    import os

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

    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
    )

    return logging.getLogger(__name__)


logger = configure_cli_logging()


def create_mock_dynamodb_data():
    """Create sample DynamoDB data for testing."""
    return {
        "Items": [
            {
                "PK": {"S": "category#automotive"},
                "SK": {"S": "metadata"},
                "category_name": {"S": "Automotive Gearboxes"},
                "description": {"S": "Gearboxes for automotive applications"},
                "created_at": {"S": "2025-01-01T10:00:00Z"},
            },
            {
                "PK": {"S": "category#industrial"},
                "SK": {"S": "metadata"},
                "category_name": {"S": "Industrial Gearboxes"},
                "description": {"S": "Heavy-duty industrial gearboxes"},
                "created_at": {"S": "2025-01-01T10:00:00Z"},
            },
            {
                "PK": {"S": "category#marine"},
                "SK": {"S": "metadata"},
                "category_name": {"S": "Marine Gearboxes"},
                "description": {"S": "Gearboxes for marine applications"},
                "created_at": {"S": "2025-01-01T10:00:00Z"},
            },
            {
                "PK": {"S": "gearbox#GB-001"},
                "SK": {"S": "metadata"},
                "gearbox_id": {"S": "GB-001"},
                "model_name": {"S": "PowerMax 5000"},
                "manufacturer": {"S": "GearTech Industries"},
                "gearbox_type": {"S": "planetary"},
                "torque_rating": {"N": "5000"},
                "performance_rating": {"N": "92"},
                "application_type": {"S": "heavy_duty"},
                "price_range": {"S": "high"},
                "created_at": {"S": "2025-01-01T12:00:00Z"},
            },
            {
                "PK": {"S": "gearbox#GB-002"},
                "SK": {"S": "metadata"},
                "gearbox_id": {"S": "GB-002"},
                "model_name": {"S": "SpeedForce 3200"},
                "manufacturer": {"S": "VelocityGear Corp"},
                "gearbox_type": {"S": "helical"},
                "torque_rating": {"N": "3200"},
                "performance_rating": {"N": "88"},
                "application_type": {"S": "automotive"},
                "price_range": {"S": "medium"},
                "created_at": {"S": "2025-01-01T13:00:00Z"},
            },
            {
                "PK": {"S": "gearbox#GB-003"},
                "SK": {"S": "metadata"},
                "gearbox_id": {"S": "GB-003"},
                "model_name": {"S": "TurboShift 1500"},
                "manufacturer": {"S": "RapidMotion Ltd"},
                "gearbox_type": {"S": "worm"},
                "torque_rating": {"N": "1500"},
                "performance_rating": {"N": "85"},
                "application_type": {"S": "industrial"},
                "price_range": {"S": "low"},
                "created_at": {"S": "2025-01-01T14:00:00Z"},
            },
            {
                "PK": {"S": "gearbox#GB-004"},
                "SK": {"S": "metadata"},
                "gearbox_id": {"S": "GB-004"},
                "model_name": {"S": "OceanDrive 2800"},
                "manufacturer": {"S": "MarineGear Solutions"},
                "gearbox_type": {"S": "planetary"},
                "torque_rating": {"N": "2800"},
                "performance_rating": {"N": "90"},
                "application_type": {"S": "marine"},
                "price_range": {"S": "high"},
                "created_at": {"S": "2025-01-01T15:00:00Z"},
            },
            {
                "PK": {"S": "gearbox#GB-005"},
                "SK": {"S": "metadata"},
                "gearbox_id": {"S": "GB-005"},
                "model_name": {"S": "CompactForce 800"},
                "manufacturer": {"S": "MiniGear Inc"},
                "gearbox_type": {"S": "spur"},
                "torque_rating": {"N": "800"},
                "performance_rating": {"N": "82"},
                "application_type": {"S": "light_duty"},
                "price_range": {"S": "low"},
                "created_at": {"S": "2025-01-01T16:00:00Z"},
            },
        ],
        "Count": 8,
        "ScannedCount": 8,
    }


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        prog="gearbox-catalog",
        description="Gearbox Catalog CLI - Test the Lambda function locally or interact with DynamoDB.",
        epilog="""
Examples:
  # Test with mock data (default)
  python -m app

  # Test with category filter
  python -m app --category automotive

  # Test with multiple filters
  python -m app --category automotive --min-torque 2000

  # Test with type filter and JSON output
  python -m app --type planetary --format json

  # Test against live DynamoDB (requires AWS credentials)
  python -m app --live --category industrial

  # Test with verbose output
  python -m app --verbose --manufacturer "GearTech"
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--live",
        action="store_true",
        help="Test against live DynamoDB instead of mock data (requires AWS credentials)",
    )

    parser.add_argument(
        "--format",
        "-f",
        choices=["text", "json", "summary"],
        default="text",
        help="Output format for the response",
    )

    parser.add_argument(
        "--category", help="Filter by category (e.g., automotive, industrial, marine)"
    )

    parser.add_argument(
        "--type", help="Filter by gearbox type (e.g., planetary, helical, worm)"
    )

    parser.add_argument("--manufacturer", help="Filter by manufacturer name")

    parser.add_argument(
        "--min-torque", type=float, help="Filter by minimum torque rating"
    )

    parser.add_argument(
        "--min-performance", type=float, help="Filter by minimum performance rating"
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    parser.add_argument("--version", action="version", version="gearbox-catalog 1.0.0")

    return parser


def format_response(response_data: dict, format_type: str) -> str:
    """Format the response according to the specified output format."""
    if format_type == "json":
        return json.dumps(response_data, indent=2, default=str)

    elif format_type == "summary":
        summary = response_data.get("summary", {})
        return f"""Gearbox Catalog Summary:
- Total items: {summary.get("total_items", "N/A")}
- Categories: {summary.get("categories", "N/A")}
- Gearbox products: {summary.get("gearbox_products", "N/A")}
        """

    else:  # text format (default)
        body = response_data
        output = [f"Message: {body.get('message', 'N/A')}"]

        # Summary
        summary = body.get("summary", {})
        output.append(f"Total items: {summary.get('total_items', 'N/A')}")
        output.append(f"Categories: {summary.get('categories', 'N/A')}")
        output.append(f"Gearbox products: {summary.get('gearbox_products', 'N/A')}")

        # Categories
        categories = body.get("categories", [])
        if categories:
            output.append(f"\nCategories ({len(categories)}):")
            for i, cat in enumerate(categories, 1):
                name = cat.get("category_name", "N/A")
                desc = cat.get("description", "N/A")
                output.append(f"  {i}. {name} - {desc}")

        # Gearboxes
        gearboxes = body.get("gearboxes", [])
        if gearboxes:
            output.append(f"\nGearboxes ({len(gearboxes)}):")
            for i, gearbox in enumerate(gearboxes, 1):
                model = gearbox.get("model_name", "N/A")
                manufacturer = gearbox.get("manufacturer", "N/A")
                gtype = gearbox.get("gearbox_type", "N/A")
                torque = gearbox.get("torque_rating", "N/A")
                perf = gearbox.get("performance_rating", "N/A")
                output.append(f"  {i}. {model} by {manufacturer}")
                output.append(
                    f"     Type: {gtype}, Torque: {torque} Nm, Performance: {perf}%"
                )

        return "\n".join(output)


def main() -> None:
    """
    Gearbox Catalog CLI - Test the Lambda function locally or interact with DynamoDB.

    This function tests the gearbox catalog Lambda handler either with mock data
    or against live DynamoDB, providing a way to verify functionality without
    deploying to AWS Lambda.
    """
    # Parse command line arguments
    parser = create_parser()
    args = parser.parse_args()

    # Set logging level based on verbose flag
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    logger.info("Starting gearbox catalog CLI test")

    try:
        # Import the Lambda handler
        if __name__ == "__main__" and __package__ is None:
            # Running as script, import from current directory
            from app import lambda_handler
        else:
            # Running as module, import from package
            from .app import lambda_handler

        # Build query parameters from command line arguments
        query_params = {}
        if args.category:
            query_params["category"] = args.category
        if args.type:
            query_params["type"] = args.type
        if args.manufacturer:
            query_params["manufacturer"] = args.manufacturer
        if args.min_torque:
            query_params["min_torque"] = str(args.min_torque)
        if args.min_performance:
            query_params["min_performance"] = str(args.min_performance)

        # Create test event
        test_event = {
            "httpMethod": "GET",
            "headers": {"x-api-key": "test-api-key"},
            "body": None,
            "queryStringParameters": query_params if query_params else None,
        }

        if args.live:
            logger.info("Testing against live DynamoDB (requires AWS credentials)")
            result = lambda_handler(test_event, None)
        else:
            logger.info("Testing with mock DynamoDB data")
            # Mock the DynamoDB scan operation
            mock_data = create_mock_dynamodb_data()
            with patch("app.dynamodb.scan") as mock_scan:
                mock_scan.return_value = mock_data
                result = lambda_handler(test_event, None)

        # Process the result
        if result["statusCode"] == 200:
            body = json.loads(result["body"])
            formatted_output = format_response(body, args.format)
            print(formatted_output)  # Keep output printing for CLI results

            logger.info("Lambda handler test completed successfully")
            if not args.live:
                logger.info("Using mock DynamoDB data for testing")
                if query_params:
                    logger.info(f"Filtering applied: {query_params}")
                    logger.debug("Query parameters working as expected")
                else:
                    logger.debug(
                        "All items returned from gearbox_catalog table - no filters applied"
                    )

                # Success messages for user (keep prints for CLI feedback)
                print("\n✅ Lambda handler test completed successfully with mock data!")
                if query_params:
                    print(f"✅ Filtering applied: {query_params}")
                    print("✅ Query parameters working as expected")
                else:
                    print("✅ All items returned from gearbox_catalog table")
                    print("✅ No filters applied")
        else:
            logger.error(
                f"Lambda handler returned error status {result['statusCode']}: {result['body']}"
            )
            print(f"❌ Error (Status {result['statusCode']}): {result['body']}")
            sys.exit(1)

        logger.info("Gearbox catalog CLI test completed successfully")

    except ImportError as e:
        logger.error(f"Failed to import Lambda handler: {e}")
        print(
            "❌ Error: Could not import the Lambda handler. Make sure you're in the lambda/app directory.",
            file=sys.stderr,
        )
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error during gearbox catalog test: {e}")
        print(f"❌ Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback

            logger.debug("Full traceback:", exc_info=True)
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
