"""
Authentication routes: /register, /login, /logout, /send-otp, /verify-otp, /reset-password
"""
import time
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from ..extensions import mysql, bcrypt
from ..models.user import User
from ..models.stats import UserStats
from ..services.auth_service import send_otp_sms, send_otp_email, generate_otp, validate_phone_number
from ..utils.db_helpers import db_cursor

auth_bp = Blueprint("auth", __name__)

def normalize_phone(phone):
    """Normalize phone number to E.164 format"""
    if not phone:
        return None
    digits = "".join(c for c in phone if c.isdigit())
    if len(digits) == 10:
        return "+91" + digits
    return "+" + digits if digits else None

@auth_bp.route("/")
def home():
    """Redirect to dashboard if logged in, otherwise to auth page"""
    if "user_id" in session:
        return redirect(url_for("pages.dashboard"))
    return redirect(url_for("auth.auth_page"))

@auth_bp.route("/auth")
def auth_page():
    """Show login/register page"""
    return render_template("sign-up.html")

@auth_bp.route("/register", methods=["POST"])
def register():
    """Register a new user"""
    # Accept JSON or Form
    data = request.get_json() or request.form
    
    username = data.get("name")
    email = data.get("email")
    password = data.get("password")
    phone = data.get("phone")
    
    if not username or not email or not password:
        return jsonify({"status": "error", "message": "Missing required fields"}), 400
    
    # Normalize phone
    phone_normalized = normalize_phone(phone)
    
    # Check if email exists
    if User.get_by_email(email):
        return jsonify({"status": "error", "message": "Email already registered"}), 409
    
    # Check if phone exists (if provided)
    if phone_normalized and User.get_by_phone(phone_normalized):
        return jsonify({"status": "error", "message": "Phone already registered"}), 409
    
    try:
        # Create user
        hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")
        user_id = User.create(username, email, phone_normalized, hashed_pw)
        
        # Create user stats
        UserStats.create_or_get(user_id)
        
        # Auto-login
        session["user_id"] = user_id
        session["username"] = username
        
        return jsonify({"status": "success", "message": "Registration successful"})
    except Exception as e:
        return jsonify({"status": "error", "message": "Registration failed"}), 500

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Login user or show login page"""
    if request.method == "GET":
        return render_template("sign-up.html")
    
    # Handle POST request for login
    # Accept JSON or Form
    data = request.get_json() or request.form
    
    email = data.get("email")
    password = data.get("password")
    
    if not email or not password:
        return jsonify({"status": "error", "message": "Email and password are required"}), 400
    
    user = User.get_by_email(email)
    
    if not user:
        return jsonify({"status": "error", "message": "Invalid email or password"}), 401
    
    # Debug logging
    from flask import current_app
    current_app.logger.debug(f"User found: {user['username']}")
    current_app.logger.debug(f"Password hash type: {type(user['password'])}")
    current_app.logger.debug(f"Password hash length: {len(user['password'])}")
    current_app.logger.debug(f"Password hash: {user['password'][:30]}...")
    
    if not bcrypt.check_password_hash(user["password"], password):
        return jsonify({"status": "error", "message": "Invalid email or password"}), 401
    
    # Successful login
    session["user_id"] = user["id"]
    session["username"] = user["username"]
    
    # Update login stats
    UserStats.update_login(user["id"])
    
    return jsonify({"status": "success", "message": "Login successful"})

@auth_bp.route("/logout")
def logout():
    """Logout user"""
    session.clear()
    flash("Logged out", "info")
    return redirect(url_for("auth.auth_page"))

@auth_bp.route("/send-otp", methods=["POST"])
def send_otp_route():
    """Send OTP to user's phone or email"""
    data = request.get_json() or request.form
    
    email = (data.get("email") or "").strip() or None
    phone = normalize_phone(data.get("phone"))
    
    if not phone and not email:
        return jsonify({"error": "Email or phone required"}), 400
    
    # Find user
    if phone:
        user = User.get_by_phone(phone)
    elif email:
        user = User.get_by_email(email)
    else:
        return jsonify({"status": "error", "message": "Email or phone required"}), 400
    
    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404
    
    # Generate OTP
    otp = str(int(time.time()) % 1000000).zfill(6)
    otp_expiry = datetime.utcnow() + timedelta(minutes=5)
    
    # Save OTP to database
    User.update_otp(user["id"], otp, otp_expiry)
    
    # Send OTP
    ok_sms = False
    ok_email = False
    messages = []
    
    if phone:
        ok_sms = send_otp_sms(phone, otp)
        messages.append(f"SMS {'sent' if ok_sms else 'failed'}")
    
    if email or user.get("email"):
        ok_email = send_otp_email(email or user["email"], otp)
        messages.append(f"Email {'sent' if ok_email else 'failed'}")
    
    # Store user ID in session for verification
    session["otp_user_id"] = user["id"]
    
    ok_any = ok_sms or ok_email
    return jsonify({
        "status": "success" if ok_any else "error",
        "message": " | ".join(messages)
    })

@auth_bp.route("/verify-otp", methods=["POST"])
def verify_otp():
    """Verify OTP code"""
    data = request.get_json() or request.form
    otp = data.get("otp")
    
    uid = session.get("otp_user_id")
    if not uid:
        return jsonify({"status": "error", "message": "No OTP session found"}), 400
    
    user = User.get_by_id(uid)
    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404
    
    otp_code = user.get("otp_code")
    otp_expiry = user.get("otp_expiry")
    
    if not otp_code or otp != otp_code:
        return jsonify({"status": "error", "message": "Invalid OTP"}), 400
    
    if not otp_expiry or datetime.utcnow() > otp_expiry:
        return jsonify({"status": "error", "message": "OTP expired"}), 400
    
    # OTP verified successfully
    session["otp_verified_user_id"] = uid
    return jsonify({"status": "success", "message": "OTP verified"})

@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    """Reset user password after OTP verification"""
    uid = session.get("otp_verified_user_id")
    if not uid:
        return jsonify({"status": "error", "message": "OTP not verified"}), 400
    
    data = request.get_json() or request.form
    new_pw = data.get("new_password")
    
    if not new_pw:
        return jsonify({"status": "error", "message": "Password required"}), 400
    
    # Hash password
    hashed = bcrypt.generate_password_hash(new_pw).decode("utf-8")
    
    # Update password and clear OTP
    cur = None
    try:
        cur = db_cursor()
        cur.execute("""
            UPDATE users 
            SET password=%s, otp_code=NULL, otp_expiry=NULL 
            WHERE id=%s
        """, (hashed, uid))
        mysql.connection.commit()
    finally:
        if cur:
            cur.close()
    
    # Clear OTP session data
    session.pop("otp_verified_user_id", None)
    session.pop("otp_user_id", None)
    
    return jsonify({"status": "success", "message": "Password updated successfully"})

@auth_bp.route("/google_login")
def google_login():
    """Handle Google OAuth login"""
    try:
        from flask_dance.contrib.google import google
        
        if not google.authorized:
            return redirect(url_for("google.login"))
        
        info = google.get("/oauth2/v2/userinfo").json()
        email = info.get("email")
        name = info.get("name")
        gid = info.get("id")
        
        # Check if user exists
        user = User.get_by_oauth("google", gid)
        
        if not user:
            # Check by email
            user = User.get_by_email(email)
            
            if not user:
                # Create new user
                import os
                random_pw = bcrypt.generate_password_hash(os.urandom(8)).decode("utf-8")
                user_id = User.create(name, email, None, random_pw, "google", gid)
                UserStats.create_or_get(user_id)
                username = name
            else:
                user_id = user["id"]
                username = user["username"]
        else:
            user_id = user["id"]
            username = user["username"]
        
        session["user_id"] = user_id
        session["username"] = username
        
        flash("Logged in via Google", "success")
        return redirect(url_for("pages.dashboard"))
    except Exception as e:
        flash("Google login failed", "danger")
        return redirect(url_for("auth.auth_page"))
