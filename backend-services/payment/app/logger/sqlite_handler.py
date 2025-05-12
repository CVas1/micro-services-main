import logging
import sqlite3
import os
from datetime import datetime

class SQLiteHandler(logging.Handler):
    def __init__(self, db_path="app/logger/logs.sqlite3"):
        super().__init__()
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created TEXT,
                    level TEXT,
                    message TEXT,
                    module TEXT,
                    funcName TEXT,
                    lineno INTEGER
                )
            """)
            conn.commit()

    def emit(self, record):
        log_entry = self.format(record)
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO logs (created, level, message, module, funcName, lineno)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    datetime.utcfromtimestamp(record.created).isoformat(),
                    record.levelname,
                    record.getMessage(),
                    record.module,
                    record.funcName,
                    record.lineno
                ))
                conn.commit()
        except Exception:
            self.handleError(record)
