import re
import pandas as pd
from pathlib import Path
from typing import List, Dict
import re
import logger_util
import pdfplumber
from datetime import datetime
from database import InvoiceDatabase

class InvoiceProcessor:
    def __init__(self):
        self.logger = logger_util.LoggerUtility().logger
        # self.logger.info("InvoiceProcessor initialized.")
        self.db = InvoiceDatabase()
        self.stats : Dict[str, int] = {
            "invoices_processed" : 0,
            "tables_extracted" : 0,
            "errors" : 0
        }
    def process_invoices(self, input_dir : Path, output_dir : Path) -> None:
        "Batch processing of pdf invoices"
        try:
            # Ensure both input_dir and output_dir are Path objects
            if isinstance(input_dir, str):
                input_dir = Path(input_dir)
            if isinstance(output_dir, str):
                output_dir = Path(output_dir)
            output_dir.mkdir(exist_ok=True)
            #Input directory for all files
            for pdf_file in input_dir.glob("*.pdf"):
                # Extract data from pdf files
                data = self._extract_from_pdf(pdf_file)
                # for row in data:
                #     print(data)
                # saving the extracted data to Excel files
                self._save_to_excel(data, output_dir / f"{pdf_file.stem}.xlsx") # file name same with .xlsx extension
                self.stats["invoices_processed"] += 1
                # print(data)
                self.db.insert_invoices_batch(data)
                self.db.export_to_excel()

                # for row in data:
                #     # self.db.insert_invoices_batch(row)
                #     print(row)
                
                # self._save_to_sqlite(data)
        except Exception as e:
            self.logger.error(f"Batch processing failed ! {str(e)}")
            raise

    def _extract_from_pdf(self, pdf_file : Path) -> List[Dict]:
        data = []
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                # tables = page.crop(page_bbox).extract_tables()
                if tables:
                    for table in tables:
                        cleaned = self._clean_table_data(table)
                        data.extend(cleaned)
                        self.stats["tables_extracted"]
                # text = page.extract_text()
                # if text:
                #     parsed = self._parse_unstructured_text(text)
                #     data.extend(parsed)
        return data
    
    def _save_to_excel(self, data : List[Dict], output_path : Path) -> None:
        df = pd.DataFrame(data)
        with pd.ExcelWriter(output_path) as writer:
            df.to_excel(writer, index = False)
        self.logger.info(f"Saved invoice data: {output_path}")
    def _save_to_sqlite(self, data : List[Dict]):
        import sqlite3
        conn = sqlite3.connect("invoices.db")
        pd.DataFrame(data).to_sql("invoices",conn)
    
    def _clean_table_data(self, table : List[List[str]]) -> List[Dict]:
        "Clean and Normalize extracted data from pdf file"
        detected_vendor = []
        #Remove empty rows
        table = [row for row in table if any(cell.strip() for cell in row if cell)]
        # Normalize headers
        headers = [cell.strip() for cell in table[0]]
        # ensure consistent row length
        table = [row + [""] * (len(headers) - len(row)) for row in table[1:]]
        #covert data types
        for row in table:
            for i, cell in enumerate(row):
                cell = cell.strip()  # Clean leading/trailing whitespace
                if cell == "": # Preserve empty cells
                    continue
                if re.match(r"^\d+$", cell):
                    row[i] = int(cell) # convert to integer 
                elif re.match(r"^\d+\.\d+$",cell):
                    row[i] = float(cell) # convert to float
                elif re.match(r"^[\$£€]\d+\.\d+$", cell): #currency symbol $
                    row[i] = float(re.sub(r"^[\$£€]", "", cell))
                elif re.match(r"\d{1,2}/\d{1,2}/\d{4}|\d{4}-\d{2}-\d{2}", cell):
                    row[i] = datetime.strptime(cell, "%Y-%m-%d").date()  # Adjust format as needed
            vendor = self._detect_vendor(cell)
            detected_vendor.append(vendor)
        # Handle merged cells
        for row in table:
            for i, cell in enumerate(row):
                if not cell and i > 0: # it is not first cell and cell value is zero
                    row[i] = row[i - 1] # insert value of the previous cell
        #combine headers and row
        cleaned_table = [dict(zip(headers,row)) for row in table]
        return cleaned_table
    def _detect_vendor(self,text:str) -> str:
        patterns = {
        "Amazon": r"amazon\.com/invoice",
        "Stripe": r"stripe\s+invoice",
        "PayPal": r"paypal\.com/invoice"
        }
        for vendor, pattern in patterns.items():
            if re.search(pattern,text,re.IGNORECASE):
                return vendor
        return "unknown"

    
    def _parse_unstructured_text(self, text:str) -> List[Dict[str,str]]:
        """
        Parse unstructured text to extract structured information like email, phone, dates, etc.
        Args:
            text (str): The unstructured text to parse.
        Returns:
            List[Dict[str, str]]: A list of dictionaries with extracted data.

        """

        # Define regex patterns for various types of data
        email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        phone_pattern = r"\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,3}[-.\s]?\d{3,4}(?!\.\d|\d-\d)"
        # date_pattern = r"\d{1,2}/\d{1,2}/\d{4}|\d{4}-\d{2}-\d{2}|\d{2}-\w{3}-\d{4}"
        date_pattern = r"\d{1,2}/\d{1,2}/\d{4}|\d{4}-\d{2}-\d{2}"
        # Extract matches
        emails = re.findall(email_pattern, text)
        phones = re.findall(phone_pattern, text)
        dates = re.findall(date_pattern,text)

        #create a structured list of find informations
        parsed_data = []
        if emails:
            parsed_data.append({"type":"email", "value":emails})
        if phones:
            parsed_data.append({"type":"phones","value":phones})
        if dates:
            parsed_data.append({"type":"dates","value":dates})
        
        # Add unstructured text if needed
        # parsed_data.append({"type":"raw_text","value":text.strip()})

        return parsed_data
    
if __name__ == "__main__":
    prcocessor = InvoiceProcessor()
    prcocessor.process_invoices(r"E:\pdf files",r"E:\excel files" )
    # data = [
    # {"invoice_id": 1, "vendor": "Amazon", "amount": 45.00, "date": "2023-05-25"},
    # {"invoice_id": 2, "vendor": "Stripe", "amount": 30.00, "date": "2023-05-24"}
    # ]
    # prcocessor._save_to_sqlite(data)


