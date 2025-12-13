"""
Enhanced Profile routes with real-time features and API endpoints
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_socketio import emit, join_room, leave_room
from datetime import datetime, timedelta
import json
from ..extensions import mysql, socketio
from ..models.user import User
from ..models.portfolio import PortfolioLink
from ..models.stats import UserStats, UserActivity
from ..utils.decorators import login_required
from ..utils.file_helpers import safe_save_file
from ..utils.db_helpers import db_cursor

profile_bp = Blueprint("profile", __name__)

@profile_bp.route("/user-profile")
@login_required
def user_profile():
    """Enhanced user profile page with real-time features"""
    from ..models.courses import UserProgress
    from ..models.achievements import Achievement
    
    uid = session["user_id"]
    
    # Get user details
    user = User.get_by_id(uid)
    
    # Get portfolio links
    links = PortfolioLink.get_user_links(uid)
    
    # Get user statistics
    stats = UserActivity.get_user_stats(uid)
    today_stats = UserActivity.get_today_stats(uid)
    
    # Merge today's stats with overall stats
    stats.update(today_stats)
    
    # Get learning statistics
    learning_stats = UserProgress.get_user_overall_stats(uid)
    
    # Get module-specific progress for skill development
    for i in range(1, 7):  # Modules 1-6
        module_progress = UserProgress.get_user_module_progress(uid, i)
        learning_stats[f'module_{i}_progress'] = module_progress.get('progress_percentage', 0) if module_progress else 0
    
    # Get recent activities
    activities = UserActivity.get_recent_activities(uid, limit=10)
    
    # Get tasks
    tasks = UserActivity.get_user_tasks(uid)
    
    # Get achievements
    achievements = Achievement.get_user_achievements(uid) if hasattr(Achievement, 'get_user_achievements') else []
    
    # Calculate weekly stats
    weekly_progress = UserActivity.get_weekly_progress(uid)
    if weekly_progress:
        weekly_hours = sum([day.get('study_minutes', 0) for day in weekly_progress.get('activity', [])]) / 60
        weekly_tasks = sum([day.get('completed_tasks', 0) for day in weekly_progress.get('tasks', [])])
        weekly_xp = stats.get('points', 0) * 0.1  # Estimate weekly XP
        
        stats.update({
            'weekly_hours': round(weekly_hours, 1),
            'weekly_tasks': weekly_tasks,
            'weekly_xp': int(weekly_xp)
        })
    
    return render_template(
        "profile/user-profile.html",
        username=session.get("username"),
        user=user,
        links=links,
        stats=stats,
        learning_stats=learning_stats,
        activities=activities,
        tasks=tasks,
        achievements=achievements,
        active_page="user_profile",
        show_sidebar=True
    )

@profile_bp.route("/update_profile", methods=["POST"])
@login_required
def update_profile():
    """Update user profile"""
    uid = session["user_id"]
    data = request.form
    
    profession = data.get("profession")
    bio = data.get("bio")
    photo = request.files.get("profile_photo")
    resume = request.files.get("resume")
    
    # Handle photo upload
    photo_name = None
    if photo and photo.filename:
        photo_name = safe_save_file(photo, subfolder=f"user_{uid}")
    
    # Handle resume upload
    resume_name = None
    if resume and resume.filename:
        resume_name = safe_save_file(resume, subfolder=f"user_{uid}")
    
    # Update user profile
    User.update_profile(
        uid,
        profession=profession,
        bio=bio,
        profile_photo=photo_name,
        resume_path=resume_name
    )
    
    flash("Profile updated successfully!", "success")
    return redirect(url_for("profile.user_profile"))

@profile_bp.route("/add_link", methods=["POST"])
@login_required
def add_link():
    """Add portfolio link"""
    uid = session["user_id"]
    platform = request.form.get("platform", "")
    url = request.form.get("url", "")
    
    if platform and url:
        PortfolioLink.create(uid, platform, url)
        flash("Portfolio link added successfully!", "success")
    else:
        flash("Platform and URL are required", "warning")
    
    return redirect(url_for("profile.user_profile"))

@profile_bp.route("/settings")
@login_required
def settings():
    """User settings page with real-time stats and profile management"""
    from ..models.courses import UserProgress
    
    uid = session["user_id"]
    
    # Get user details
    user = User.get_by_id(uid)
    
    # Get comprehensive statistics
    stats = UserActivity.get_user_stats(uid)
    today_stats = UserActivity.get_today_stats(uid)
    
    # Get learning statistics
    learning_stats = UserProgress.get_user_overall_stats(uid)
    
    # Get weekly progress for graphs
    weekly_progress = UserActivity.get_weekly_progress(uid)
    
    # Get recent activities
    activities = UserActivity.get_recent_activities(uid, limit=15)
    
    # Get portfolio links
    links = PortfolioLink.get_user_links(uid)
    
    # Get streak information
    streak_data = UserActivity.get_streak_details(uid)
    
    return render_template(
        "profile/settings.html",
        username=session.get("username"),
        user=user,
        session=session,
        stats=stats,
        today_stats=today_stats,
        learning_stats=learning_stats,
        weekly_progress=weekly_progress,
        activities=activities,
        links=links,
        streak_data=streak_data,
        active_page="settings",
        show_sidebar=True
    )

# =====================================
# API ENDPOINTS FOR REAL-TIME FEATURES
# =====================================

@profile_bp.route("/api/profile/upload_photo", methods=["POST"])
@login_required
def upload_profile_photo():
    """Upload profile photo via API"""
    uid = session["user_id"]
    
    try:
        if 'profile_photo' not in request.files:
            return jsonify({"success": False, "error": "No file provided"}), 400
        
        photo = request.files['profile_photo']
        
        if photo.filename == '':
            return jsonify({"success": False, "error": "No file selected"}), 400
        
        # Validate file type
        allowed_extensions = {'png', 'jpg', 'jpeg', 'webp'}
        if not photo.filename or '.' not in photo.filename:
            return jsonify({"success": False, "error": "Invalid file type"}), 400
        
        ext = photo.filename.rsplit('.', 1)[1].lower()
        if ext not in allowed_extensions:
            return jsonify({"success": False, "error": "Only PNG, JPG, JPEG, and WebP files are allowed"}), 400
        
        # Save the file
        photo_name = safe_save_file(photo, subfolder=f"user_{uid}")
        
        if not photo_name:
            return jsonify({"success": False, "error": "Failed to save file"}), 500
        
        # Update user profile
        User.update_profile(uid, profile_photo=photo_name)
        
        # Emit real-time update
        socketio.emit("profile_photo_updated", {
            "user_id": uid,
            "photo_url": f"/storage/uploads/{photo_name}",
            "timestamp": datetime.now().isoformat()
        }, room=f"user_{uid}")
        
        # Log activity
        UserActivity.log_activity(uid, "profile_updated", "Updated profile photo", 5)
        
        return jsonify({
            "success": True,
            "message": "Profile photo updated successfully",
            "photo_url": f"/storage/uploads/{photo_name}"
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@profile_bp.route("/api/profile/stats")
@login_required
def get_profile_stats():
    """Get real-time profile statistics"""
    uid = session["user_id"]
    
    try:
        stats = UserActivity.get_user_stats(uid)
        today_stats = UserActivity.get_today_stats(uid)
        
        return jsonify({
            "success": True,
            "data": {
                "total_hours": stats.get("total_hours", 0),
                "completed_tasks": stats.get("completed_tasks", 0),
                "active_sessions": stats.get("active_sessions", 0),
                "streak_days": stats.get("streak_days", 0),
                "today": today_stats
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@profile_bp.route("/api/profile/tasks", methods=["GET"])
@login_required
def get_tasks():
    """Get user tasks"""
    uid = session["user_id"]
    
    try:
        tasks = UserActivity.get_user_tasks(uid)
        return jsonify({
            "success": True,
            "data": tasks
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@profile_bp.route("/api/profile/tasks", methods=["POST"])
@login_required
def create_task():
    """Create a new task"""
    uid = session["user_id"]
    data = request.get_json()
    
    try:
        task_id = UserActivity.create_task(
            uid,
            data.get("text"),
            data.get("priority", "medium")
        )
        
        # Emit real-time update
        socketio.emit("task_created", {
            "task_id": task_id,
            "text": data.get("text"),
            "priority": data.get("priority", "medium"),
            "user_id": uid
        }, room=f"user_{uid}")
        
        # Log activity
        UserActivity.log_activity(uid, "task_created", f"Created task: {data.get('text')}")
        
        return jsonify({
            "success": True,
            "data": {"task_id": task_id}
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@profile_bp.route("/api/profile/tasks/<int:task_id>", methods=["PUT"])
@login_required
def update_task(task_id):
    """Update task status"""
    uid = session["user_id"]
    data = request.get_json()
    
    try:
        UserActivity.update_task(task_id, uid, data)
        
        # Emit real-time update
        socketio.emit("task_updated", {
            "task_id": task_id,
            "updates": data,
            "user_id": uid
        }, room=f"user_{uid}")
        
        # Log activity if task completed
        if data.get("completed"):
            UserActivity.log_activity(uid, "task_completed", f"Completed task ID: {task_id}")
        
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@profile_bp.route("/api/profile/tasks/<int:task_id>", methods=["DELETE"])
@login_required
def delete_task(task_id):
    """Delete a task"""
    uid = session["user_id"]
    
    try:
        UserActivity.delete_task(task_id, uid)
        
        # Emit real-time update
        socketio.emit("task_deleted", {
            "task_id": task_id,
            "user_id": uid
        }, room=f"user_{uid}")
        
        # Log activity
        UserActivity.log_activity(uid, "task_deleted", f"Deleted task ID: {task_id}")
        
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@profile_bp.route("/api/profile/activities")
@login_required
def get_activities():
    """Get recent activities"""
    uid = session["user_id"]
    limit = request.args.get("limit", 20, type=int)
    
    try:
        activities = UserActivity.get_recent_activities(uid, limit)
        return jsonify({
            "success": True,
            "data": activities
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@profile_bp.route("/api/profile/weekly-progress")
@login_required
def get_weekly_progress():
    """Get weekly progress data for charts"""
    uid = session["user_id"]
    
    try:
        weekly_data = UserActivity.get_weekly_progress(uid)
        return jsonify({
            "success": True,
            "data": weekly_data
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@profile_bp.route("/api/profile/session/start", methods=["POST"])
@login_required
def start_session():
    """Start a focus session"""
    uid = session["user_id"]
    data = request.get_json()
    
    try:
        session_id = UserActivity.start_session(uid, data.get("type", "study"))
        
        # Emit real-time update
        socketio.emit("session_started", {
            "session_id": session_id,
            "user_id": uid,
            "start_time": datetime.now().isoformat()
        }, room=f"user_{uid}")
        
        # Log activity
        UserActivity.log_activity(uid, "session_started", f"Started {data.get('type', 'study')} session")
        
        return jsonify({
            "success": True,
            "data": {"session_id": session_id}
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@profile_bp.route("/api/profile/session/<int:session_id>/end", methods=["POST"])
@login_required
def end_session(session_id):
    """End a focus session"""
    uid = session["user_id"]
    
    try:
        duration = UserActivity.end_session(session_id, uid)
        
        # Emit real-time update
        socketio.emit("session_ended", {
            "session_id": session_id,
            "user_id": uid,
            "duration": duration,
            "end_time": datetime.now().isoformat()
        }, room=f"user_{uid}")
        
        # Log activity
        UserActivity.log_activity(uid, "session_ended", f"Completed session ({duration} minutes)")
        
        return jsonify({
            "success": True,
            "data": {"duration": duration}
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@profile_bp.route("/api/profile/update", methods=["POST"])
@login_required
def update_profile_api():
    """Update user profile via API"""
    uid = session["user_id"]
    
    try:
        # Handle JSON data
        if request.is_json:
            data = request.get_json()
            
            # Update basic profile info
            User.update_profile(
                uid,
                username=data.get("username"),
                profession=data.get("profession"),
                bio=data.get("bio")
            )
            
            # Emit real-time update
            socketio.emit("profile_updated", {
                "user_id": uid,
                "updates": data
            }, room=f"user_{uid}")
            
            return jsonify({"success": True, "message": "Profile updated successfully"})
        
        # Handle form data with files
        else:
            data = request.form
            
            profession = data.get("profession")
            bio = data.get("bio")
            username = data.get("username")
            photo = request.files.get("profile_photo")
            resume = request.files.get("resume")
            
            # Handle photo upload
            photo_name = None
            if photo and photo.filename:
                photo_name = safe_save_file(photo, subfolder=f"user_{uid}")
            
            # Handle resume upload
            resume_name = None
            if resume and resume.filename:
                resume_name = safe_save_file(resume, subfolder=f"user_{uid}")
            
            # Update user profile
            User.update_profile(
                uid,
                username=username,
                profession=profession,
                bio=bio,
                profile_photo=photo_name,
                resume_path=resume_name
            )
            
            # Emit real-time update
            socketio.emit("profile_updated", {
                "user_id": uid,
                "updates": {
                    "username": username,
                    "profession": profession,
                    "bio": bio,
                    "profile_photo": photo_name,
                    "resume_path": resume_name
                }
            }, room=f"user_{uid}")
            
            return jsonify({"success": True, "message": "Profile updated successfully"})
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# =====================================
# WEBSOCKET HANDLERS
# =====================================

@socketio.on("join_profile_room")
def handle_join_profile_room(data):
    """Join user's profile room for real-time updates"""
    if "user_id" in session:
        uid = session["user_id"]
        room = f"user_{uid}"
        join_room(room)
        emit("joined_room", {"room": room, "user_id": uid})

@socketio.on("leave_profile_room")
def handle_leave_profile_room(data):
    """Leave user's profile room"""
    if "user_id" in session:
        uid = session["user_id"]
        room = f"user_{uid}"
        leave_room(room)
        emit("left_room", {"room": room, "user_id": uid})

@socketio.on("update_activity")
def handle_activity_update(data):
    """Handle real-time activity updates"""
    if "user_id" in session:
        uid = session["user_id"]
        
        try:
            # Log the activity
            UserActivity.log_activity(
                uid,
                data.get("type", "general"),
                data.get("description", "Activity update")
            )
            
            # Broadcast to user's room
            emit("activity_logged", {
                "user_id": uid,
                "activity": data,
                "timestamp": datetime.now().isoformat()
            }, room=f"user_{uid}")
            
        except Exception as e:
            emit("error", {"message": str(e)})

@socketio.on("request_stats_update")
def handle_stats_update_request():
    """Handle request for updated statistics"""
    if "user_id" in session:
        uid = session["user_id"]
        
        try:
            stats = UserActivity.get_user_stats(uid)
            today_stats = UserActivity.get_today_stats(uid)
            
            emit("stats_updated", {
                "user_id": uid,
                "stats": stats,
                "today_stats": today_stats,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            emit("error", {"message": str(e)})

# Test profile route removed for production deployment