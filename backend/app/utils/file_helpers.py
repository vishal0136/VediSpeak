"""
File upload and validation helpers
"""
import os
import io
from flask import current_app
from werkzeug.utils import secure_filename

def allowed_file(filename):
    """Check if file extension is allowed"""
    if not filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower() if "." in filename else ""
    return ext in current_app.config["ALLOWED_EXTENSIONS"]

def safe_save_file(fileobj, subfolder=""):
    """Validate and save uploaded file; returns saved filename or None."""
    if not fileobj or fileobj.filename == "":
        return None
    if not allowed_file(fileobj.filename):
        return None
    
    filename = secure_filename(fileobj.filename)
    folder = os.path.join(current_app.config["UPLOAD_FOLDER"], subfolder) if subfolder else current_app.config["UPLOAD_FOLDER"]
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, filename)
    
    # Check file size
    fileobj.stream.seek(0, io.SEEK_END)
    size = fileobj.stream.tell()
    fileobj.stream.seek(0)
    if size > current_app.config["MAX_CONTENT_LENGTH"]:
        return None
    
    fileobj.save(filepath)
    return os.path.join(subfolder, filename) if subfolder else filename
