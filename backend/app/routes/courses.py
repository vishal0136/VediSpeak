"""
Course routes for Learning Management System
- Course and module management
- Progress tracking and statistics
- Real-time updates via WebSocket
"""
from flask import Blueprint, request, jsonify, session, render_template
from flask_socketio import emit, join_room, leave_room
from ..utils.decorators import login_required
from ..extensions import socketio
from ..models.courses import Course, Module, UserProgress, Quiz
from ..models.stats import UserActivity
import logging
from datetime import datetime

courses_bp = Blueprint("courses", __name__)
logger = logging.getLogger(__name__)


# =====================================
# COURSE MANAGEMENT ROUTES
# =====================================

@courses_bp.route("/api/courses")
@login_required
def get_courses():
    """Get all available courses with user progress"""
    try:
        user_id = session.get("user_id")
        courses = Course.get_all_courses()
        
        # Add user progress to each course
        for course in courses:
            progress = UserProgress.get_user_course_progress(user_id, course['id'])
            course['user_progress'] = progress
        
        return jsonify({
            "status": "success",
            "courses": courses
        })
    except Exception as e:
        logger.error(f"Error getting courses: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@courses_bp.route("/api/courses/<int:course_id>")
@login_required
def get_course_details(course_id):
    """Get detailed course information with modules"""
    try:
        user_id = session.get("user_id")
        
        # Get course details
        course = Course.get_course_by_id(course_id)
        if not course:
            return jsonify({"status": "error", "message": "Course not found"}), 404
        
        # Get course modules
        modules = Module.get_course_modules(course_id)
        
        # Add user progress to each module
        for module in modules:
            progress = UserProgress.get_user_module_progress(user_id, module['id'])
            module['user_progress'] = progress
        
        # Get course progress
        course_progress = UserProgress.get_user_course_progress(user_id, course_id)
        
        return jsonify({
            "status": "success",
            "course": course,
            "modules": modules,
            "progress": course_progress
        })
    except Exception as e:
        logger.error(f"Error getting course details: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@courses_bp.route("/api/modules/<int:module_id>")
@login_required
def get_module_details(module_id):
    """Get detailed module information"""
    try:
        user_id = session.get("user_id")
        
        # Get module details
        module = Module.get_module_by_id(module_id)
        if not module:
            return jsonify({"status": "error", "message": "Module not found"}), 404
        
        # Get user progress
        progress = UserProgress.get_user_module_progress(user_id, module_id)
        
        # Get quiz if exists
        quiz = Quiz.get_module_quiz(module_id)
        
        return jsonify({
            "status": "success",
            "module": module,
            "progress": progress,
            "quiz": quiz
        })
    except Exception as e:
        logger.error(f"Error getting module details: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


# =====================================
# PROGRESS TRACKING ROUTES
# =====================================

@courses_bp.route("/api/progress/module/<int:module_id>", methods=["POST"])
@login_required
def update_module_progress(module_id):
    """Update user's progress for a module"""
    try:
        user_id = session.get("user_id")
        data = request.get_json()
        
        progress_percentage = data.get('progress_percentage', 0)
        time_spent = data.get('time_spent_minutes', 0)
        quiz_score = data.get('quiz_score')
        
        # Validate input
        if not (0 <= progress_percentage <= 100):
            return jsonify({"status": "error", "message": "Invalid progress percentage"}), 400
        
        # Update progress
        success = UserProgress.update_module_progress(
            user_id, module_id, progress_percentage, time_spent, quiz_score
        )
        
        if success:
            # Log activity
            UserActivity.log_activity(
                user_id, "module_progress", 
                f"Updated module progress to {progress_percentage}%", 
                int(progress_percentage / 10)  # Points based on progress
            )
            
            # Get updated progress
            updated_progress = UserProgress.get_user_module_progress(user_id, module_id)
            
            # Emit real-time update
            socketio.emit('progress_updated', {
                'module_id': module_id,
                'progress': updated_progress
            }, room=f'user_{user_id}')
            
            return jsonify({
                "status": "success",
                "progress": updated_progress
            })
        else:
            return jsonify({"status": "error", "message": "Failed to update progress"}), 500
            
    except Exception as e:
        logger.error(f"Error updating module progress: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@courses_bp.route("/api/progress/user")
@login_required
def get_user_progress():
    """Get user's overall learning statistics"""
    try:
        user_id = session.get("user_id")
        stats = UserProgress.get_user_overall_stats(user_id)
        
        return jsonify({
            "status": "success",
            "stats": stats
        })
    except Exception as e:
        logger.error(f"Error getting user progress: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


# =====================================
# QUIZ ROUTES
# =====================================

@courses_bp.route("/api/quiz/<int:quiz_id>")
@login_required
def get_quiz(quiz_id):
    """Get quiz questions"""
    try:
        # Note: In a real implementation, you'd get quiz by ID
        # For now, we'll get by module_id since that's what we have
        module_id = request.args.get('module_id')
        if not module_id:
            return jsonify({"status": "error", "message": "Module ID required"}), 400
        
        quiz = Quiz.get_module_quiz(int(module_id))
        if not quiz:
            return jsonify({"status": "error", "message": "Quiz not found"}), 404
        
        return jsonify({
            "status": "success",
            "quiz": quiz
        })
    except Exception as e:
        logger.error(f"Error getting quiz: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@courses_bp.route("/api/quiz/<int:quiz_id>/submit", methods=["POST"])
@login_required
def submit_quiz(quiz_id):
    """Submit quiz answers and get score"""
    try:
        user_id = session.get("user_id")
        data = request.get_json()
        
        answers = data.get('answers', [])
        
        # Get quiz details
        module_id = request.args.get('module_id')
        if not module_id:
            return jsonify({"status": "error", "message": "Module ID required"}), 400
        
        quiz = Quiz.get_module_quiz(int(module_id))
        if not quiz:
            return jsonify({"status": "error", "message": "Quiz not found"}), 404
        
        # Calculate score
        questions = quiz['questions']
        correct_answers = 0
        total_questions = len(questions)
        
        for i, answer in enumerate(answers):
            if i < len(questions) and questions[i].get('correct') == answer:
                correct_answers += 1
        
        score = (correct_answers / total_questions * 100) if total_questions > 0 else 0
        
        # Submit attempt
        attempt_id = Quiz.submit_quiz_attempt(user_id, quiz['id'], answers, score)
        
        # Update module progress with quiz score
        UserProgress.update_module_progress(user_id, int(module_id), 100, 0, score)
        
        # Log activity
        UserActivity.log_activity(
            user_id, "quiz_completed", 
            f"Completed quiz with score {score:.1f}%", 
            int(score / 10)
        )
        
        return jsonify({
            "status": "success",
            "score": score,
            "correct_answers": correct_answers,
            "total_questions": total_questions,
            "passed": score >= quiz['passing_score'],
            "attempt_id": attempt_id
        })
        
    except Exception as e:
        logger.error(f"Error submitting quiz: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


# =====================================
# LEARNING ANALYTICS ROUTES
# =====================================

@courses_bp.route("/api/analytics/dashboard")
@login_required
def get_learning_analytics():
    """Get comprehensive learning analytics for dashboard"""
    try:
        user_id = session.get("user_id")
        
        # Get overall stats
        stats = UserProgress.get_user_overall_stats(user_id)
        
        # Get recent courses
        courses = Course.get_all_courses()
        recent_courses = []
        
        for course in courses[:3]:  # Get top 3 courses
            progress = UserProgress.get_user_course_progress(user_id, course['id'])
            if progress:
                course['progress'] = progress
                recent_courses.append(course)
        
        return jsonify({
            "status": "success",
            "analytics": {
                "overall_stats": stats,
                "recent_courses": recent_courses,
                "learning_streak": stats['streak_days'],
                "total_time_hours": round(stats['total_time_minutes'] / 60, 1),
                "completion_rate": round(
                    (stats['completed_courses'] / max(stats['total_courses'], 1)) * 100, 1
                )
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting learning analytics: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


# =====================================
# WEBSOCKET HANDLERS
# =====================================

@socketio.on('join_learning_room')
def handle_join_learning():
    """Join learning room for real-time updates"""
    user_id = session.get("user_id")
    if user_id:
        room = f'user_{user_id}'
        join_room(room)
        emit('learning_joined', {'message': 'Connected to learning updates'})


@socketio.on('leave_learning_room')
def handle_leave_learning():
    """Leave learning room"""
    user_id = session.get("user_id")
    if user_id:
        room = f'user_{user_id}'
        leave_room(room)
        emit('learning_left', {'message': 'Disconnected from learning updates'})


@socketio.on('start_module_session')
def handle_start_module_session(data):
    """Start a learning session for a module"""
    try:
        user_id = session.get("user_id")
        module_id = data.get('module_id')
        
        if not user_id or not module_id:
            emit('session_error', {'error': 'Invalid session data'})
            return
        
        # Log session start
        UserActivity.log_activity(
            user_id, "session_started", 
            f"Started learning session for module {module_id}", 
            1
        )
        
        emit('session_started', {
            'module_id': module_id,
            'start_time': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error starting module session: {e}")
        emit('session_error', {'error': str(e)})


@socketio.on('update_session_progress')
def handle_session_progress(data):
    """Update progress during a learning session"""
    try:
        user_id = session.get("user_id")
        module_id = data.get('module_id')
        progress = data.get('progress', 0)
        time_spent = data.get('time_spent', 0)
        
        if not user_id or not module_id:
            emit('progress_error', {'error': 'Invalid progress data'})
            return
        
        # Update progress
        success = UserProgress.update_module_progress(
            user_id, module_id, progress, time_spent
        )
        
        if success:
            # Get updated stats
            stats = UserProgress.get_user_overall_stats(user_id)
            
            # Get module details for context
            module = Module.get_module_by_id(module_id)
            course = Course.get_course_by_id(module['course_id']) if module else None
            
            # Emit to user's room for real-time updates across all tabs
            room = f'user_{user_id}'
            socketio.emit('progress_updated', {
                'module_id': module_id,
                'progress': progress,
                'overall_stats': stats,
                'module': module,
                'course': course
            }, room=room)
            
            # Also emit to learning room
            socketio.emit('learning_progress_updated', {
                'user_id': user_id,
                'module_id': module_id,
                'progress': progress,
                'stats': stats
            }, room='learning_room')
            
        else:
            emit('progress_error', {'error': 'Failed to update progress'})
        
    except Exception as e:
        logger.error(f"Error updating session progress: {e}")
        emit('progress_error', {'error': str(e)})


@socketio.on('join_user_room')
def handle_join_user_room():
    """Join user-specific room for real-time updates"""
    user_id = session.get("user_id")
    if user_id:
        room = f'user_{user_id}'
        join_room(room)
        emit('user_room_joined', {'message': 'Connected to personal updates'})


@socketio.on('request_stats_update')
def handle_stats_request():
    """Request updated learning statistics"""
    try:
        user_id = session.get("user_id")
        if not user_id:
            emit('stats_error', {'error': 'User not authenticated'})
            return
        
        # Get fresh stats
        stats = UserProgress.get_user_overall_stats(user_id)
        
        emit('stats_updated', {
            'user_id': user_id,
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"Error getting stats update: {e}")
        emit('stats_error', {'error': str(e)})


# =====================================
# PAGE ROUTES
# =====================================

# Module page route moved to pages.py to avoid conflicts