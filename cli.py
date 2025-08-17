#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "requests>=2.32.4",
#     "click>=8.1.7",
#     "boto3>=1.40.8",
#     "rich>=13.0.0",
# ]
# ///
"""
CLI tool for testing the gearbox catalog production endpoint.

This script provides an interactive command-line interface for testing
all CRUD operations against the deployed gearbox catalog API.
"""

import json
import os
import sys
from typing import Dict, Any, Optional

import click
import requests
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.syntax import Syntax

console = Console()

class GearboxAPI:
    """Client for the Gearbox Catalog API."""
    
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {'Content-Type': 'application/json'}
        if api_key:
            self.headers['x-api-key'] = api_key
    
    def get_all_gearboxes(self) -> requests.Response:
        """Get all gearboxes from the catalog."""
        return requests.get(f"{self.base_url}/gearboxes", headers=self.headers)
    
    def get_gearboxes_by_type(self, gearbox_type: str) -> requests.Response:
        """Get gearboxes filtered by type."""
        params = {'type': gearbox_type}
        return requests.get(f"{self.base_url}/gearboxes", headers=self.headers, params=params)
    
    def create_gearbox(self, gearbox_data: Dict[str, Any]) -> requests.Response:
        """Create a new gearbox."""
        payload = {
            "operation": "create",
            "gearbox": gearbox_data,
            "timestamp": "2025-08-17T12:00:00Z"
        }
        return requests.post(f"{self.base_url}/gearboxes", headers=self.headers, json=payload)
    
    def update_gearbox(self, gearbox_id: str, updates: Dict[str, Any]) -> requests.Response:
        """Update an existing gearbox."""
        payload = {
            "operation": "update",
            "gearbox_id": gearbox_id,
            "updates": updates,
            "timestamp": "2025-08-17T12:00:00Z"
        }
        return requests.post(f"{self.base_url}/gearboxes", headers=self.headers, json=payload)
    
    def delete_gearbox(self, gearbox_id: str) -> requests.Response:
        """Delete a gearbox."""
        payload = {
            "operation": "delete",
            "gearbox_id": gearbox_id
        }
        return requests.post(f"{self.base_url}/gearboxes", headers=self.headers, json=payload)


def display_response(response: requests.Response, operation: str):
    """Display API response in a formatted way."""
    status_color = "green" if response.status_code < 400 else "red"
    
    console.print(f"\n[bold]{operation} Response[/bold]")
    console.print(f"Status: [{status_color}]{response.status_code}[/{status_color}]")
    
    try:
        data = response.json()
        syntax = Syntax(json.dumps(data, indent=2), "json", theme="monokai", line_numbers=True)
        console.print(Panel(syntax, title="Response Body"))
    except json.JSONDecodeError:
        console.print(f"Raw response: {response.text}")


def interactive_mode(api: GearboxAPI):
    """Interactive mode for testing API operations."""
    auth_status = "🔑 Authenticated" if api.api_key else "⚠️  No API Key"
    console.print(Panel.fit(
        f"[bold blue]Gearbox Catalog API Interactive Tester[/bold blue]\n"
        f"Endpoint: {api.base_url}\n"
        f"Auth: {auth_status}\n\n"
        "Choose operations to test against your production endpoint.",
        border_style="blue"
    ))
    
    while True:
        console.print("\n[bold cyan]Available Operations:[/bold cyan]")
        console.print("1. List all gearboxes")
        console.print("2. Filter gearboxes by type")
        console.print("3. Create new gearbox")
        console.print("4. Update existing gearbox")
        console.print("5. Delete gearbox")
        console.print("6. Test API connectivity")
        console.print("7. Exit")
        
        choice = Prompt.ask("Select operation", choices=["1", "2", "3", "4", "5", "6", "7"])
        
        if choice == "1":
            response = api.get_all_gearboxes()
            display_response(response, "GET All Gearboxes")
            
        elif choice == "2":
            gearbox_type = Prompt.ask("Enter gearbox type to filter")
            response = api.get_gearboxes_by_type(gearbox_type)
            display_response(response, f"GET Gearboxes (type={gearbox_type})")
            
        elif choice == "3":
            console.print("[yellow]Creating new gearbox...[/yellow]")
            gearbox_id = Prompt.ask("Gearbox ID")
            model_name = Prompt.ask("Model name")
            manufacturer = Prompt.ask("Manufacturer")
            gearbox_type = Prompt.ask("Gearbox type")
            
            gearbox_data = {
                "gearbox_id": gearbox_id,
                "model_name": model_name,
                "manufacturer": manufacturer,
                "gearbox_type": gearbox_type
            }
            
            # Optional fields
            if Confirm.ask("Add torque rating?"):
                gearbox_data["torque_rating"] = int(Prompt.ask("Torque rating (numeric)"))
            if Confirm.ask("Add performance rating?"):
                gearbox_data["performance_rating"] = int(Prompt.ask("Performance rating (numeric)"))
            if Confirm.ask("Add application type?"):
                gearbox_data["application_type"] = Prompt.ask("Application type")
            if Confirm.ask("Add price range?"):
                gearbox_data["price_range"] = Prompt.ask("Price range")
            
            response = api.create_gearbox(gearbox_data)
            display_response(response, "CREATE Gearbox")
            
        elif choice == "4":
            gearbox_id = Prompt.ask("Gearbox ID to update")
            console.print("[yellow]Enter updates (press Enter with empty value to finish):[/yellow]")
            
            updates = {}
            while True:
                field = Prompt.ask("Field name (or press Enter to finish)", default="")
                if not field:
                    break
                value = Prompt.ask(f"New value for {field}")
                # Try to convert to number if it looks numeric
                try:
                    if '.' in value:
                        updates[field] = float(value)
                    else:
                        updates[field] = int(value)
                except ValueError:
                    updates[field] = value
            
            if updates:
                response = api.update_gearbox(gearbox_id, updates)
                display_response(response, "UPDATE Gearbox")
            else:
                console.print("[yellow]No updates provided[/yellow]")
                
        elif choice == "5":
            gearbox_id = Prompt.ask("Gearbox ID to delete")
            if Confirm.ask(f"Are you sure you want to delete gearbox {gearbox_id}?"):
                response = api.delete_gearbox(gearbox_id)
                display_response(response, "DELETE Gearbox")
            else:
                console.print("[yellow]Delete cancelled[/yellow]")
                
        elif choice == "6":
            console.print("[yellow]Testing API connectivity...[/yellow]")
            response = api.get_all_gearboxes()
            if response.status_code == 200:
                console.print("[green]✓ API is accessible[/green]")
            elif response.status_code == 401:
                console.print("[red]✗ API key authentication failed[/red]")
            else:
                console.print(f"[red]✗ API returned status {response.status_code}[/red]")
            display_response(response, "Connectivity Test")
            
        elif choice == "7":
            console.print("[green]Goodbye![/green]")
            break


@click.command()
@click.option('--url', '-u', required=True, help='API Gateway base URL')
@click.option('--api-key', '-k', help='API key for authentication (or set GEARBOX_API_KEY env var)')
@click.option('--operation', '-o', type=click.Choice(['list', 'create', 'update', 'delete', 'filter']), 
              help='Specific operation to run (non-interactive)')
@click.option('--gearbox-id', help='Gearbox ID for update/delete operations')
@click.option('--type', 'gearbox_type', help='Filter by gearbox type')
@click.option('--data', help='JSON data for create/update operations')
@click.option('--interactive', '-i', is_flag=True, help='Run in interactive mode')
def main(url: str, api_key: Optional[str], operation: Optional[str], 
         gearbox_id: Optional[str], gearbox_type: Optional[str], 
         data: Optional[str], interactive: bool):
    """
    CLI tool for testing the gearbox catalog production API.
    
    Examples:
    
    # Interactive mode
    uv run cli.py -u https://your-api.execute-api.us-east-1.amazonaws.com/Prod -i
    
    # List all gearboxes
    uv run cli.py -u https://your-api.execute-api.us-east-1.amazonaws.com/Prod -k your-key -o list
    
    # Filter by type
    uv run cli.py -u https://your-api.execute-api.us-east-1.amazonaws.com/Prod -k your-key -o filter --type planetary
    
    # Create gearbox
    uv run cli.py -u https://your-api.execute-api.us-east-1.amazonaws.com/Prod -k your-key -o create --data '{"gearbox_id":"GB-001","model_name":"Test","manufacturer":"TestCorp","gearbox_type":"planetary"}'
    """
    # Get API key from environment if not provided
    if not api_key:
        api_key = os.getenv('GEARBOX_API_KEY')
        if not api_key:
            console.print("[yellow]Warning: No API key provided. Some endpoints may require authentication.[/yellow]")
    
    api = GearboxAPI(url, api_key)
    
    if interactive or not operation:
        interactive_mode(api)
        return
    
    # Non-interactive mode
    try:
        if operation == 'list':
            response = api.get_all_gearboxes()
            display_response(response, "List All Gearboxes")
            
        elif operation == 'filter':
            if not gearbox_type:
                console.print("[red]Error: --type required for filter operation[/red]")
                sys.exit(1)
            response = api.get_gearboxes_by_type(gearbox_type)
            display_response(response, f"Filter by Type ({gearbox_type})")
            
        elif operation == 'create':
            if not data:
                console.print("[red]Error: --data required for create operation[/red]")
                sys.exit(1)
            gearbox_data = json.loads(data)
            response = api.create_gearbox(gearbox_data)
            display_response(response, "Create Gearbox")
            
        elif operation == 'update':
            if not gearbox_id or not data:
                console.print("[red]Error: --gearbox-id and --data required for update operation[/red]")
                sys.exit(1)
            updates = json.loads(data)
            response = api.update_gearbox(gearbox_id, updates)
            display_response(response, "Update Gearbox")
            
        elif operation == 'delete':
            if not gearbox_id:
                console.print("[red]Error: --gearbox-id required for delete operation[/red]")
                sys.exit(1)
            response = api.delete_gearbox(gearbox_id)
            display_response(response, "Delete Gearbox")
            
    except json.JSONDecodeError as e:
        console.print(f"[red]Error: Invalid JSON data - {e}[/red]")
        sys.exit(1)
    except requests.RequestException as e:
        console.print(f"[red]Error: API request failed - {e}[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()