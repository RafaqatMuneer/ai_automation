import shutil
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

class DownlaodsOrganizer:
    """File Organization tool"""

    def __init__(self):
        self.logger = self._setup_logging()
        
        # categories for file organization
        self.categories: Dict[str, list[str]] ={
            "Documents" : [".pdf",".docx",".txt"],
            "Images" : [".jpg", ".png", "heic"],
            "Archives": [".zip", ".rar"],
            "Spreadsheets": [".xlsx", ".csv"],
            "Code": [".py", ".js", ".json"]
        }
        self.dry_run : bool = False
        self.status : Dict[str, int] = {
            "moved" : 0,
            "skipped" : 0,
            "errors" : 0
        }
    def _setup_logging(self) -> logging.Logger:
        """Configure error logging"""
        #configure logger
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO) # for info and higher level e.g. warning, error
        # File handler to log messages into file
        file_handler = logging.FileHandler("organizer.log") # output log to the file
        file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")) # formatting log output timestamp - level - message
        # Console Handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))
        # Attach Handler to logger for logging message to repective output
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        return logger
    # script to resolve duplicated names
    def _resolve_duplicate(self, target : Path) -> Path:
        "Handling filename conflicts"
        timestamp = datetime.now().strftime("%d%m%Y_%H%M%S")
        return target.with_stem(f"{target.stem}_Duplicated_{timestamp}")

    
if __name__ == "__main__":
    organizer = DownlaodsOrganizer()
    organizer.dry_run = False




