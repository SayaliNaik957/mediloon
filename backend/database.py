import sqlite3
import os
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pharmacy.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Inventory Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        quantity INTEGER NOT NULL,
        reorder_threshold INTEGER NOT NULL,
        price REAL NOT NULL,
        is_rx BOOLEAN NOT NULL,
        dosage TEXT NOT NULL,
        alternatives TEXT
    )
    """)
    
    # 2. Order History Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS order_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id TEXT NOT NULL,
        medicine_name TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        order_date TEXT NOT NULL
    )
    """)
    
    # 3. Prescriptions Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS prescriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id TEXT NOT NULL,
        medicine_name TEXT NOT NULL,
        dosage TEXT NOT NULL,
        valid_until TEXT NOT NULL,
        is_used BOOLEAN NOT NULL DEFAULT 0
    )
    """)
    
    # 4. Drug Interactions Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS drug_interactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        medicine_a TEXT NOT NULL,
        medicine_b TEXT NOT NULL,
        risk_level TEXT NOT NULL,
        description TEXT NOT NULL
    )
    """)
    
    # 5. Patient Orders Table (Pharmacist Verification Queue)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patient_orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id TEXT NOT NULL,
        items TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Pending Verification',
        prescription_file TEXT,
        order_date TEXT NOT NULL,
        total_price REAL NOT NULL
    )
    """)
    
    conn.commit()
    seed_data(cursor, conn)
    conn.close()

def seed_data(cursor, conn):
    # Check if database is already seeded
    cursor.execute("SELECT COUNT(*) FROM inventory")
    if cursor.fetchone()[0] > 0:
        return
        
    print("Seeding database with initial pharmacy data...")
    
    # Seed Inventory
    inventory_items = [
        ("Paracetamol 500mg", 150, 20, 4.50, 0, "1 tablet every 6 hours", "Ibuprofen 400mg, Aspirin 100mg"),
        ("Ibuprofen 400mg", 100, 15, 6.20, 0, "1 tablet every 8 hours", "Paracetamol 500mg, Aspirin 100mg"),
        ("Aspirin 100mg", 200, 30, 3.80, 0, "1 tablet daily", "Ibuprofen 400mg"),
        ("Amoxicillin 250mg", 12, 10, 18.50, 1, "1 capsule 3 times daily", "Azithromycin 250mg"),
        ("Lisinopril 10mg", 45, 15, 12.00, 1, "1 tablet daily", "Losartan 50mg"),
        ("Metformin 500mg", 60, 20, 8.50, 1, "1 tablet twice daily with meals", "Glipizide 5mg"),
        ("Atorvastatin 20mg", 0, 10, 15.00, 1, "1 tablet at bedtime", "Rosuvastatin 10mg"),
        ("Warfarin 5mg", 2, 15, 22.00, 1, "1 tablet daily as directed", "Apixaban 5mg")
    ]
    cursor.executemany("""
        INSERT OR IGNORE INTO inventory (name, quantity, reorder_threshold, price, is_rx, dosage, alternatives)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, inventory_items)
    
    # Seed Order History
    # We want to simulate a chronic pattern for cust_101:
    # They take Lisinopril 10mg daily.
    # A pack of 30 tablets is ordered every 30 days.
    # Today is 2026-06-27
    today = datetime(2026, 6, 27)
    
    history_items = [
        # Customer 101 - Lisinopril 10mg orders
        ("cust_101", "Lisinopril 10mg", 30, (today - timedelta(days=90)).strftime("%Y-%m-%d")),
        ("cust_101", "Lisinopril 10mg", 30, (today - timedelta(days=60)).strftime("%Y-%m-%d")),
        ("cust_101", "Lisinopril 10mg", 30, (today - timedelta(days=30)).strftime("%Y-%m-%d")),
        
        # Customer 101 - Metformin 500mg orders (takes 2 daily, ordered 60 tab pack every 30 days)
        ("cust_101", "Metformin 500mg", 60, (today - timedelta(days=85)).strftime("%Y-%m-%d")),
        ("cust_101", "Metformin 500mg", 60, (today - timedelta(days=55)).strftime("%Y-%m-%d")),
        ("cust_101", "Metformin 500mg", 60, (today - timedelta(days=25)).strftime("%Y-%m-%d")),
        
        # Customer 101 - Paracetamol 500mg (ordered occasionally)
        ("cust_101", "Paracetamol 500mg", 1, (today - timedelta(days=45)).strftime("%Y-%m-%d")),
    ]
    cursor.executemany("""
        INSERT INTO order_history (customer_id, medicine_name, quantity, order_date)
        VALUES (?, ?, ?, ?)
    """, history_items)
    
    # Seed Prescriptions
    prescriptions = [
        # Valid prescription for Lisinopril for cust_101
        ("cust_101", "Lisinopril 10mg", "1 tablet daily", "2026-12-31"),
        # Valid prescription for Metformin for cust_101
        ("cust_101", "Metformin 500mg", "1 tablet twice daily with meals", "2026-12-31"),
        # Expired prescription for Amoxicillin for cust_101 (expired May 1, 2026)
        ("cust_101", "Amoxicillin 250mg", "1 capsule 3 times daily", "2026-05-01"),
        # Valid prescription for Warfarin for cust_101
        ("cust_101", "Warfarin 5mg", "1 tablet daily as directed", "2026-10-15")
    ]
    cursor.executemany("""
        INSERT INTO prescriptions (customer_id, medicine_name, dosage, valid_until)
        VALUES (?, ?, ?, ?)
    """, prescriptions)
    
    # Seed Drug Interactions
    interactions = [
        ("Aspirin 100mg", "Warfarin 5mg", "HIGH", "Concomitant use of Aspirin and Warfarin significantly increases bleeding risk. Monitor INR closely or consider alternative therapy."),
        ("Ibuprofen 400mg", "Aspirin 100mg", "MODERATE", "Ibuprofen may interfere with the antiplatelet effect of low-dose Aspirin, reducing cardioprotection."),
        ("Lisinopril 10mg", "Ibuprofen 400mg", "MODERATE", "NSAIDs like Ibuprofen may reduce the antihypertensive efficacy of ACE inhibitors like Lisinopril and increase risk of renal impairment.")
    ]
    cursor.executemany("""
        INSERT INTO drug_interactions (medicine_a, medicine_b, risk_level, description)
        VALUES (?, ?, ?, ?)
    """, interactions)
    
    conn.commit()
    print("Database seeded successfully!")

if __name__ == "__main__":
    init_db()
