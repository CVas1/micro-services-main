import logging
import sqlite3
import threading
import os
from datetime import datetime

class SQLiteHandler(logging.Handler):
    def __init__(self, db_path='logs.sqlite3'):
        super().__init__()
        self.db_path = db_path
        self._lock = threading.Lock()
        self._ensure_table()

    def _ensure_table(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created TEXT,
                    level TEXT,
                    message TEXT,
                    module TEXT,
                    funcName TEXT,
                    lineno INTEGER
                )
            ''')
            conn.commit()

    def emit(self, record):
        try:
            msg = self.format(record)
            with self._lock:
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute(
                        'INSERT INTO logs (created, level, message, module, funcName, lineno) VALUES (?, ?, ?, ?, ?, ?)',
                        (
                            datetime.fromtimestamp(record.created).isoformat(),
                            record.levelname,
                            msg,
                            record.module,
                            record.funcName,
                            record.lineno
                        )
                    )
                    conn.commit()
        except Exception:
            self.handleError(record) 