"""Logs endpoints."""
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from db.dependencies import get_db
from datetime import datetime, timedelta
from typing import Optional, List
from logger import logger
import sqlite3
from pydantic import BaseModel
from api.dependencies import admin_auth_dependency

router = APIRouter(
    prefix="/logs",
    tags=["logs"]
)

class LogEntry(BaseModel):
    id: int
    created: str
    level: str
    message: str
    module: str
    funcName: str
    lineno: int

class LogStats(BaseModel):
    total_logs: int
    level_counts: dict
    recent_errors_24h: int
    module_counts: dict

@router.get("/", response_model=List[LogEntry], dependencies=[Depends(admin_auth_dependency)])
def get_logs(
    level: Optional[str] = Query(None, description="Filter logs by level (INFO, WARNING, ERROR)"),
    start_date: Optional[str] = Query(None, description="Filter logs from this date (ISO format)"),
    end_date: Optional[str] = Query(None, description="Filter logs until this date (ISO format)"),
    module: Optional[str] = Query(None, description="Filter logs by module name"),
    search: Optional[str] = Query(None, description="Search in log messages"),
    page: int = Query(1, description="Page number", ge=1),
    page_size: int = Query(50, description="Number of logs per page", ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Retrieve logs with optional filtering by level, date range, module, and search term.
    Supports pagination.
    """
    try:
        conn = sqlite3.connect("app/logger/logs.sqlite3")
        cursor = conn.cursor()

        # Base query
        query = "SELECT id, created, level, message, module, funcName, lineno FROM logs"
        count_query = "SELECT COUNT(*) FROM logs"
        params = []
        conditions = []

        # Add filters if provided
        if level:
            conditions.append("level = ?")
            params.append(level.upper())

        if start_date:
            conditions.append("created >= ?")
            params.append(start_date)

        if end_date:
            conditions.append("created <= ?")
            params.append(end_date)

        if module:
            conditions.append("module = ?")
            params.append(module)

        if search:
            conditions.append("message LIKE ?")
            params.append(f"%{search}%")

        # Combine conditions
        if conditions:
            where_clause = " WHERE " + " AND ".join(conditions)
            query += where_clause
            count_query += where_clause

        # Get total count
        cursor.execute(count_query, params)
        total_count = cursor.fetchone()[0]

        # Add ordering and pagination
        offset = (page - 1) * page_size
        query += " ORDER BY created DESC LIMIT ? OFFSET ?"
        params.extend([page_size, offset])

        # Execute query
        cursor.execute(query, params)
        logs = cursor.fetchall()

        # Convert to list of dictionaries
        log_entries = [
            LogEntry(
                id=log[0],
                created=log[1],
                level=log[2],
                message=log[3],
                module=log[4],
                funcName=log[5],
                lineno=log[6]
            )
            for log in logs
        ]

        conn.close()
        return log_entries

    except Exception as e:
        logger.error(f"Error retrieving logs: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while retrieving logs: {str(e)}"
        )

@router.get("/levels", response_model=List[str], dependencies=[Depends(admin_auth_dependency)])
def get_log_levels():
    """
    Retrieve all log levels that have been used in the logs.
    """
    try:
        conn = sqlite3.connect("app/logger/logs.sqlite3")
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT level FROM logs ORDER BY level")
        levels = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return levels
    except Exception as e:
        logger.error(f"Error retrieving log levels: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while retrieving log levels: {str(e)}"
        )

@router.get("/modules", response_model=List[str], dependencies=[Depends(admin_auth_dependency)])
def get_modules():
    """
    Retrieve all modules that have generated logs.
    """
    try:
        conn = sqlite3.connect("app/logger/logs.sqlite3")
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT module FROM logs ORDER BY module")
        modules = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return modules
    except Exception as e:
        logger.error(f"Error retrieving modules: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while retrieving modules: {str(e)}"
        )

@router.get("/stats", response_model=LogStats, dependencies=[Depends(admin_auth_dependency)])
def get_log_stats():
    """
    Get statistics about the logs (count by level, recent errors, module counts, etc.).
    """
    try:
        conn = sqlite3.connect("app/logger/logs.sqlite3")
        cursor = conn.cursor()

        # Get count by level
        cursor.execute("""
            SELECT level, COUNT(*) as count 
            FROM logs 
            GROUP BY level
        """)
        level_counts = {row[0]: row[1] for row in cursor.fetchall()}

        # Get count by module
        cursor.execute("""
            SELECT module, COUNT(*) as count 
            FROM logs 
            GROUP BY module
        """)
        module_counts = {row[0]: row[1] for row in cursor.fetchall()}

        # Get recent errors (last 24 hours)
        yesterday = (datetime.now() - timedelta(days=1)).isoformat()
        cursor.execute("""
            SELECT COUNT(*) 
            FROM logs 
            WHERE level = 'ERROR' AND created >= ?
        """, (yesterday,))
        recent_errors = cursor.fetchone()[0]

        # Get total log count
        cursor.execute("SELECT COUNT(*) FROM logs")
        total_logs = cursor.fetchone()[0]

        conn.close()

        return LogStats(
            total_logs=total_logs,
            level_counts=level_counts,
            recent_errors_24h=recent_errors,
            module_counts=module_counts
        )

    except Exception as e:
        logger.error(f"Error retrieving log statistics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while retrieving log statistics: {str(e)}"
        ) 