"""
Database connection and helper functions
"""
import traceback
from flask import current_app
from ..extensions import mysql

DB_AVAILABLE = False
_db_init_error = None

def test_db_connection(app):
    """Test database connection at startup"""
    global DB_AVAILABLE, _db_init_error
    try:
        with app.app_context():
            cur = mysql.connection.cursor()
            cur.execute("SELECT 1")
            cur.close()
        DB_AVAILABLE = True
        app.logger.info("Database connection successful")
        return True
    except Exception as e:
        _db_init_error = e
        DB_AVAILABLE = False
        app.logger.error("Database connection test failed: %s", e)
        app.logger.debug(traceback.format_exc())
        return False

def db_cursor():
    """Helper to get a cursor; caller must close it in finally.
       Raises RuntimeError with actionable message if DB not available."""
    if not DB_AVAILABLE:
        msg = f"Database is not available. Check MYSQL_HOST / MYSQL_USER / MYSQL_PASSWORD / MYSQL_DB. Original error: {_db_init_error}"
        current_app.logger.error(msg)
        raise RuntimeError(msg)
    return mysql.connection.cursor()
