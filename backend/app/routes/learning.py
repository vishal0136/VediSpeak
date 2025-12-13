"""
Learning Management System routes with real-time progress tracking
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_socketio import emit, join_room, leave_room
from datetime import datetime, timedelta
import json
from ..extensions import mysql, socketio
from ..utils.decorators import login_required
from ..utils.db_helpers import db_cursor

learning_bp = Blueprint("learning", __name__)

@learning_bp.route("/learning-hub")
@login_required
def learn_hub():
    """Enhanced learning hub with real-time stats"""
    uid = session["user_id"]
    
    # Get learning statistics
    stats = get_learning_stats(uid)
    
    return render_template(
        "learn.html",
        username=session.get("username"),
        stats=stats,
        active_page="learn"
    )

@learning_bp.route("/learning/module/<int:module_id>")
@login_required
def module_page(module_id):
    """Individual module page"""
    uid = session["user_id"]
    
    # Get module progress
    progress = get_module_progress(uid, module_id)
    
    # Module templates mapping
    module_templates = {
        1: "courses/module1.html",
        2: "courses/module2.html", 
        3: "courses/module3.html",
        4: "courses/module4.html",
        5: "courses/module5.html",
        6: "courses/module6.html"
    }
    
    template = module_templates.get(module_id, "courses/module1.html")
    
    return render_template(
        template,
        username=session.get("username"),
        module_id=module_id,
        progress=progress,
        active_page="learn"
    )

@learning_bp.route("/api/learning/stats")
@login_required
def get_learning_stats_api():
    """Get real-time learning statistics"""
    uid = session["user_id"]
    
    try:
        stats = get_learning_stats(uid)
        return jsonify({
            "success": True,
            "data": stats
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@learning_bp.route("/api/learning/progress", methods=["POST"])
@login_required
def update_progress():
    """Update learning progress"""
    uid = session["user_id"]
    data = request.get_json()
    
    try:
        module_id = data.get("module_id")
        lesson_id = data.get("lesson_id")
        progress = data.get("progress", 0)
        completed = data.get("completed", False)
        
        # Update progress in database
        update_lesson_progress(uid, module_id, lesson_id, progress, completed)
        
        # Emit real-time update
        socketio.emit("progress_updated", {
            "user_id": uid,
            "module_id": module_id,
            "lesson_id": lesson_id,
            "progress": progress,
            "completed": completed
        }, room=f"learning_{uid}")
        
        # Log learning activity
        log_learning_activity(uid, "lesson_progress", f"Module {module_id}, Lesson {lesson_id}: {progress}%")
        
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@learning_bp.route("/api/learning/session/start", methods=["POST"])
@login_required
def start_learning_session():
    """Start a learning session"""
    uid = session["user_id"]
    data = request.get_json()
    
    try:
        module_id = data.get("module_id")
        lesson_id = data.get("lesson_id")
        
        session_id = create_learning_session(uid, module_id, lesson_id)
        
        # Emit real-time update
        socketio.emit("session_started", {
            "user_id": uid,
            "session_id": session_id,
            "module_id": module_id,
            "lesson_id": lesson_id,
            "start_time": datetime.now().isoformat()
        }, room=f"learning_{uid}")
        
        return jsonify({
            "success": True,
            "data": {"session_id": session_id}
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@learning_bp.route("/api/learning/session/<int:session_id>/end", methods=["POST"])
@login_required
def end_learning_session(session_id):
    """End a learning session"""
    uid = session["user_id"]
    
    try:
        duration = end_session(session_id, uid)
        
        # Emit real-time update
        socketio.emit("session_ended", {
            "user_id": uid,
            "session_id": session_id,
            "duration": duration,
            "end_time": datetime.now().isoformat()
        }, room=f"learning_{uid}")
        
        # Log activity
        log_learning_activity(uid, "session_completed", f"Studied for {duration} minutes")
        
        return jsonify({
            "success": True,
            "data": {"duration": duration}
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Helper functions
def get_learning_stats(user_id):
    """Get comprehensive learning statistics"""
    cur = None
    try:
        cur = db_cursor()
        
        # Get total study hours
        cur.execute("""
            SELECT COALESCE(SUM(duration_minutes), 0) as total_minutes
            FROM learning_sessions WHERE user_id = %s AND end_time IS NOT NULL
        """, [user_id])
        total_minutes = cur.fetchone()[0]
        
        # Get completed modules
        cur.execute("""
            SELECT COUNT(DISTINCT module_id) as completed_modules
            FROM learning_progress WHERE user_id = %s AND completed = 1
        """, [user_id])
        completed_modules = cur.fetchone()[0]
        
        # Get current streak
        streak_days = calculate_learning_streak(user_id)
        
        # Get today's study time
        cur.execute("""
            SELECT COALESCE(SUM(duration_minutes), 0) as today_minutes
            FROM learning_sessions 
            WHERE user_id = %s AND DATE(start_time) = CURDATE() AND end_time IS NOT NULL
        """, [user_id])
        today_minutes = cur.fetchone()[0]
        
        # Calculate overall progress
        cur.execute("""
            SELECT AVG(progress) as avg_progress
            FROM learning_progress WHERE user_id = %s
        """, [user_id])
        avg_progress = cur.fetchone()[0] or 0
        
        return {
            'total_hours': round(total_minutes / 60, 1),
            'completed_modules': completed_modules,
            'streak_days': streak_days,
            'today_minutes': today_minutes,
            'overall_progress': round(avg_progress, 1)
        }
    finally:
        if cur:
            cur.close()

def get_module_progress(user_id, module_id):
    """Get progress for a specific module"""
    cur = None
    try:
        cur = db_cursor()
        
        cur.execute("""
            SELECT lesson_id, progress, completed, last_accessed
            FROM learning_progress 
            WHERE user_id = %s AND module_id = %s
            ORDER BY lesson_id
        """, (user_id, module_id))
        
        lessons = cur.fetchall()
        return lessons or []
    finally:
        if cur:
            cur.close()

def update_lesson_progress(user_id, module_id, lesson_id, progress, completed):
    """Update progress for a specific lesson"""
    cur = None
    try:
        cur = db_cursor()
        
        # Insert or update progress
        cur.execute("""
            INSERT INTO learning_progress (user_id, module_id, lesson_id, progress, completed, last_accessed)
            VALUES (%s, %s, %s, %s, %s, NOW())
            ON DUPLICATE KEY UPDATE
            progress = %s, completed = %s, last_accessed = NOW()
        """, (user_id, module_id, lesson_id, progress, completed, progress, completed))
        
        mysql.connection.commit()
    finally:
        if cur:
            cur.close()

def create_learning_session(user_id, module_id, lesson_id):
    """Create a new learning session"""
    cur = None
    try:
        cur = db_cursor()
        
        cur.execute("""
            INSERT INTO learning_sessions (user_id, module_id, lesson_id, start_time)
            VALUES (%s, %s, %s, NOW())
        """, (user_id, module_id, lesson_id))
        
        mysql.connection.commit()
        return cur.lastrowid
    finally:
        if cur:
            cur.close()

def end_session(session_id, user_id):
    """End a learning session and return duration"""
    cur = None
    try:
        cur = db_cursor()
        
        # Update session end time
        cur.execute("""
            UPDATE learning_sessions 
            SET end_time = NOW(), duration_minutes = TIMESTAMPDIFF(MINUTE, start_time, NOW())
            WHERE id = %s AND user_id = %s
        """, (session_id, user_id))
        
        # Get duration
        cur.execute("""
            SELECT duration_minutes FROM learning_sessions WHERE id = %s
        """, [session_id])
        
        duration = cur.fetchone()[0] or 0
        mysql.connection.commit()
        return duration
    finally:
        if cur:
            cur.close()

def calculate_learning_streak(user_id):
    """Calculate consecutive days of learning activity"""
    cur = None
    try:
        cur = db_cursor()
        
        cur.execute("""
            SELECT DISTINCT DATE(start_time) as study_date
            FROM learning_sessions 
            WHERE user_id = %s AND end_time IS NOT NULL
            ORDER BY study_date DESC
            LIMIT 30
        """, [user_id])
        
        dates = [row[0] for row in cur.fetchall()]
        if not dates:
            return 0
        
        streak = 0
        current_date = datetime.now().date()
        
        for date in dates:
            if date == current_date or date == current_date - timedelta(days=streak):
                streak += 1
                current_date = date
            else:
                break
        
        return streak
    finally:
        if cur:
            cur.close()

def log_learning_activity(user_id, activity_type, description):
    """Log learning activity"""
    cur = None
    try:
        cur = db_cursor()
        
        cur.execute("""
            INSERT INTO learning_activity_log (user_id, activity_type, description, created_at)
            VALUES (%s, %s, %s, NOW())
        """, (user_id, activity_type, description))
        
        mysql.connection.commit()
    finally:
        if cur:
            cur.close()

# WebSocket handlers
@socketio.on("join_learning_room")
def handle_join_learning_room(data):
    """Join user's learning room for real-time updates"""
    if "user_id" in session:
        uid = session["user_id"]
        room = f"learning_{uid}"
        join_room(room)
        emit("joined_learning_room", {"room": room, "user_id": uid})

@socketio.on("leave_learning_room")
def handle_leave_learning_room(data):
    """Leave user's learning room"""
    if "user_id" in session:
        uid = session["user_id"]
        room = f"learning_{uid}"
        leave_room(room)
        emit("left_learning_room", {"room": room, "user_id": uid})