import re
import pandas as pd
from pathlib import Path
import logging
from typing import List, Dict
import re
import logger_util
import pdfplumber

class InvoiceProcessor:
    def __init__(self):
        self.logger = logger_util.LoggerUtility().logger
        # self.logger.info("InvoiceProcessor initialized.")
        self.stats : Dict[str, int] = {
            "invoices_processed" : 0,
            "tables_extracted" : 0,
            "errors" : 0
        }
    def process_invoices(self, input_dir : Path, output_dir : Path) -> None:
        "Batch processing of pdf invoices"
        try:
            output_dir.mkdir(exist_ok=True)
            #Input directory for all files
            for pdf_file in input_dir.glob("*.pdf"):
                # Extract data from pdf files
                data = self._extract_from_pdf(pdf_file)
                # saving the extracted data to Excel files
                self._save_to_excel(data, output_dir / f"{pdf_file.stem}.xlsx") # file name same with .xlsx extension
                self.stats["invoices_processed"] += 1
        except Exception as e:
            self.logger.error(f"Batch processing failed ! {str(e)}")
            raise

    def _extract_from_pdf(self, pdf_file : Path) -> List[Dict]:
        data = []
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                if tables:
                    for table in tables:
                        cleaned = self._clean_table_data(table)
                        data.extend(cleaned)
                        # self.stats["tables_extracted"]
                text = page.extract_text()
                if text and not tables:
                    parsed = self._parse_unstructured_text(text)
                    data.extend(parsed)
        return data
    
    def _save_to_excel(self):
        pass
    def _clean_table_data(self, table):
        return table
    def _parse_unstructured_text(self,text):
        return [{"text" : text}]


    
if __name__ == "__main__":
    prcocessor = InvoiceProcessor()

