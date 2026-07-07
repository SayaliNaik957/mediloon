import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import init_db
from backend.agents.agent_system import run_agent_pipeline, process_prescription_upload
from backend.mcp.tools import (
    get_inventory_status,
    get_cart,
    clear_cart,
    create_patient_order,
    get_patient_orders,
    dispatch_patient_order,
    get_draft_pos,
    confirm_supplier_po
)

class PrescriptionUploadRequest(BaseModel):
    filename: str
    customer_id: str = "cust_101"

class ConfirmOrderRequest(BaseModel):
    customer_id: str = "cust_101"
    prescription_file: str = None

class DispatchOrderRequest(BaseModel):
    order_id: int

class ConfirmPORequest(BaseModel):
    item: str
    supplier_email: str

# Initialize database on startup if it doesn't exist
db_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pharmacy.db")
if not os.path.exists(db_file):
    print("Database file not found, initializing...")
    init_db()

app = FastAPI(title="Mediloon Autonomous Pharmacy System API")

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    customer_id: str = "cust_101"

@app.get("/api/inventory")
async def api_inventory():
    """Gets the current inventory list and stock status."""
    try:
        return get_inventory_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/cart")
async def api_cart():
    """Gets the current shopping cart state."""
    try:
        return get_cart()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
async def api_chat(req: ChatRequest):
    """Processes user text input through the multi-agent ordering pipeline."""
    try:
        result = await run_agent_pipeline(req.message, req.customer_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/clear-cart")
async def api_clear_cart():
    """Clears all items in the cart."""
    try:
        return clear_cart()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/reset-db")
async def api_reset_db():
    """Resets the pharmacy database to initial seed data."""
    try:
        if os.path.exists(db_file):
            os.remove(db_file)
        init_db()
        return {"status": "success", "message": "Database reset and seeded successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload-prescription")
async def api_upload_prescription(req: PrescriptionUploadRequest):
    """Parses an uploaded prescription mock file and auto-orders items into cart."""
    try:
        result = await process_prescription_upload(req.filename, req.customer_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/confirm-order")
async def api_confirm_order(req: ConfirmOrderRequest):
    """Saves active cart items as a verified patient order awaiting pharmacist approval."""
    try:
        return create_patient_order(req.customer_id, req.prescription_file)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/orders")
async def api_get_orders(customer_id: str = None):
    """Retrieves list of active patient orders."""
    try:
        return get_patient_orders(customer_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/dispatch-order")
async def api_dispatch_order(req: DispatchOrderRequest):
    """Verification queue action: dispatches order, deducts database inventory."""
    try:
        return dispatch_patient_order(req.order_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/procurement/drafts")
async def api_get_procurement_drafts():
    """Retrieves active draft PO invoices for out-of-stock items."""
    try:
        return get_draft_pos()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/procurement/confirm")
async def api_confirm_procurement(req: ConfirmPORequest):
    """Confirms draft supplier PO invoice, updates database stock, emails supplier."""
    try:
        return confirm_supplier_po(req.item, req.supplier_email)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount the frontend directory to serve UI files directly
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
    print(f"Mounted frontend directory: {frontend_dir}")
else:
    print(f"Frontend directory not found at: {frontend_dir}. API will run in standalone mode.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
