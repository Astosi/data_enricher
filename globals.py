import logging
import os

from dotenv import load_dotenv
from logger import Logger

load_dotenv()

LOG_DIR = os.getenv('LOG_DIR')

Logger.set_log_dir(LOG_DIR)
