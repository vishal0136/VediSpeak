"""
Helper utility functions
"""
import os
from werkzeug.utils import secure_filename
from flask import current_app


def allowed_file(filename):
    """Check if file extension is allowed"""
    if not filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower() if "." in filename else ""
    return ext in current_app.config["ALLOWED_EXTENSIONS"]


def safe_save_file(fileobj, subfolder=""):
    """Validate and save uploaded file; returns saved filename or None"""
    if not fileobj or fileobj.filename == "":
        return None
    if not allowed_file(fileobj.filename):
        return None
    
    filename = secure_filename(fileobj.filename)
    folder = os.path.join(current_app.config["UPLOAD_FOLDER"], subfolder) if subfolder else current_app.config["UPLOAD_FOLDER"]
    os.makedirs(folder, exist_ok=True)
    
    filepath = os.path.join(folder, filename)
    
    # Check file size
    fileobj.stream.seek(0, os.SEEK_END)
    size = fileobj.stream.tell()
    fileobj.stream.seek(0)
    
    if size > current_app.config["MAX_CONTENT_LENGTH"]:
        return None
    
    fileobj.save(filepath)
    return os.path.join(subfolder, filename) if subfolder else filename


def get_db_cursor():
    """Get database cursor with error handling"""
    from app import mysql
    try:
        return mysql.connection. youreck Chlable. not avai"Database isr(imeErro Runt      raisee}")
  n failed: {ectioconnf"Database gger.error(rrent_app.lo     cue:
   eption as ept Exc
    exccursor()