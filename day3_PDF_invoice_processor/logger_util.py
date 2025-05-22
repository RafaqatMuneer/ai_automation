import logging
# logging logic for info and above
class LoggerUtility:
    def __init__(self):
        self.logger = self.setup_logger()
        
    def setup_logger(self) -> logging.Logger:
        logger = logging.getLogger(__name__)
        if not logger.handlers: # Avoid adding multiple handlers
            logger.setLevel(logging.INFO)
            #File Handler
            file_handler = logging.FileHandler("processor.log")
            file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")) # formatting log output timestamp - level - message
            logger.addHandler(file_handler)
            # Console Handler
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))
            logger.addHandler(console_handler)

        return logger
if __name__ == "__main__":
    logger_utility = LoggerUtility()
    logger = logger_utility.logger
    # logger.info("Logger setup")
    
    
