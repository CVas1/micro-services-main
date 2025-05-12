import sqlite3
import threading
from datetime import datetime
import inspect

class SQLiteLogger:
    def __init__(self, db_path="logs.db"):
        self.db_path = db_path
        self._lock = threading.Lock()
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    level TEXT NOT NULL,
                    message TEXT NOT NULL,
                    module TEXT NOT NULL,
                    funcName TEXT,
                    lineno INTEGER
                )
            ''')
            conn.commit()

    def log(self, message, level="INFO"):
        timestamp = datetime.utcnow().isoformat()
        
        # Get caller information
        frame = inspect.currentframe().f_back
        module = frame.f_globals.get('__name__', 'unknown')
        func_name = frame.f_code.co_name
        line_no = frame.f_lineno
        
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT INTO logs (timestamp, level, message, module, funcName, lineno) VALUES (?, ?, ?, ?, ?, ?)",
                    (timestamp, level, message, module, func_name, line_no)
                )
                conn.commit()

# Singleton logger instance
logger = SQLiteLogger() 