import logging
import os
import sys

log_level = logging.INFO
try:
    if os.environ['LOG_LEVEL']:
        level = os.environ['LOG_LEVEL']
        if level == 'info':
            log_level = logging.INFO
        elif level == 'debug':
            log_level = logging.DEBUG
except KeyError:
    # log level isn't defined, using INFO
    log_level = logging.INFO
# Configure logger
logger = logging.getLogger(__name__)

logger.setLevel(log_level)

# Create stdout handler
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(log_level)

# Create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Add handler to logger
logger.addHandler(handler)
