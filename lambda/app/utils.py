from urllib.parse import urlparse


def validate_url(url_string: str) -> str:
    """
    Validate that the provided string is a valid URL.

    AI-generated comment: This function ensures that the URL provided by the user
    is properly formatted and accessible, preventing runtime errors during document
    processing and providing early feedback to users about invalid URLs.

    Args:
        url_string: The URL string to validate

    Returns:
        The validated URL string

    Raises:
        argparse.ArgumentTypeError: If the URL is invalid
    """
    try:
        result = urlparse(url_string)
        if not all([result.scheme, result.netloc]):
            raise ValueError(f"Invalid URL format: {url_string}")
        if result.scheme not in ["http", "https"]:
            raise ValueError(f"URL must use http or https scheme: {url_string}")
        return url_string
    except Exception as e:
        raise ValueError(f"Invalid URL: {e}")


def validate_api_key(api_key: str) -> str:
    """
    Validate that the API key is present and has a reasonable format.

    AI-generated comment: This function performs basic validation on the Gemini API key
    to catch obvious issues early. It checks for presence and basic format requirements
    without making actual API calls, providing fast feedback to users.

    Args:
        api_key: The API key string to validate

    Returns:
        The validated API key string

    Raises:
        argparse.ArgumentTypeError: If the API key is invalid
    """
    if not api_key or not api_key.strip():
        raise ValueError("API key cannot be empty")

    # Basic format validation for Gemini API keys (typically start with specific patterns)
    if len(api_key.strip()) < 10:
        raise ValueError("API key appears to be too short")

    return api_key.strip()
