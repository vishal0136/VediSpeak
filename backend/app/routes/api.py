"""
API routes: /api/hours_spent, /api/performance_grade
"""
from datetime import date, timedelta
from flask import Blueprint, jsonify, session
from ..utils.decorators import login_required
from ..utils.db_helpers import db_cursor

api_bp = Blueprint("api", __name__)

@api_bp.route("/hours_spent")
@login_required
def hours_spent():
    """Get user's study hours for the last 6 months"""
    user_id = session["user_id"]
    cur = None
    try:
        cur = db_cursor()
        
        # Aggregate last 6 months of activity
        cur.execute("""
            SELECT 
                DATE_FORMAT(activity_date, '%%b %%Y') AS month,
                SUM(CASE WHEN activity_type='study' THEN duration_minutes ELSE 0 END) AS study,
                SUM(CASE WHEN activity_type='online_test' THEN duration_minutes ELSE 0 END) AS online_test
            FROM user_activity
            WHERE user_id=%s AND activity_date >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
            GROUP BY month
            ORDER BY MIN(activity_date) ASC
        """, [user_id])
        
        rows = cur.fetchall()
        labels = []
        study = []
        online_test = []
        
        # Fill last 6 months with zeros if no activity
        today = date.today()
        for i in reversed(range(6)):
            month_date = (today.replace(day=1) - timedelta(days=i*30))
            month_name = month_date.strftime("%b %Y")
            
            # Check if row exists for this month
            found = next((r for r in rows if r[0] == month_name), None)
            labels.append(month_name)
            study.append(found[1] if found else 0)
            online_test.append(found[2] if found else 0)
        
        return jsonify({
            "labels": labels,
            "study": study,
            "online_test": online_test
        })
    
    except Exception as e:
        return jsonify({"labels": [], "study": [], "online_test": []}), 500
    finally:
        if cur:
            cur.close()

@api_bp.route("/performance_grade")
@login_required
def performance_grade():
    """Get user's performance grade based on activity and completion"""
    user_id = session["user_id"]
    cur = None
    try:
        cur = db_cursor()
        
        # Calculate performance based on multiple factors
        performance_score = 0
        
        # Factor 1: Study activity (40% weight)
        cur.execute("""
            SELECT COALESCE(SUM(duration_minutes), 0) as total_study_minutes
            FROM user_activity
            WHERE user_id=%s AND activity_type='study'
        """, [user_id])
        
        study_minutes = cur.fetchone()[0] or 0
        study_score = min(study_minutes / 60 / 10, 4.0)  # Max 4 points for 10+ hours
        
        # Factor 2: Task completion rate (30% weight)
        cur.execute("""
            SELECT 
                COUNT(*) as total_tasks,
                SUM(CASE WHEN completed = 1 THEN 1 ELSE 0 END) as completed_tasks
            FROM user_tasks
            WHERE user_id=%s
        """, [user_id])
        
        task_data = cur.fetchone()
        total_tasks = task_data[0] or 0
        completed_tasks = task_data[1] or 0
        
        completion_rate = (completed_tasks / max(total_tasks, 1)) if total_tasks > 0 else 0
        completion_score = completion_rate * 3.0  # Max 3 points for 100% completion
        
        # Factor 3: Consistency/streak (30% weight)
        cur.execute("""
            SELECT COUNT(DISTINCT activity_date) as active_days
            FROM user_activity
            WHERE user_id=%s AND activity_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
        """, [user_id])
        
        active_days = cur.fetchone()[0] or 0
        consistency_score = min(active_days / 15, 3.0)  # Max 3 points for 15+ active days
        
        # Calculate final grade (out of 10)
        performance_score = study_score + completion_score + consistency_score
        final_grade = min(performance_score, 10.0)
        
        return jsonify({"grade": round(final_grade, 2)})
    
    except Exception as e:
        return jsonify({"grade": 0}), 500
    finally:
        if cur:
            cur.close()
