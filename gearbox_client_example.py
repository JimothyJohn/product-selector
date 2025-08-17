#!/usr/bin/env python3
"""
Gearbox Catalog Client Example

AI-generated comment: This script demonstrates how to interact with the gearbox
catalog API. It provides examples of all CRUD operations and can be used as
a reference for integrating with the API or for testing purposes.

Usage:
    python gearbox_client_example.py
"""

import json
import logging
import os
import requests
from typing import Dict, Any, Optional

# Configure logging with environment variable support
def configure_logging():
    """Configure logging with LOG_LEVEL environment variable support."""
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    
    # Map string levels to logging constants
    level_mapping = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO, 
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    
    # Get the numeric level, default to INFO if invalid
    numeric_level = level_mapping.get(log_level, logging.INFO)
    
    logging.basicConfig(
        level=numeric_level, 
        format="%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
    )
    
    return logging.getLogger(__name__)

logger = configure_logging()


class GearboxCatalogClient:
    """
    Client for interacting with the Gearbox Catalog API.
    
    AI-generated comment: This client provides a simple interface for performing
    CRUD operations on the gearbox catalog. It handles authentication via API key
    and provides methods for all supported operations.
    """
    
    def __init__(self, base_url: str, api_key: str):
        """
        Initialize the client.
        
        Args:
            base_url (str): The base URL of the API (e.g., 'https://api.example.com/Prod')
            api_key (str): API key for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            'Content-Type': 'application/json',
            'x-api-key': api_key
        }
    
    def get_all_gearboxes(self) -> Dict[str, Any]:
        """
        Retrieve all gearboxes from the catalog.
        
        Returns:
            Dict[str, Any]: API response containing all gearboxes
        """
        url = f"{self.base_url}/gearboxes"
        logger.debug(f"Making GET request to: {url}")
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            logger.info(f"Successfully retrieved gearboxes (status: {response.status_code})")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to retrieve gearboxes: {e}")
            raise
    
    
    def create_gearbox(self, gearbox_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new gearbox entry.
        
        Args:
            gearbox_data (Dict[str, Any]): Gearbox details
            
        Returns:
            Dict[str, Any]: API response
        """
        payload = {
            "operation": "create",
            "gearbox": gearbox_data,
            "timestamp": "2025-01-14T17:00:00Z"
        }
        response = requests.post(f"{self.base_url}/gearboxes", headers=self.headers, json=payload)
        return response.json()
    
    def update_gearbox(self, gearbox_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing gearbox.
        
        Args:
            gearbox_id (str): ID of the gearbox to update
            updates (Dict[str, Any]): Fields to update
            
        Returns:
            Dict[str, Any]: API response
        """
        payload = {
            "operation": "update",
            "gearbox_id": gearbox_id,
            "updates": updates,
            "timestamp": "2025-01-14T17:00:00Z"
        }
        response = requests.post(f"{self.base_url}/gearboxes", headers=self.headers, json=payload)
        return response.json()
    
    def delete_gearbox(self, gearbox_id: str) -> Dict[str, Any]:
        """
        Delete a gearbox entry.
        
        Args:
            gearbox_id (str): ID of the gearbox to delete
            
        Returns:
            Dict[str, Any]: API response
        """
        payload = {
            "operation": "delete",
            "gearbox_id": gearbox_id
        }
        response = requests.post(f"{self.base_url}/gearboxes", headers=self.headers, json=payload)
        return response.json()


def main():
    """
    Demonstrate the gearbox catalog client functionality.
    
    AI-generated comment: This function shows examples of all CRUD operations.
    Replace the base_url and api_key with your actual values to test against
    a deployed API.
    """
    # AI-generated comment: Replace these with your actual API endpoint and key
    BASE_URL = "https://your-api-gateway-url.execute-api.us-east-1.amazonaws.com/Prod"
    API_KEY = "your-api-key-here"
    
    client = GearboxCatalogClient(BASE_URL, API_KEY)
    
    logger.info("Starting Gearbox Catalog API Demo")
    print("=== Gearbox Catalog API Demo ===\n")
    
    # 1. Get all gearboxes
    logger.info("Fetching all gearboxes from catalog")
    print("1. Fetching all gearboxes...")
    try:
        result = client.get_all_gearboxes()
        print(f"Status: Success")
        print(f"Total items: {result.get('summary', {}).get('total_items', 'N/A')}")
        print(f"Gearbox products: {result.get('summary', {}).get('gearbox_products', 'N/A')}")
        logger.debug(f"Retrieved {result.get('summary', {}).get('total_items', 0)} total items")
    except Exception as e:
        logger.error(f"Failed to fetch gearboxes: {e}")
        print(f"Error: {e}")
    print()
    
    # 2. Show gearbox summary
    print("2. Displaying gearbox summary...")
    try:
        result = client.get_all_gearboxes()
        print(f"Status: Success")
        print(f"Categories: {result.get('summary', {}).get('categories', 'N/A')}")
        if 'gearboxes' in result:
            print(f"Available gearboxes: {len(result['gearboxes'])}")
    except Exception as e:
        print(f"Error: {e}")
    print()
    
    # 3. Create a new gearbox (example)
    print("3. Creating a new gearbox...")
    new_gearbox = {
        "gearbox_id": "GB-DEMO-999",
        "model_name": "Demo Test Gearbox",
        "manufacturer": "Test Corp",
        "gearbox_type": "planetary",
        "torque_rating": 1500,
        "performance_rating": 85,
        "application_type": "test_application",
        "price_range": "medium"
    }
    
    try:
        result = client.create_gearbox(new_gearbox)
        print(f"Status: {result.get('message', 'Unknown')}")
        print(f"Created gearbox ID: {result.get('gearbox_id', 'N/A')}")
    except Exception as e:
        print(f"Error: {e}")
    print()
    
    # 4. Update the gearbox
    print("4. Updating the gearbox...")
    updates = {
        "torque_rating": 1600,
        "performance_rating": 90,
        "model_name": "Demo Test Gearbox - Updated"
    }
    
    try:
        result = client.update_gearbox("GB-DEMO-999", updates)
        print(f"Status: {result.get('message', 'Unknown')}")
        print(f"Updated fields: {result.get('updated_fields', [])}")
    except Exception as e:
        print(f"Error: {e}")
    print()
    
    # 5. Delete the gearbox
    print("5. Deleting the test gearbox...")
    try:
        result = client.delete_gearbox("GB-DEMO-999")
        print(f"Status: {result.get('message', 'Unknown')}")
    except Exception as e:
        print(f"Error: {e}")
    print()
    
    print("=== Demo Complete ===")


if __name__ == "__main__":
    main()
