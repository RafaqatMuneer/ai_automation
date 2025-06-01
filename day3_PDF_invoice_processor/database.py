import sqlite3
from pathlib import Path
from typing import List, Dict
import logging
import pandas as pd
class InvoiceDatabase:
    def __init__(self, db_path: str = "invoices.db"):
        self.db_path = Path(db_path)
        self._init_db()
        self.logger = logging.getLogger(__name__)

    def _init_db(self) -> None:
        """Initialize the database with a professional schema design."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS invoices (
                    invoice_id TEXT NOT NULL,
                    customer_name TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    email TEXT NOT NULL,
                    date TEXT NOT NULL,
                    vendor TEXT NOT NULL,
                    item TEXT NOT NULL,
                    quantity INTEGER CHECK (quantity > 0),
                    price REAL CHECK (price > 0),
                    total REAL CHECK (total > 0)
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_invoice_date
                ON invoices(date)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_invoice_vendor
                ON invoices(vendor)
            """)

    def insert_invoice(self, invoice: Dict) -> bool:
        """Insert a single invoice into the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO invoices 
                    (invoice_id, customer_name, phone, email, date, vendor, item, quantity, price, total)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    invoice["invoice_id"],
                    invoice["customer_name"],
                    invoice["phone"],
                    invoice["email"],
                    invoice["date"],
                    invoice["vendor"],
                    invoice["item"],
                    invoice["quantity"],
                    invoice["price"],
                    invoice["total"]
                ))
            return True
        except sqlite3.Error as e:
            self.logger.error(f"Failed to insert invoice: {e}")
            return False

    def insert_invoices_batch(self, invoices: List[Dict]) -> bool:
        """Insert multiple invoices in a batch process."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.executemany("""
                    INSERT INTO invoices 
                    (invoice_id, customer_name, phone, email, date, vendor, item, quantity, price, total)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, [
                    (
                        invoice["invoice_id"],
                        invoice["customer_name"],
                        invoice["phone"],
                        invoice["email"],
                        invoice["date"],
                        invoice["vendor"],
                        invoice["item"],
                        invoice["quantity"],
                        invoice["price"],
                        invoice["total"]
                    )
                    for invoice in invoices
                ])
                
            return True
        except sqlite3.Error as e:
            self.logger.error(f"Failed to insert batch invoices: {e}")
            return False

    def search_invoices(self, query: str) -> List[Dict]:
        """Search invoices based on vendor, item, or date."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM invoices 
                WHERE vendor LIKE ? OR item LIKE ? OR date LIKE ?
                ORDER BY date DESC
            """, (f"%{query}%", f"%{query}%", f"%{query}%"))
            return [dict(row) for row in cursor]
    def export_to_excel(self, query: str = "SELECT * FROM invoices"):
        """Day 2 integration point"""
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql(query, conn)
            df.to_excel("invoices.xlsx", engine="openpyxl")
    

# Sample data for batch processing
sample_invoices = [
    {
        "invoice_id": 5,
        "customer_name": "John Joseph",
        "phone": "001-648-572-49",
        "email": "s8a3nxd9r9a6128@example.com",
        "date": "2023-03-16",
        "vendor": "PayPal",
        "item": "Widget A",
        "quantity": 4,
        "price": 11.24
    },
    {
        "invoice_id": 5,
        "customer_name": "John Joseph",
        "phone": "001-648-572-49",
        "email": "s8a3nxd9r9a6128@example.com",
        "date": "2023-03-16",
        "vendor": "Stripe",
        "item": "Widget B",
        "quantity": 3,
        "price": 22.36
    },
    {
        "invoice_id": 5,
        "customer_name": "John Joseph",
        "phone": "001-648-572-49",
        "email": "s8a3nxd9r9a6128@example.com",
        "date": "2023-03-16",
        "vendor": "Amazon",
        "item": "Widget C",
        "quantity": 4,
        "price": 20.11
    },
]

sample_invoices = [{'invoice_id': 1, 'customer_name': 'Nicholas Murphy', 'phone': '+1-741-505-87', 'email': '7t8imx1o2th6y2w7ashington@', 'date': 'e2x0a2m5-p0le5.-c2o8m', 'vendor': 'PayPal', 'item': 'Widget A', 'quantity': 1, 'price': 12.69, 'total': 12.69}, {'invoice_id': 1, 'customer_name': 'Nicholas Murphy', 'phone': '+1-741-505-87', 'email': '7t8imx1o2th6y2w7ashington@', 'date': 'e2x0a2m5-p0le5.-c2o8m', 'vendor': 'PayPal', 'item': 'Widget B', 'quantity': 1, 'price': 77.93, 'total': 77.93}, {'invoice_id': 1, 'customer_name': 'Nicholas Murphy', 'phone': '+1-741-505-87', 'email': '7t8imx1o2th6y2w7ashington@', 'date': 'e2x0a2m5-p0le5.-c2o8m', 'vendor': 'eBay', 'item': 'Widget C', 'quantity': 5, 'price': 21.63, 'total': 108.15}]
# Initialize database and insert batch
db = InvoiceDatabase()
db.insert_invoices_batch(sample_invoices)
db.export_to_excel()

# # Search invoices
# search_results = db.search_invoices("Amazon")
# print(search_results)

