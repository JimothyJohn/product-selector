#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "python-dotenv>=1.1.1",
#     "boto3>=1.39.10",
#     "requests>=2.32.4",
#     "httpx>=0.27.0"
# ]
# ///
"""
CLI entry point for datasheetminer.

AI-generated comment: This module provides a command-line interface for the datasheetminer
application, allowing users to run document analysis locally without needing to deploy
to AWS Lambda. It serves as a wrapper around the core analysis functionality and can
be easily extended for MCP (Model Context Protocol) integration.

Usage:
    uv run datasheetminer --prompt "Analyze this document" --url "https://example.com/doc.pdf" --x-api-key $KEYVAR
    uv run datasheetminer --help
"""

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from utils import validate_url, validate_api_key

from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Configure logging for CLI
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_parser() -> argparse.ArgumentParser:
    """
    Create and configure the argument parser for the CLI.

    AI-generated comment: This function centralizes argument configuration and makes
    the CLI definition more maintainable. It replaces Click's decorator-based approach
    with argparse's more explicit configuration while maintaining all the same functionality.

    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        prog="datasheetminer",
        description="Datasheetminer CLI - Analyze PDF documents using Gemini AI.",
        epilog="""
Examples:
  # Basic usage with environment variable
  export GEMINI_API_KEY="your-api-key"
  uv run datasheetminer --prompt "Summarize this document" --url "https://example.com/doc.pdf"

  # Save output to file
  uv run datasheetminer -p "Extract key specifications" -u "https://example.com/spec.pdf" -o analysis.txt

  # Use markdown output format
  uv run datasheetminer -p "Create a technical summary" -u "https://example.com/tech.pdf" -f markdown
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--prompt", "-p", required=True, help="The analysis prompt to send to Gemini AI"
    )

    parser.add_argument(
        "--url",
        "-u",
        required=True,
        type=validate_url,
        help="URL of the PDF document to analyze",
    )

    parser.add_argument(
        "--x-api-key",
        type=validate_api_key,
        default=os.getenv("GEMINI_API_KEY"),
        help="Gemini API key (can also be set via GEMINI_API_KEY environment variable)",
    )

    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Output file path for saving the response (optional)",
    )

    parser.add_argument(
        "--format",
        "-f",
        choices=["text", "json", "markdown"],
        default="text",
        help="Output format for the response",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    parser.add_argument("--version", action="version", version="datasheetminer 0.1.0")

    return parser


def main() -> None:
    """
    Datasheetminer CLI - Analyze PDF documents using Gemini AI.

    AI-generated comment: This is the main CLI function that orchestrates the document
    analysis process. It handles argument parsing, validation, and coordinates the
    analysis workflow while providing user-friendly output and error handling.

    Examples:
        # Basic usage with environment variable
        export GEMINI_API_KEY="your-api-key"
        uv run datasheetminer --prompt "Summarize this document" --url "https://example.com/doc.pdf"

        # Save output to file
        uv run datasheetminer -p "Extract key specifications" -u "https://example.com/spec.pdf" -o analysis.txt

        # Use markdown output format
        uv run datasheetminer -p "Create a technical summary" -u "https://example.com/tech.pdf" -f markdown
    """
    # Parse command line arguments
    parser = create_parser()
    args = parser.parse_args()

    # Validate that API key is provided either via argument or environment variable
    if not args.x_api_key:
        parser.error(
            "API key is required. Provide it via --x-api-key or set GEMINI_API_KEY environment variable."
        )

    # Set logging level based on verbose flag
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    logger.info(f"Starting document analysis for URL: {args.url}")
    logger.info(f"Prompt: {args.prompt}")

    try:
        """
        # AI-generated comment: Process the document analysis and handle the single response.
        # The response is now a single object, not a stream.
        response = analyze_document(args.prompt, args.url, args.x_api_key)

        if not response or not hasattr(response, "text") or not response.text.strip():
            print("No response received from Gemini AI", file=sys.stderr)
            sys.exit(1)

        full_response = response.text
        """
        full_response = "Hello, world!"

        # Format the response based on user preference
        formatted_response = format_response(full_response, args.format)

        # Output the response
        if args.output:
            # Save to file
            args.output.write_text(formatted_response, encoding="utf-8")
            print(f"Response saved to: {args.output}", file=sys.stderr)
        else:
            # Print to stdout
            print(formatted_response)

        logger.info("Document analysis completed successfully")

    except Exception as e:
        logger.error(f"Error during document analysis: {e}")
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def format_response(response: str, format_type: str) -> str:
    """
    Format the response according to the specified output format.

    AI-generated comment: This function provides multiple output formats to make
    the CLI output more flexible and useful for different use cases, including
    integration with other tools and systems.

    Args:
        response: The raw response text from Gemini AI
        format_type: The desired output format ('text', 'json', or 'markdown')

    Returns:
        The formatted response string
    """
    if format_type == "json":
        return json.dumps(
            {"response": response, "status": "success", "timestamp": str(Path().cwd())},
            indent=2,
        )

    elif format_type == "markdown":
        # AI-generated comment: Convert the response to markdown format for
        # better readability and integration with markdown processors.
        return f"# Document Analysis Response\n\n{response}\n\n---\n*Generated by Datasheetminer CLI*"

    else:  # text format (default)
        return response


if __name__ == "__main__":
    # AI-generated comment: This allows the module to be run directly as a script
    # in addition to being imported as a module, providing flexibility for
    # different execution methods.
    main()
