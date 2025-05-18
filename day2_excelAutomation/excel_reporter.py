import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.chart import BarChart, Reference
import logging
from typing import Dict, List
from openpyxl.utils.dataframe import dataframe_to_rows
from pathlib import Path

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
        # data = {
        #     "Product": ["Widget A", "Widget B", "Widget C"],
        #     "Q1 Sales": [45000, 56000, 89000],
        #     "Q2 Sales": [51000, 63000, 92000]
        # }
        return pd.DataFrame({
            "Product": ["Widget A", "Widget B"],
            "Q1 Sales": [45000, 56000],
            "Q2 Sales": [51000, 63000]
        })
    def create_report(self, output_path: Path) -> None:
        "Generate Excel report"
        try:
            data = self.fetch_data()
            # print(data)
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
        for row in data.itertuples():
            ws.append(row[1:])
        chart = BarChart()
        chart.title = "Product performance report"
        values = Reference(ws, min_col=2, max_col=3, min_row=1, max_row=3)
        categories = Reference(ws, min_col=1, min_row=2, max_row=ws.max_row)

        chart.add_data(values, titles_from_data=True)
        chart.set_categories(categories)
        ws.add_chart(chart, "E2")
        self.stats["charts"] += 1
    # def _add_summary_sheet(self, workbook: Workbook, data: pd.DataFrame) -> None:
    #     """Formatted summary with charts"""
    #     ws = workbook.create_sheet("Summary")
        
    #     # Header
    #     ws["A1"] = "Quarterly Performance"
    #     ws["A1"].font = Font(bold=True, size=14)
        
    #     # Data
    #     for row in data.itertuples():
    #         ws.append(row[1:])  # Skip index
            
    #     # Chart
    #     chart = BarChart()
    #     chart.title = "Sales by Quarter"
    #     values = Reference(ws, min_col=2, max_col=3, min_row=1, max_row=3)
    #     chart.add_data(values, titles_from_data=True)
    #     ws.add_chart(chart, "E2")
    #     self.stats["charts"] += 1
if __name__ == "__main__":
    generator = ExcelReportGenerator()
     # 1. Get business data
    # sales_data = generator.fetch_data("erp_system")
    
    # 2. Generate investor-ready report
    generator.create_report(Path("Q2_Sales_Report.xlsx"))
    
    # 3. Log performance metrics
    generator.logger.info(f"Charts generated: {generator.stats['charts']}")

