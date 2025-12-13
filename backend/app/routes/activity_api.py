"""
Real-time Activity API Routes
Handles all real-time activity tracking, progress updates, and statistics
"""
from flask import Blueprint, request, jsonify, session
from ..utils.decorators import login_required
from ..services.realtime_activity_service import RealtimeActivityService
from datetime import datetime
import json

activity_api_bp = Blueprint("activity_api", __name__, url_prefix="/api/activity")

@activity_api_bp.route("/dashboard-stats", methods=["GET"])
@login_required
def get_dashboard_stats():
    """Get comprehensive dashboard statistics"""
    try:
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"error": "User not authenticated"}), 401
        
        # Initialize user stats if not exists
        RealtimeActivityService.initialize_user_stats(user_id)
        
        # Get dashboard stats
        stats = RealtimeActivityService.get_user_dashboard_stats(user_id)
        
        return jsonify({
            "status": "success",
            "data": stats
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@activity_api_bp.route("/live-feed", methods=["GET"])
@login_required
def get_live_activity_feed():
    """Get live activity feed"""
    try:
        user_id = session.get("user_id")
        limit = request.args.get("limit", 20, type=int)
        
        activities = RealtimeActivityService.get_live_activity_feed(user_id, limit)
        
        return jsonify({
            "status": "success",
            "data": activities
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@activity_api_bp.route("/weekly-chart", methods=["GET"])
@login_required
def get_weekly_chart_data():
    """Get weekly progress chart data"""
    try:
        user_id = session.get("user_id")
        
        chart_data = RealtimeActivityService.get_weekly_chart_data(user_id)
        
        return jsonify({
            "status": "success",
            "data": chart_data
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@activity_api_bp.route("/log-activity", methods=["POST"])
@login_required
def log_activity():
    """Log user activity"""
    try:
        user_id = session.get("user_id")
        data = request.get_json()
        
        if not data or "activity_type" not in data:
            return jsonify({"error": "Activity type is required"}), 400
        
        activity_id = RealtimeActivityService.log_activity(
            user_id=user_id,
            activity_type=data["activity_type"],
            module_id=data.get("module_id"),
            description=data.get("description", ""),
            duration_minutes=data.get("duration_minutes", 0),
            metadata=data.get("metadata", {})
        )
        
        return jsonify({
            "status": "success",
            "activity_id": activity_id,
            "message": "Activity logged successfully"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@activity_api_bp.route("/update-module-progress", methods=["POST"])
@login_required
def update_module_progress():
    """Update module progress"""
    try:
        user_id = session.get("user_id")
        data = request.get_json()
        
        if not data or "module_id" not in data:
            return jsonify({"error": "Module ID is required"}), 400
        
        success = RealtimeActivityService.update_module_progress(
            user_id=user_id,
            module_id=data["module_id"],
            progress_data={
                "progress_percentage": data.get("progress_percentage", 0),
                "time_spent_minutes": data.get("time_spent_minutes", 0),
                "quiz_score": data.get("quiz_score", 0)
            }
        )
        
        if success:
            return jsonify({
                "status": "success",
                "message": "Module progress updated successfully"
            })
        else:
            return jsonify({"error": "Failed to update progress"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@activity_api_bp.route("/start-session", methods=["POST"])
@login_required
def start_session():
    """Start a live learning session"""
    try:
        user_id = session.get("user_id")
        data = request.get_json() or {}
        
        session_id = RealtimeActivityService.start_live_session(
            user_id=user_id,
            session_type=data.get("session_type", "study"),
            module_id=data.get("module_id")
        )
        
        return jsonify({
            "status": "success",
            "session_id": session_id,
            "message": "Session started successfully"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@activity_api_bp.route("/end-session", methods=["POST"])
@login_required
def end_session():
    """End a live learning session"""
    try:
        user_id = session.get("user_id")
        data = request.get_json()
        
        if not data or "session_id" not in data:
            return jsonify({"error": "Session ID is required"}), 400
        
        session_summary = RealtimeActivityService.end_live_session(
            session_id=data["session_id"],
            user_id=user_id
        )
        
        return jsonify({
            "status": "success",
            "data": session_summary,
            "message": "Session ended successfully"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@activity_api_bp.route("/quick-stats", methods=["GET"])
@login_required
def get_quick_stats():
    """Get quick stats for real-time updates"""
    try:
        user_id = session.get("user_id")
        
        stats = RealtimeActivityService.get_user_dashboard_stats(user_id)
        
        # Return only essential stats for quick updates
        quick_stats = {
            "total_xp": stats.get("basic_stats", {}).get("total_xp_points", 0),
            "current_streak": stats.get("basic_stats", {}).get("current_streak", 0),
            "today_study_minutes": stats.get("today_stats", {}).get("study_minutes", 0),
            "skill_level": stats.get("basic_stats", {}).get("skill_level", "Beginner"),
            "modules_completed": stats.get("basic_stats", {}).get("modules_completed", 0)
        }
        
        return jsonify({
            "status": "success",
            "data": quick_stats
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@activity_api_bp.route("/skill-progress", methods=["GET"])
@login_required
def get_skill_progress():
    """Get detailed skill development progress"""
    try:
        user_id = session.get("user_id")
        
        stats = RealtimeActivityService.get_user_dashboard_stats(user_id)
        skills = stats.get("skills", [])
        
        # Format skills for frontend
        formatted_skills = []
        for skill in skills:
            skill_data = {
                "category": skill["skill_category"],
                "level": skill["skill_level"],
                "xp_points": skill["xp_points"],
                "progress_percentage": min((skill["xp_points"] % 100), 100),
                "next_level_xp": (skill["skill_level"] * 100) - skill["xp_points"]
            }
            formatted_skills.append(skill_data)
        
        return jsonify({
            "status": "success",
            "data": formatted_skills
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@activity_api_bp.route("/initialize", methods=["POST"])
@login_required
def initialize_user():
    """Initialize real-time tracking for user"""
    try:
        user_id = session.get("user_id")
        
        success = RealtimeActivityService.initialize_user_stats(user_id)
        
        if success:
            return jsonify({
                "status": "success",
                "message": "User tracking initialized successfully"
            })
        else:
            return jsonify({"error": "Failed to initialize tracking"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# WebSocket events for real-time updates (if using SocketIO)
try:
    from ..extensions import socketio
    
    @socketio.on('join_activity_room')
    def on_join_activity_room():
        """Join user's activity room for real-time updates"""
        user_id = session.get("user_id")
        if user_id:
            room = f"user_{user_id}_activity"
            socketio.join_room(room)
            socketio.emit('activity_room_joined', {'room': room})
    
    @socketio.on('request_live_stats')
    def on_request_live_stats():
        """Send live stats to user"""
        user_id = session.get("user_id")
        if user_id:
            try:
                stats = RealtimeActivityService.get_user_dashboard_stats(user_id)
                room = f"user_{user_id}_activity"
                socketio.emit('live_stats_update', stats, room=room)
            except Exception as e:
                socketio.emit('stats_error', {'error': str(e)})
    
    def broadcast_activity_update(user_id: int, activity_data: dict):
        """Broadcast activity update to user's room"""
        room = f"user_{user_id}_activity"
        socketio.emit('activity_update', activity_data, room=room)
    
    def broadcast_progress_update(user_id: int, progress_data: dict):
        """Broadcast progress update to user's room"""
        room = f"user_{user_id}_activity"
        socketio.emit('progress_update', progress_data, room=room)

except ImportError:
    # SocketIO not available
    def broadcast_activity_update(user_id: int, activity_data: dict):
        pass
    
    def broadcast_progress_update(user_id: int, progress_data: dict):
        pass