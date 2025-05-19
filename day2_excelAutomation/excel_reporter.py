import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.chart import BarChart, Reference
import logging
from typing import Dict, List
from openpyxl.utils.dataframe import dataframe_to_rows
from pathlib import Path
import requests

class ExcelReportGenerator:
    def __init__(self):
        self.logger = self._setup_logger()
        # self.logger.info(f"Starting orgnization of ")
        self.stats = {"sheets": 0, "charts": 0, "backups": 0}
    def _setup_logger(self) -> logging.Logger:
        "The Logging Configuration"
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO) # logging level info and higher order
        handler = logging.FileHandler("excel_automation.log")
        handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")) # formatting log output timestamp - level - message
        logger.addHandler(handler)
        return logger
    
    def fetch_data(self) -> pd.DataFrame:
        # return pd.DataFrame({
        #     "Product": ["Widget A", "Widget B", "Widget C"],
        #     "Q1 Sales": [45000, 56000, 89000],
        #     "Q2 Sales": [51000, 63000, 92000]
        # })
        """Fetch data from fakestore API"""
        url = "https://fakestoreapi.com/products"
        response = requests.get(url)
        if response.status_code != 200:
            logging.error(f"API call failed with status {response.status_code}")
        return pd.DataFrame(response.json())
    
    def _flatten_dict_columns(self) -> pd.DataFrame:
        df = self.fetch_data()
        for col in df.columns:
            # Check if the first row is a dictionary
            if isinstance(df[col].iloc[0], dict):  
                # Expand the dictionary into separate columns
                dict_df = pd.json_normalize(df[col])
                dict_df.columns = [f"{col}_{subcol}" for subcol in dict_df.columns]  # Rename columns
                df = df.drop(columns=[col]).join(dict_df)  # Drop the original column and join expanded columns
        return df

    def create_report(self, output_path: Path) -> None:
        "Generate Excel report"
        try:
            data = self._flatten_dict_columns()
            with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
                data.to_excel(writer,sheet_name="Sales Data", index=False)
                self.stats["sheets"] += 1
                #Summary sheet
                workbook = writer.book
                self._add_summary_sheet(workbook, data)
            self.logger.info(f"Report generated: {output_path}")
        except Exception as e:
            self.logger.error(f"Report failed: {str(e)}")
            raise
    # summary sheet of excel workbook
    def _add_summary_sheet(self, workbook : Workbook, data: pd.DataFrame) -> None:
        "Add formatted summary with chart"
        ws = workbook.create_sheet("Executive Summary")
        # Header
        ws["A1"] = "Quarterly Sales Report"
        ws["A1"].font = Font(bold= True, size=14)
        # for row in data.itertuples():
        #     ws.append(row[1:])
        for row in dataframe_to_rows(data, index=False, header=True):
            ws.append(row)
        chart = BarChart()
        chart.title = "Product performance report"
        # chart.style = 4
        values = Reference(ws, min_col=2, max_col=ws.max_column, min_row=1, max_row=ws.max_row)
        # categories = Reference(ws, min_col=1, min_row=2, max_row=ws.max_row)

        chart.add_data(values, titles_from_data=True)
        # chart.set_categories(categories)
        ws.add_chart(chart, "E2")
        self.stats["charts"] += 1
if __name__ == "__main__":
    generator = ExcelReportGenerator()
    # Generate investor-ready report
    generator.create_report(Path("Q2_Sales_Report.xlsx"))   
    # Log performance metrics
    generator.logger.info(f"Charts generated: {generator.stats['charts']}")

