import logging
from .sqlite_handler import SQLiteHandler

logger = logging.getLogger("order_app")
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    sqlite_handler = SQLiteHandler(db_path="app/logger/logs.sqlite3")
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(module)s %(message)s')
    sqlite_handler.setFormatter(formatter)
    logger.addHandler(sqlite_handler) 