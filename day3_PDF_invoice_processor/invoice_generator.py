from fpdf import FPDF
import os
import random
from faker import Faker
from datetime import datetime, timedelta

# Initialize Faker for random data generation
fake = Faker()

class InvoicePDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Invoice', 0, 1, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_invoice(invoice_id, output_dir):
    pdf = InvoicePDF()
    pdf.add_page()
    pdf.set_font('Arial', '', 12)

    # Generate random data
    customer_name = fake.name()
    phone_number = fake.phone_number()
    email = fake.email()
    date = (datetime.now() - timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d')

    # Table Header
    pdf.cell(30, 10, 'invoice_id', 1)
    pdf.cell(40, 10, 'customer_name', 1)
    pdf.cell(30, 10, 'phone', 1)
    pdf.cell(40, 10, 'email', 1)
    pdf.cell(30, 10, 'date', 1)
    pdf.cell(30, 10, 'vendor', 1)
    pdf.cell(30, 10, 'item', 1)
    pdf.cell(20, 10, 'quantity', 1)
    pdf.cell(30, 10, 'price', 1)
    pdf.cell(30, 10, 'total', 1)
    pdf.ln()

    # Sample data for items with vendors
    vendors = ['Amazon', 'Stripe', 'PayPal', 'eBay', 'Walmart']
    items = [
        ('Widget A', random.choice(vendors), random.randint(1, 5), round(random.uniform(10, 50), 2)),
        ('Widget B', random.choice(vendors), random.randint(1, 5), round(random.uniform(20, 80), 2)),
        ('Widget C', random.choice(vendors), random.randint(1, 5), round(random.uniform(5, 30), 2)),
    ]

    # Add rows to the table
    for item, vendor, qty, price in items:
        total = qty * price
        pdf.cell(30, 10, str(invoice_id), 1)
        pdf.cell(40, 10, customer_name, 1)
        pdf.cell(30, 10, phone_number, 1)
        pdf.cell(40, 10, email, 1)
        pdf.cell(30, 10, date, 1)
        pdf.cell(30, 10, vendor, 1)
        pdf.cell(30, 10, item, 1)
        pdf.cell(20, 10, str(qty), 1)
        pdf.cell(30, 10, f"${price:.2f}", 1)
        pdf.cell(30, 10, f"${total:.2f}", 1)
        pdf.ln()

    # Save the PDF
    output_path = os.path.join(output_dir, f"invoice_{invoice_id}.pdf")
    pdf.output(output_path)
    print(f"Invoice {invoice_id} saved to {output_path}")

# Directory to save invoices
output_dir = r"E:\pdf files"
os.makedirs(output_dir, exist_ok=True)

# Generate 10 sample invoices
for i in range(1, 11):
    generate_invoice(i, output_dir)
