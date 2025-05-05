# config.py or wherever you have your logging setup

import logging
from config import REPO_ROOT  # Import REPO_ROOT from config.py

def setup_logging():
    log_file_path = REPO_ROOT / "pipeline_log.txt"  # Dynamically set the log file path inside the repo
    
    logging.basicConfig(
        filename=log_file_path,  # Path to your log file
        level=logging.INFO,  # Log everything at INFO level and above
        format='%(asctime)s - %(message)s'  # Format with a timestamp
    )
