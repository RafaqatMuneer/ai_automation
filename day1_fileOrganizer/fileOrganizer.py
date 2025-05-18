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
            "Images" : [".jpeg", ".png", "heic"],
            "Archives": [".zip", ".rar"],
            "Spreadsheets": [".xlsx", ".csv"],
            "Code": [".py", ".js", ".json"],
            "Softwares" : [".exe"]
        }
        self.dry_run : bool = False
        self.stats : Dict[str, int] = {
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
        timestamp = datetime.now().strftime("%d%m%Y_%H%M%S") # current time with string formatting
        return target.with_stem(f"{target.stem}_Duplicated_{timestamp}") #stem method to get filenmae without extension
  
    def _should_skip(self, file : Path) -> bool:
        "Logic for file retention, skipping files"
        #SKip files that are modified in last 24 hours
        last_modified = datetime.fromtimestamp(file.stat().st_mtime)
        if datetime.now() - last_modified < timedelta(hours=24):
            return True
        # Skip system and hidden files
        if file.name.startswith(".") or file.name.startswith("~") or file.suffix.lower() == ".ini":
            return True
        return False
    def organize(self, source : Optional[Path] = None) -> None:
        # Main file organization workflow
        source = source or Path.home() / "Downloads"
        self.logger.info(f"Starting orgnization of {source}")

        try:
            # Create categories folders first
            for category in self.categories:
                (source / category).mkdir(exist_ok=True)  # appending category subdirectory to the source
            # processing files in source folder
            for item in source.iterdir():
                if self._should_skip(item):
                    self.stats["skipped"] += 1
                    continue
                if item.is_file():
                    dest_category = "Others"
                    for category, exts in self.categories.items():
                        if item.suffix.lower() in exts:
                            dest_category = category
                            break
                    dest_path = source / dest_category / item.name
                    # Handle duplicate file name
                    if dest_path.exists():
                        dest_path = self._resolve_duplicate(dest_path)
                    # Execute move
                    if not self.dry_run:
                        try:
                            shutil.move(str(item),str(dest_path))
                            self.stats["moved"] += 1
                            self.logger.info(f"Moved: {item.name} -> {dest_category}")

                        except Exception as e:
                            self.stats["errors"] += 1
                            self.logger.error(f"Failed {item.name} : {str(e)}")

        finally:
            # Always print summary
            self.logger.info(
                f"Operation complete. Moved: {self.stats['moved']}, "
                f"Skipped: {self.stats['skipped']}, Errors: {self.stats['errors']}"
            )

    
if __name__ == "__main__":
    organizer = DownlaodsOrganizer()
   # Enable dry-run mode for testing
    organizer.dry_run = False  
    organizer.organize()



