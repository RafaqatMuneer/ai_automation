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

    # Invoice Header
    pdf.cell(0, 10, f'Invoice ID: {invoice_id}', ln=True)
    pdf.cell(0, 10, f'Customer Name: {customer_name}', ln=True)
    pdf.cell(0, 10, f'Phone: {phone_number}', ln=True)
    pdf.cell(0, 10, f'Email: {email}', ln=True)
    pdf.cell(0, 10, f'Date: {date}', ln=True)

    # Add a line break
    pdf.ln(10)

    # Invoice Table
    pdf.cell(40, 10, 'Item', 1)
    pdf.cell(40, 10, 'Quantity', 1)
    pdf.cell(40, 10, 'Price', 1)
    pdf.cell(40, 10, 'Total', 1)
    pdf.ln()

    # Sample data for items
    items = [
        ('Widget A', random.randint(1, 5), round(random.uniform(10, 50), 2)),
        ('Widget B', random.randint(1, 5), round(random.uniform(20, 80), 2)),
        ('Widget C', random.randint(1, 5), round(random.uniform(5, 30), 2)),
    ]

    for item, qty, price in items:
        total = qty * price
        pdf.cell(40, 10, item, 1)
        pdf.cell(40, 10, str(qty), 1)
        pdf.cell(40, 10, f"${price:.2f}", 1)
        pdf.cell(40, 10, f"${total:.2f}", 1)
        pdf.ln()

    # Total Amount
    pdf.ln(10)
    total_amount = sum(qty * price for _, qty, price in items)
    pdf.cell(0, 10, f'Total Amount: ${total_amount:.2f}', ln=True)

    # Save the PDF
    output_path = os.path.join(output_dir, f"invoice_{invoice_id}.pdf")
    pdf.output(output_path)
    print(f"Invoice {invoice_id} saved to {output_path}")

# Directory to save invoices
output_dir = r"E:\pdf files"
os.makedirs(output_dir, exist_ok=True)

# Generate 100 sample invoices
for i in range(1, 101):
    generate_invoice(i, output_dir)
