import os
import sys

# Add backend directory to sys.path so we can run this directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server.fastmcp import FastMCP
from mcp.shared.exceptions import McpError
from mcp.types import INVALID_PARAMS

from backend.mcp.tools import (
    add_to_cart,
    clear_cart,
    check_interactions,
    validate_prescription,
    get_inventory_status,
    get_refill_predictions,
    trigger_procurement_workflow,
    get_cart
)

# Initialize FastMCP server
mcp = FastMCP("Mediloon Pharmacy Server")

@mcp.tool()
def tool_add_to_cart(medicine_name: str, quantity: int) -> dict:
    """
    Adds a specified quantity of a medicine to the shopping cart.
    
    Args:
        medicine_name (str): The name of the medicine (e.g., 'Paracetamol 500mg').
        quantity (int): The number of units to add.
        
    Returns:
        dict: The updated cart state and status.
    """
    return add_to_cart(medicine_name, quantity)

@mcp.tool()
def tool_clear_cart() -> dict:
    """
    Clears all items from the current shopping cart.
    
    Returns:
        dict: Status message confirming clearance.
    """
    return clear_cart()

@mcp.tool()
def tool_get_cart() -> dict:
    """
    Retrieves the current shopping cart items and order total price.
    
    Returns:
        dict: Current cart contents and total amount.
    """
    return get_cart()

@mcp.tool()
def tool_check_interactions(medicines: list) -> dict:
    """
    Checks for drug-drug interactions between a list of medicine names.
    
    Args:
        medicines (list): List of medicine names (e.g., ['Aspirin 100mg', 'Warfarin 5mg']).
        
    Returns:
        dict: Interaction safety details and warning messages.
    """
    return check_interactions(medicines)

@mcp.tool()
def tool_validate_prescription(medicine_name: str, customer_id: str) -> dict:
    """
    Verifies if a customer has a valid prescription for a prescription-only (Rx) medicine.
    
    Args:
        medicine_name (str): Name of the medicine (e.g. 'Amoxicillin 250mg').
        customer_id (str): Customer ID (e.g. 'cust_101').
        
    Returns:
        dict: Validation details including status (valid, invalid, expired).
    """
    return validate_prescription(medicine_name, customer_id)

@mcp.tool()
def tool_get_inventory_status() -> dict:
    """
    Retrieves current stock levels of all medicines in the pharmacy inventory.
    
    Returns:
        dict: List of medicines, stock, and low stock statuses.
    """
    return get_inventory_status()

@mcp.tool()
def tool_get_refill_predictions(customer_id: str) -> dict:
    """
    Predicts when chronic medicines will run out based on the customer's purchase history.
    
    Args:
        customer_id (str): Customer ID (e.g. 'cust_101').
        
    Returns:
        dict: Depletion forecasting and suggestion timeline.
    """
    return get_refill_predictions(customer_id)

@mcp.tool()
def tool_trigger_procurement_workflow(medicine_name: str, quantity: int) -> dict:
    """
    Dispatches a purchase order to restock a medicine from the supplier (triggers Zapier/n8n API).
    
    Args:
        medicine_name (str): Name of the medicine to restock.
        quantity (int): Number of units to order.
        
    Returns:
        dict: Supplier dispatch invoice/PO details.
    """
    return trigger_procurement_workflow(medicine_name, quantity)

if __name__ == "__main__":
    # If run directly, launch the FastMCP server in stdio mode
    mcp.run()
