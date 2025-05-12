import logging
from .sqlite_handler import SQLiteHandler

logger = logging.getLogger("app_logger")
logger.setLevel(logging.INFO)

if not logger.hasHandlers():
    handler = SQLiteHandler("app/logger/logs.sqlite3")
    formatter = logging.Formatter('%(asctime)s %(levelname)s [%(module)s:%(lineno)d] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
