"""
Page routes: /dashboard, /learn, /about-us, /resources, /stt-tts, /isl-recognition
"""
from flask import Blueprint, render_template, session
from ..utils.decorators import login_required

pages_bp = Blueprint("pages", __name__)

@pages_bp.route("/dashboard")
@login_required
def dashboard():
    """Main user dashboard with personalized data"""
    from ..models.stats import UserStats, UserActivity
    from ..models.courses import Course, UserProgress
    from ..models.achievements import Achievement
    from ..models.user import User
    
    user_id = session.get("user_id")
    username = session.get("username")
    
    # Get user data
    user = User.get_by_id(user_id) if user_id else {}
    
    # Get user stats
    stats = UserStats.get_by_user_id(user_id) or {
        'courses': 0, 'progress': 0, 'achievements': 0, 
        'points': 0, 'modules_completed': 0
    }
    
    # Get user courses with progress
    courses = Course.get_all_courses()[:3]  # Get top 3 courses
    for course in courses:
        progress = UserProgress.get_user_course_progress(user_id, course['id'])
        course['user_progress'] = progress
    
    # Get achievements
    achievements = Achievement.get_user_achievements(user_id) or []
    
    # Get weekly activity
    weekly_activity = UserActivity.get_weekly_activity(user_id) or []
    
    return render_template("dashboard.html", 
                         username=username,
                         user=user,
                         session=session,
                         stats=stats,
                         courses=courses,
                         achievements=achievements,
                         weekly_activity=weekly_activity,
                         active_page="dashboard")


@pages_bp.route("/about")
def about():
    """Redirect to main about page for compatibility"""
    from flask import redirect, url_for
    return redirect(url_for('pages.about_us'))

@pages_bp.route("/learn")
@login_required
def learn():
    """Learning hub with real-time course progress"""
    from ..models.courses import Course, UserProgress
    from ..models.user import User
    
    user_id = session.get("user_id")
    username = session.get("username")
    
    # Get user data
    user = User.get_by_id(user_id) if user_id else {}
    
    # Get learning statistics
    learning_stats = UserProgress.get_user_overall_stats(user_id)
    
    # Get courses with progress
    courses = Course.get_all_courses()
    for course in courses:
        progress = UserProgress.get_user_course_progress(user_id, course['id'])
        course['user_progress'] = progress
    
    # Format stats for template
    stats = {
        'completed_modules': learning_stats['total_modules_completed'],
        'total_hours': round(learning_stats['total_time_minutes'] / 60, 1),
        'streak_days': learning_stats['streak_days'],
        'today_minutes': 0,  # Calculate today's minutes from recent activity
        'overall_progress': learning_stats['avg_progress']
    }
    
    # Calculate today's activity
    from datetime import datetime
    today = datetime.now().date()
    for activity in learning_stats['recent_activity']:
        if activity['date'] == str(today):
            stats['today_minutes'] = activity.get('modules', 0) * 15  # Estimate 15 min per module
            break
    
    return render_template("learn.html", 
                         username=username,
                         user=user,
                         session=session,
                         stats=stats,
                         courses=courses,
                         learning_stats=learning_stats,
                         active_page="learn")

@pages_bp.route("/learn/course/<int:course_id>")
@login_required
def learn_course(course_id):
    """Course overview page with modules"""
    from ..models.courses import Course, Module, UserProgress
    from ..models.user import User
    
    user_id = session.get("user_id")
    username = session.get("username")
    
    # Get course details
    course = Course.get_course_by_id(course_id)
    if not course:
        return render_template("error.html", 
                             error="Course not found", 
                             username=username), 404
    
    # Get course modules
    modules = Module.get_course_modules(course_id)
    
    # Add user progress to each module
    for module in modules:
        progress = UserProgress.get_user_module_progress(user_id, module['id'])
        module['user_progress'] = progress
    
    # Get course progress
    course_progress = UserProgress.get_user_course_progress(user_id, course_id)
    
    # Get user data
    user = User.get_by_id(user_id) if user_id else {}
    
    # Use a simple course overview template for all courses
    template = "courses/course_overview.html"
    
    return render_template(template,
                         username=username,
                         user=user,
                         session=session,
                         course=course,
                         modules=modules,
                         course_progress=course_progress,
                         active_page="learn")

@pages_bp.route("/learn/module/<int:module_id>")
@login_required
def learn_module(module_id):
    """Individual module learning page with upcoming module notifications"""
    from ..models.courses import Module, Course, UserProgress, Quiz
    from ..models.user import User
    
    user_id = session.get("user_id")
    username = session.get("username")
    
    # Get module details
    module = Module.get_module_by_id(module_id)
    if not module:
        return render_template("error.html", 
                             error="Module not found", 
                             username=username), 404
    
    # Get course details
    course = Course.get_course_by_id(module['course_id'])
    
    # Get user progress
    progress = UserProgress.get_user_module_progress(user_id, module_id)
    
    # Get quiz if exists
    quiz = Quiz.get_module_quiz(module_id)
    
    # Get user data
    user = User.get_by_id(user_id) if user_id else {}
    
    # Get course progress for context
    course_progress = UserProgress.get_user_course_progress(user_id, course['id'])
    
    # Define all available modules with their details
    all_modules = {
        1: {
            "title": "ISL Alphabet & Fingerspelling",
            "title_hindi": "भारतीय सांकेतिक वर्णमाला",
            "description": "Master the 26 letters of ISL alphabet with proper hand shapes and movements.",
            "template": "courses/module1.html",
            "available": True
        },
        2: {
            "title": "Numbers & Mathematical Concepts", 
            "title_hindi": "संख्या और गणित",
            "description": "Learn cardinal numbers, ordinal numbers, and basic arithmetic operations in ISL.",
            "template": "courses/module2.html",
            "available": True
        },
        3: {
            "title": "Family & Relationships",
            "title_hindi": "परिवार और रिश्ते", 
            "description": "Essential vocabulary for family members, relationships, and social connections.",
            "template": "courses/module3.html",
            "available": True
        },
        4: {
            "title": "Colors, Shapes & Objects",
            "title_hindi": "रंग, आकार और वस्तुएं",
            "description": "Learn to describe the visual world - colors, geometric shapes, and common objects.",
            "template": "courses/module4.html",
            "available": True
        },
        5: {
            "title": "Time & Calendar Concepts",
            "title_hindi": "समय और कैलेंडर",
            "description": "Master time expressions, days, months, seasons, and temporal concepts.",
            "template": "courses/module5.html",
            "available": True
        },
        6: {
            "title": "Basic Grammar & Sentence Structure",
            "title_hindi": "व्याकरण और वाक्य संरचना", 
            "description": "Understand ISL grammar rules, word order, and sentence formation.",
            "template": "courses/module6.html",
            "available": True
        },
        7: {
            "title": "Daily Activities & Routines",
            "title_hindi": "दैनिक गतिविधियां",
            "description": "Learn signs for everyday activities, routines, and common actions.",
            "template": "courses/module_learning.html",
            "available": False,
            "coming_soon": True
        },
        8: {
            "title": "Emotions & Feelings",
            "title_hindi": "भावनाएं और अनुभूतियां",
            "description": "Express emotions, feelings, and psychological states through ISL.",
            "template": "courses/module_learning.html", 
            "available": False,
            "coming_soon": True
        },
        9: {
            "title": "Places & Directions",
            "title_hindi": "स्थान और दिशाएं",
            "description": "Navigate and describe locations, directions, and geographical concepts.",
            "template": "courses/module_learning.html",
            "available": False,
            "coming_soon": True
        },
        10: {
            "title": "Food & Health",
            "title_hindi": "भोजन और स्वास्थ्य", 
            "description": "Learn vocabulary related to food, nutrition, health, and medical terms.",
            "template": "courses/module_learning.html",
            "available": False,
            "coming_soon": True
        },
        11: {
            "title": "Education & Work",
            "title_hindi": "शिक्षा और कार्य",
            "description": "Professional and educational vocabulary for academic and workplace settings.",
            "template": "courses/module_learning.html",
            "available": False,
            "coming_soon": True
        },
        12: {
            "title": "Advanced Grammar & Discourse",
            "title_hindi": "उन्नत व्याकरण",
            "description": "Advanced linguistic structures, discourse markers, and complex communication.",
            "template": "courses/module_learning.html",
            "available": False,
            "coming_soon": True
        }
    }
    
    # Get current module info
    current_module_info = all_modules.get(module_id, {})
    
    # Check if module is available
    if not current_module_info.get("available", False):
        # Show coming soon notification
        upcoming_modules = [mod for mod_id, mod in all_modules.items() 
                          if mod_id > 6 and mod.get("coming_soon", False)]
        
        return render_template("courses/coming_soon.html",
                             username=username,
                             user=user,
                             session=session,
                             requested_module=current_module_info,
                             module_id=module_id,
                             upcoming_modules=upcoming_modules,
                             active_page="learn")
    
    # Get template for available modules
    template = current_module_info.get("template", "courses/module_learning.html")
    
    # Get next available modules for notifications
    next_modules = []
    for next_id in range(module_id + 1, min(module_id + 4, 13)):  # Show next 3 modules
        if next_id in all_modules:
            next_module = all_modules[next_id].copy()
            next_module['id'] = next_id
            next_modules.append(next_module)
    
    # Merge module data with database info if available
    if module:
        current_module_info.update(module)
    else:
        # Use predefined module info if not in database
        module = current_module_info
        module['id'] = module_id
    
    return render_template(template,
                         username=username,
                         user=user,
                         session=session,
                         module=module,
                         course=course,
                         progress=progress,
                         course_progress=course_progress,
                         quiz=quiz,
                         module_number=module_id,
                         next_modules=next_modules,
                         all_modules=all_modules,
                         active_page="learn")

@pages_bp.route("/about-us")
def about_us():
    """About us page - Professional ISL Recognition System overview"""
    from ..models.user import User
    
    user_id = session.get("user_id")
    user = User.get_by_id(user_id) if user_id else {}
    
    return render_template("about.html", 
                         username=session.get("username"),
                         user=user,
                         session=session,
                         active_page="about_us",
                         show_sidebar=False)

@pages_bp.route("/resources")
@login_required
def resources():
    """Resources page"""
    from ..models.user import User
    
    user_id = session.get("user_id")
    user = User.get_by_id(user_id) if user_id else {}
    
    return render_template("resources.html", 
                         username=session.get("username"),
                         user=user,
                         session=session,
                         active_page="resources")

@pages_bp.route("/stt-tts")
@login_required
def stt_tts():
    """Speech-to-text and text-to-speech tools page"""
    from ..models.user import User
    
    user_id = session.get("user_id")
    user = User.get_by_id(user_id) if user_id else {}
    
    return render_template("tools.html", 
                         username=session.get("username"),
                         user=user,
                         session=session,
                         active_page="stt-tts",
                         show_sidebar=True)

@pages_bp.route("/isl-recognition")
@login_required
def isl_recognition():
    """ISL recognition page with live ML model"""
    from ..models.user import User
    
    user_id = session.get("user_id")
    user = User.get_by_id(user_id) if user_id else {}
    
    return render_template(
        "isl_recognition.html",
        username=session.get("username"),
        user=user,
        session=session,
        active_page="isl-recognition",
        show_sidebar=True
    )

# Camera test routes removed for production deployment

@pages_bp.route("/tts-tool")
@login_required
def tts_tool():
    """Text-to-Speech tool page"""
    from ..models.user import User
    
    user_id = session.get("user_id")
    user = User.get_by_id(user_id) if user_id else {}
    
    return render_template("tts_tool.html",
                         username=session.get("username"),
                         user=user,
                         session=session,
                         active_page="tts-tool")

@pages_bp.route("/stt-tool")
@login_required
def stt_tool():
    """Speech-to-Text tool page"""
    from ..models.user import User
    
    user_id = session.get("user_id")
    user = User.get_by_id(user_id) if user_id else {}
    
    return render_template("stt_tool.html",
                         username=session.get("username"),
                         user=user,
                         session=session,
                         active_page="stt-tool")

@pages_bp.route("/ml-diagnostics")
@login_required
def ml_diagnostics():
    """ML system diagnostics page"""
    from ..models.user import User
    
    user_id = session.get("user_id")
    user = User.get_by_id(user_id) if user_id else {}
    
    return render_template("ml_diagnostics.html",
                         username=session.get("username"),
                         user=user,
                         session=session,
                         active_page="ml-diagnostics")

# Static file serving for uploads
from flask import send_from_directory
import os

@pages_bp.route("/storage/uploads/<path:filename>")
def uploaded_file(filename):
    """Serve uploaded files"""
    upload_folder = os.path.join(os.getcwd(), "storage", "uploads")
    return send_from_directory(upload_folder, filename)