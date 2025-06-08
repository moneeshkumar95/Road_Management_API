import logging
from pathlib import Path

# Ensure log directory exists
Path("src/logs").mkdir(parents=True, exist_ok=True)

# Configure logger
logger = logging.getLogger("request_logger")
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler("src/logs/backend.log")

# Formatter as specified
formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(client_ip)s - "%(request_line)s" %(status_code)s [Duration: %(process_time).2f s]'  # noqa: E501
)

file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
