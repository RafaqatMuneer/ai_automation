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
                        self.stats["tables_extracted"]
                text = page.extract_text()
                if text and not tables:
                    parsed = self._parse_unstructured_text(text)
                    data.extend(parsed)
        return data
    
    def _save_to_excel(self, data : List[Dict], output_path : Path) -> None:
        df = pd.date_range(data)
        with pd.ExcelWriter(output_path) as writer:
            df.to_excel(writer, index = False)
        self.logger.info(f"Saved invoice data: {output_path}")
    
    def _clean_table_data(self, table : List[List[str]]) -> List[Dict]:
        "Clean and Normalize extracted data from pdf file"
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
                elif re.match(r"^\$\d+\.\d+$", cell): #currency symbol $
                    row[i] = float(cell.replace("$", ""))
        # Handle merged cells
        for row in table:
            for i, cell in enumerate(row):
                if not cell and i > 0: # it is not first cell and cell value is zero
                    row[i] = row[i - 1] # insert value of the previous cell
        #combine headers and row
        cleaned_table = [dict(zip(headers,row)) for row in table]
        return cleaned_table
    
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
        phone_pattern = r"\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}"
        date_pattern = r"\b(?:\d{1,2}[-/th|st|nd|rd\s])?(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)[\s-]?\d{1,2}[-,]?[\s-]?\d{2,4}\b"
        # Extract matches
        emails = re.findall(email_pattern, text)
        phones = re.findall(phone_pattern, text)
        dates = re.findall(date_pattern,text)

        #create a structured list of find informations
        parsed_data = []
        if emails:
            parsed_data.append({"type":"email", "value":emails})
        if phones:
            parsed_data.append({"types":"phones","value":phones})
        if dates:
            parsed_data.append({"types":"phones","value":dates})
        
        # Add unstructured text if needed
        parsed_data.append({"type":"raw_text","value":text.strip()})

        return parsed_data


    
if __name__ == "__main__":
    prcocessor = InvoiceProcessor()


