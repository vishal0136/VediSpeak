"""
Custom decorators for authentication and authorization
"""
from functools import wraps
from flask import session, redirect, url_for, flash, jsonify, request


def login_required(f):
    """Require user to be logged in"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            if request.is_json or "/api/" in request.path:
                return jsonify({"error": "Authentication required"}), 401
            flash("⚠️ Please log in first", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function


def anonymous_required(f):
    """Require user to NOT be logged in (for login/register pages)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" in session:
            return redirect(url_for("main.dashboard"))
        return f(*args, **kwargs)
    return decorated_function
