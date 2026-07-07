import os
import sqlite3
import json
from datetime import datetime, timedelta
from ..database import get_db_connection

# Simple in-memory cart simulation
CART = {}

def get_cart() -> dict:
    """
    Retrieves the current shopping cart items and order summary.
    
    Returns:
        dict: A dictionary containing cart items and the total price.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    items = []
    total_price = 0.0
    
    for med_name, qty in CART.items():
        cursor.execute("SELECT price, is_rx, dosage FROM inventory WHERE name = ?", (med_name,))
        row = cursor.fetchone()
        if row:
            price = row["price"]
            is_rx = row["is_rx"]
            dosage = row["dosage"]
            item_total = price * qty
            total_price += item_total
            items.append({
                "medicine_name": med_name,
                "quantity": qty,
                "unit_price": price,
                "total_price": item_total,
                "requires_prescription": bool(is_rx),
                "dosage_instruction": dosage
            })
            
    conn.close()
    return {
        "cart_items": items,
        "total_items_count": sum(CART.values()),
        "total_amount": round(total_price, 2)
    }

def add_to_cart(medicine_name: str, quantity: int) -> dict:
    """
    Adds a specified quantity of a medicine to the shopping cart.
    
    Args:
        medicine_name (str): The name of the medicine (e.g., 'Paracetamol 500mg').
        quantity (int): The number of units to add.
        
    Returns:
        dict: The updated cart state and a success/failure message.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if medicine exists and verify stock
    cursor.execute("SELECT quantity, is_rx FROM inventory WHERE name LIKE ?", (f"%{medicine_name}%",))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return {"status": "error", "message": f"Medicine '{medicine_name}' not found in inventory."}
        
    # Get exact name
    cursor.execute("SELECT name, quantity, is_rx FROM inventory WHERE name LIKE ?", (f"%{medicine_name}%",))
    exact_row = cursor.fetchone()
    exact_name = exact_row["name"]
    available_qty = exact_row["quantity"]
    
    if available_qty < quantity:
        conn.close()
        return {
            "status": "error",
            "message": f"Insufficient stock. Only {available_qty} units of '{exact_name}' available."
        }
        
    # Add to cart
    CART[exact_name] = CART.get(exact_name, 0) + quantity
    conn.close()
    
    return {
        "status": "success",
        "message": f"Added {quantity} of '{exact_name}' to cart.",
        "cart": get_cart()
    }

def clear_cart() -> dict:
    """
    Clears all items from the shopping cart.
    
    Returns:
        dict: A message confirming the cart is empty.
    """
    CART.clear()
    return {"status": "success", "message": "Cart cleared.", "cart": get_cart()}

def check_interactions(medicines: list) -> dict:
    """
    Checks if there are any drug-drug interactions between the medicines in the list.
    
    Args:
        medicines (list): A list of medicine names (e.g., ['Aspirin 100mg', 'Warfarin 5mg']).
        
    Returns:
        dict: Warning details if interactions are found, otherwise a safety confirmation.
    """
    if len(medicines) < 2:
        return {"status": "safe", "message": "No interactions possible with fewer than 2 medicines."}
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    warnings = []
    
    # Check pairwise interactions
    for i in range(len(medicines)):
        for j in range(i + 1, len(medicines)):
            med_a = medicines[i]
            med_b = medicines[j]
            
            cursor.execute("""
                SELECT risk_level, description FROM drug_interactions 
                WHERE (medicine_a LIKE ? AND medicine_b LIKE ?) OR (medicine_a LIKE ? AND medicine_b LIKE ?)
            """, (f"%{med_a}%", f"%{med_b}%", f"%{med_b}%", f"%{med_a}%"))
            
            row = cursor.fetchone()
            if row:
                warnings.append({
                    "medicine_a": med_a,
                    "medicine_b": med_b,
                    "risk_level": row["risk_level"],
                    "description": row["description"]
                })
                
    conn.close()
    
    if warnings:
        return {
            "status": "warning",
            "message": "Drug interaction warning! High risk detected.",
            "interactions": warnings
        }
    else:
        return {
            "status": "safe",
            "message": "No known drug-drug interactions detected for the specified list."
        }

def validate_prescription(medicine_name: str, customer_id: str) -> dict:
    """
    Checks if a customer has a valid prescription for a prescription-only (Rx) medicine.
    
    Args:
        medicine_name (str): The name of the medicine to check.
        customer_id (str): The ID of the customer (e.g., 'cust_101').
        
    Returns:
        dict: Verification status containing whether it is valid, expired, or missing.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # First, check if the medicine actually requires a prescription (is_rx)
    cursor.execute("SELECT name, is_rx FROM inventory WHERE name LIKE ?", (f"%{medicine_name}%",))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return {"status": "error", "message": f"Medicine '{medicine_name}' not found."}
        
    exact_name = row["name"]
    is_rx = row["is_rx"]
    
    if not is_rx:
        conn.close()
        return {
            "status": "valid",
            "message": f"'{exact_name}' is an Over-The-Counter (OTC) medicine and does not require a prescription."
        }
        
    # Query prescriptions table
    cursor.execute("""
        SELECT valid_until FROM prescriptions 
        WHERE customer_id = ? AND medicine_name LIKE ? AND is_used = 0
    """, (customer_id, f"%{medicine_name}%"))
    
    rx_row = cursor.fetchone()
    if not rx_row:
        conn.close()
        return {
            "status": "invalid",
            "message": f"No active prescription found for '{exact_name}' and customer ID '{customer_id}'."
        }
        
    valid_until_str = rx_row["valid_until"]
    valid_until = datetime.strptime(valid_until_str, "%Y-%m-%d")
    
    # Assume current date is 2026-06-27 (matching local time in user's prompt)
    current_date = datetime(2026, 6, 27)
    
    if valid_until < current_date:
        conn.close()
        return {
            "status": "invalid",
            "message": f"Prescription for '{exact_name}' expired on {valid_until_str}."
        }
        
    conn.close()
    return {
        "status": "valid",
        "message": f"Valid prescription found for '{exact_name}'. Valid until {valid_until_str}."
    }

def get_inventory_status() -> dict:
    """
    Retrieves the status of all medicines in the inventory including stock levels.
    
    Returns:
        dict: A list of medicines with stock quantities and low stock alerts.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, quantity, reorder_threshold, price, is_rx FROM inventory")
    rows = cursor.fetchall()
    
    inventory_list = []
    for row in rows:
        qty = row["quantity"]
        threshold = row["reorder_threshold"]
        inventory_list.append({
            "id": row["id"],
            "name": row["name"],
            "quantity": qty,
            "reorder_threshold": threshold,
            "price": row["price"],
            "is_rx": bool(row["is_rx"]),
            "status": "Low Stock" if qty <= threshold else "Good"
        })
        
    conn.close()
    return {"inventory": inventory_list}

def get_refill_predictions(customer_id: str) -> dict:
    """
    Predicts when chronic medicines will run out based on the customer's order history.
    
    Args:
        customer_id (str): The ID of the customer (e.g., 'cust_101').
        
    Returns:
        dict: Predicted depletion dates and suggestions for refills.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get distinct chronic medicines ordered by user
    cursor.execute("""
        SELECT DISTINCT medicine_name FROM order_history 
        WHERE customer_id = ?
    """, (customer_id,))
    med_rows = cursor.fetchall()
    
    predictions = []
    current_date = datetime(2026, 6, 27)
    
    for med_row in med_rows:
        med_name = med_row["medicine_name"]
        
        # Get order dates and quantities ordered
        cursor.execute("""
            SELECT quantity, order_date FROM order_history
            WHERE customer_id = ? AND medicine_name = ?
            ORDER BY order_date ASC
        """, (customer_id, med_name))
        orders = cursor.fetchall()
        
        # We need at least 2 orders to calculate frequency
        if len(orders) < 2:
            # Check single order and default to a standard 30-day depletion if common chronic size
            if len(orders) == 1:
                last_date_str = orders[0]["order_date"]
                last_qty = orders[0]["quantity"]
                last_date = datetime.strptime(last_date_str, "%Y-%m-%d")
                
                # Check dosage to estimate depletion
                cursor.execute("SELECT is_rx, dosage FROM inventory WHERE name = ?", (med_name,))
                inv_row = cursor.fetchone()
                
                if inv_row and inv_row["is_rx"]:
                    depletion_days = last_qty  # default 1 unit per day
                    if "twice daily" in inv_row["dosage"].lower():
                        depletion_days = last_qty / 2
                    
                    depletion_date = last_date + timedelta(days=depletion_days)
                    days_remaining = (depletion_date - current_date).days
                    
                    predictions.append({
                        "medicine_name": med_name,
                        "last_order_date": last_date_str,
                        "last_quantity": last_qty,
                        "depletion_date": depletion_date.strftime("%Y-%m-%d"),
                        "days_remaining": days_remaining,
                        "status": "Refill Needed Now" if days_remaining <= 0 else f"Refill in {days_remaining} days",
                        "is_chronic": True
                    })
            continue
            
        # Calculate intervals
        dates = [datetime.strptime(o["order_date"], "%Y-%m-%d") for o in orders]
        intervals = [(dates[i] - dates[i-1]).days for i in range(1, len(dates))]
        avg_interval = sum(intervals) / len(intervals)
        
        last_order = orders[-1]
        last_date_str = last_order["order_date"]
        last_qty = last_order["quantity"]
        last_date = datetime.strptime(last_date_str, "%Y-%m-%d")
        
        # Expected depletion is last order date + avg interval
        depletion_date = last_date + timedelta(days=avg_interval)
        days_remaining = (depletion_date - current_date).days
        
        predictions.append({
            "medicine_name": med_name,
            "last_order_date": last_date_str,
            "last_quantity": last_qty,
            "depletion_date": depletion_date.strftime("%Y-%m-%d"),
            "days_remaining": days_remaining,
            "status": "Refill Needed Now" if days_remaining <= 0 else f"Refill in {days_remaining} days",
            "is_chronic": True
        })
        
    conn.close()
    return {
        "customer_id": customer_id,
        "as_of_date": "2026-06-27",
        "predictions": predictions
    }

def trigger_procurement_workflow(medicine_name: str, quantity: int) -> dict:
    """
    Triggers the distributor or supplier API (simulated via n8n / Zapier) to place a purchase order.
    
    Args:
        medicine_name (str): Name of the medicine to restock.
        quantity (int): Number of units to order from the distributor.
        
    Returns:
        dict: Order dispatch details.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT quantity, price FROM inventory WHERE name = ?", (medicine_name,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return {"status": "error", "message": f"Unknown medicine '{medicine_name}'"}
        
    current_qty = row["quantity"]
    unit_price = row["price"]
    
    # Restock inventory in DB to simulate supplier delivery
    new_qty = current_qty + quantity
    cursor.execute("UPDATE inventory SET quantity = ? WHERE name = ?", (new_qty, medicine_name))
    conn.commit()
    conn.close()
    
    return {
        "status": "success",
        "message": f"Supplier PO generated. Dispatched restock request for {quantity} units of '{medicine_name}' via Zapier/n8n API. Stock updated in database.",
        "purchase_order": {
            "supplier": "Global Pharma Distributor",
            "item": medicine_name,
            "quantity_ordered": quantity,
            "estimated_cost": round(unit_price * 0.7 * quantity, 2), # Wholesale price is 70% of retail
            "status": "PO_DISPATCHED",
            "updated_inventory_stock": new_qty
        }
    }

def create_patient_order(customer_id: str, prescription_file: str = None) -> dict:
    """
    Submits the current shopping cart items as a new patient order,
    pending pharmacist verification, and clears the cart.
    """
    cart = get_cart()
    if not cart["cart_items"]:
        return {"status": "error", "message": "Shopping cart is empty."}
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    items_json = json.dumps(cart["cart_items"])
    order_date = "2026-06-27"
    total_price = cart["total_amount"]
    
    cursor.execute("""
        INSERT INTO patient_orders (customer_id, items, status, prescription_file, order_date, total_price)
        VALUES (?, ?, 'Pending Verification', ?, ?, ?)
    """, (customer_id, items_json, prescription_file, order_date, total_price))
    
    order_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    # Clear cart
    clear_cart()
    
    return {
        "status": "success",
        "message": f"Order #{order_id} successfully created. Status: Awaiting Pharmacist Verification.",
        "order": {
            "id": order_id,
            "customer_id": customer_id,
            "status": "Pending Verification",
            "prescription_file": prescription_file,
            "order_date": order_date,
            "total_price": total_price
        }
    }

def get_patient_orders(customer_id: str = None) -> list:
    """
    Retrieves all patient orders from the database, optionally filtered by customer_id.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if customer_id:
        cursor.execute("""
            SELECT id, customer_id, items, status, prescription_file, order_date, total_price 
            FROM patient_orders WHERE customer_id = ? ORDER BY id DESC
        """, (customer_id,))
    else:
        cursor.execute("""
            SELECT id, customer_id, items, status, prescription_file, order_date, total_price 
            FROM patient_orders ORDER BY id DESC
        """)
        
    rows = cursor.fetchall()
    conn.close()
    
    orders = []
    for row in rows:
        orders.append({
            "id": row["id"],
            "customer_id": row["customer_id"],
            "items": json.loads(row["items"]),
            "status": row["status"],
            "prescription_file": row["prescription_file"],
            "order_date": row["order_date"],
            "total_price": row["total_price"]
        })
    return orders

def dispatch_patient_order(order_id: int) -> dict:
    """
    Verifies and dispatches a pending order. Deducts items from database inventory.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Fetch order details
    cursor.execute("SELECT items, status FROM patient_orders WHERE id = ?", (order_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return {"status": "error", "message": f"Order #{order_id} not found."}
        
    if row["status"] == "Dispatched":
        conn.close()
        return {"status": "error", "message": f"Order #{order_id} is already dispatched."}
        
    items = json.loads(row["items"])
    
    # Check inventory availability for all items first
    for item in items:
        cursor.execute("SELECT quantity FROM inventory WHERE name = ?", (item["medicine_name"],))
        inv_row = cursor.fetchone()
        if not inv_row:
            conn.close()
            return {"status": "error", "message": f"Medicine '{item['medicine_name']}' not found in inventory."}
        if inv_row["quantity"] < item["quantity"]:
            conn.close()
            return {
                "status": "error",
                "message": f"Cannot dispatch order. Medicine '{item['medicine_name']}' is out of stock ({inv_row['quantity']} units left, ordered {item['quantity']})."
            }
            
    # Deduct inventory stock
    low_stock_alerts = []
    for item in items:
        cursor.execute("SELECT quantity, reorder_threshold FROM inventory WHERE name = ?", (item["medicine_name"],))
        inv_row = cursor.fetchone()
        new_qty = inv_row["quantity"] - item["quantity"]
        cursor.execute("UPDATE inventory SET quantity = ? WHERE name = ?", (new_qty, item["medicine_name"]))
        
        # Check if dropped below threshold
        if new_qty <= inv_row["reorder_threshold"]:
            low_stock_alerts.append({
                "medicine_name": item["medicine_name"],
                "stock_left": new_qty,
                "threshold": inv_row["reorder_threshold"]
            })
            
    # Update order status
    cursor.execute("UPDATE patient_orders SET status = 'Dispatched' WHERE id = ?", (order_id,))
    conn.commit()
    conn.close()
    
    return {
        "status": "success",
        "message": f"Order #{order_id} has been verified and successfully dispatched.",
        "low_stock_alerts": low_stock_alerts
    }

# Memory storage for active Draft POs (since we want them to statefully progress to "Invoiced" when confirmed)
# PO ID -> PO Dictionary
DRAFT_POS = {}

def get_draft_pos() -> list:
    """
    Inspects database inventory and generates draft purchase invoices for out-of-stock items.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, quantity, reorder_threshold, price FROM inventory WHERE quantity <= reorder_threshold")
    rows = cursor.fetchall()
    conn.close()
    
    # Re-build DRAFT_POS based on out-of-stock items in DB
    active_drafts = []
    
    for row in rows:
        med_name = row["name"]
        qty = row["quantity"]
        
        # Generate PO if not exists
        if med_name not in DRAFT_POS:
            po_id = f"PO-{1000 + hash(med_name) % 9000}"
            DRAFT_POS[med_name] = {
                "id": po_id,
                "item": med_name,
                "quantity_to_order": 50,
                "wholesale_cost": round(row["price"] * 0.7 * 50, 2),
                "status": "Draft - Awaiting Confirmation",
                "supplier": "Global Wholesaler Distributor",
                "supplier_email": "orders@globalwholesaler.com"
            }
        active_drafts.append(DRAFT_POS[med_name])
        
    return active_drafts

def confirm_supplier_po(item_name: str, supplier_email: str) -> dict:
    """
    Confirms and sends a draft PO invoice to the supplier's email, triggering restocking.
    """
    if item_name not in DRAFT_POS:
        return {"status": "error", "message": f"No draft PO found for medicine '{item_name}'."}
        
    po = DRAFT_POS[item_name]
    po["status"] = "Invoiced"
    po["supplier_email"] = supplier_email
    
    # Restock database stock to represent supplier delivery
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT quantity FROM inventory WHERE name = ?", (item_name,))
    row = cursor.fetchone()
    new_qty = row["quantity"] + po["quantity_to_order"]
    cursor.execute("UPDATE inventory SET quantity = ? WHERE name = ?", (new_qty, item_name))
    conn.commit()
    conn.close()
    
    return {
        "status": "success",
        "message": f"PO {po['id']} confirmed. Invoice successfully emailed to '{supplier_email}'. Restocked {po['quantity_to_order']} units in database.",
        "po": po
    }
