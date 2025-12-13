"""
Enhanced User statistics and activity models with real-time features
"""
from ..extensions import mysql
from ..utils.db_helpers import db_cursor
from datetime import datetime, timedelta
import json

class UserStats:
    @staticmethod
    def create_or_get(user_id):
        """Create user stats if not exists, return existing stats"""
        cur = None
        try:
            cur = db_cursor()
            cur.execute("SELECT * FROM user_stats WHERE user_id = %s", [user_id])
            row = cur.fetchone()
            
            if not row:
                cur.execute("INSERT INTO user_stats (user_id) VALUES (%s)", [user_id])
                mysql.connection.commit()
                cur.execute("SELECT * FROM user_stats WHERE user_id = %s", [user_id])
                row = cur.fetchone()
            
            if row:
                cols = [desc[0] for desc in cur.description]
                return dict(zip(cols, row))
            return None
        finally:
            if cur:
                cur.close()
    
    @staticmethod
    def update_login(user_id):
        """Update last login timestamp"""
        cur = None
        try:
            cur = db_cursor()
            cur.execute("""
                UPDATE user_stats SET last_login = NOW() WHERE user_id = %s
            """, [user_id])
            mysql.connection.commit()
        finally:
            if cur:
                cur.close()
    
    @staticmethod
    def add_points(user_id, points):
        """Add points to user"""
        cur = None
        try:
            cur = db_cursor()
            cur.execute("""
                UPDATE user_stats SET points = points + %s WHERE user_id = %s
            """, (points, user_id))
            mysql.connection.commit()
        finally:
            if cur:
                cur.close()
    
    @staticmethod
    def get_by_user_id(user_id):
        """Get stats for a user"""
        cur = None
        try:
            cur = db_cursor()
            cur.execute("SELECT * FROM user_stats WHERE user_id = %s", [user_id])
            row = cur.fetchone()
            if row:
                cols = [desc[0] for desc in cur.description]
                return dict(zip(cols, row))
            return None
        finally:
            if cur:
                cur.close()

class UserActivity:
    @staticmethod
    def log_activity(user_id, activity_type, duration_minutes):
        """Log user activity"""
        cur = None
        try:
            cur = db_cursor()
            cur.execute("""
                INSERT INTO user_activity (user_id, activity_type, duration_minutes, activity_date)
                VALUES (%s, %s, %s, CURDATE())
            """, (user_id, activity_type, duration_minutes))
            mysql.connection.commit()
        finally:
            if cur:
                cur.close()
    
    @staticmethod
    def get_weekly_activity(user_id):
        """Get user's activity for the past week"""
        cur = None
        try:
            cur = db_cursor()
            cur.execute("""
                SELECT activity_type, SUM(duration_minutes) as total_minutes, activity_date
                FROM user_activity 
                WHERE user_id = %s AND activity_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
                GROUP BY activity_type, activity_date
                ORDER BY activity_date DESC
            """, [user_id])
            rows = cur.fetchall()
            if rows:
                cols = [desc[0] for desc in cur.description]
                return [dict(zip(cols, row)) for row in rows]
            return []
        finally:
            if cur:
                cur.close()
    
    @staticmethod
    def get_user_stats(user_id):
        """Get comprehensive user statistics"""
        cur = None
        try:
            cur = db_cursor()
            
            # Get basic stats
            cur.execute("SELECT * FROM user_stats WHERE user_id = %s", [user_id])
            stats = cur.fetchone() or {}
            
            # Get total study hours from activities
            cur.execute("""
                SELECT COALESCE(SUM(duration_minutes), 0) as total_minutes
                FROM user_activity WHERE user_id = %s
            """, [user_id])
            total_minutes = cur.fetchone()['total_minutes']
            
            # Get completed tasks count
            cur.execute("""
                SELECT COUNT(*) as completed_tasks
                FROM user_tasks WHERE user_id = %s AND completed = 1
            """, [user_id])
            completed_tasks = cur.fetchone()['completed_tasks']
            
            # Get active sessions count
            cur.execute("""
                SELECT COUNT(*) as active_sessions
                FROM user_sessions WHERE user_id = %s AND end_time IS NULL
            """, [user_id])
            active_sessions = cur.fetchone()['active_sessions']
            
            # Calculate streak days
            streak_days = UserActivity.calculate_streak_days(user_id)
            
            return {
                **stats,
                'total_hours': round(total_minutes / 60, 1),
                'completed_tasks': completed_tasks,
                'active_sessions': active_sessions,
                'streak_days': streak_days
            }
        finally:
            if cur:
                cur.close()
    
    @staticmethod
    def get_today_stats(user_id):
        """Get today's statistics"""
        cur = None
        try:
            cur = db_cursor()
            
            # Today's study time
            cur.execute("""
                SELECT COALESCE(SUM(duration_minutes), 0) as today_minutes
                FROM user_activity 
                WHERE user_id = %s AND activity_date = CURDATE()
            """, [user_id])
            today_minutes = cur.fetchone()['today_minutes']
            
            # Today's completed tasks
            cur.execute("""
                SELECT COUNT(*) as today_tasks
                FROM user_tasks 
                WHERE user_id = %s AND completed = 1 
                AND DATE(completed_at) = CURDATE()
            """, [user_id])
            today_tasks = cur.fetchone()['today_tasks']
            
            # Today's total tasks
            cur.execute("""
                SELECT COUNT(*) as total_tasks
                FROM user_tasks 
                WHERE user_id = %s AND DATE(created_at) = CURDATE()
            """, [user_id])
            total_tasks = cur.fetchone()['total_tasks']
            
            return {
                'today_hours': round(today_minutes / 60, 1),
                'today_completed_tasks': today_tasks,
                'today_total_tasks': total_tasks,
                'today_progress': round((today_tasks / max(total_tasks, 1)) * 100, 1)
            }
        finally:
            if cur:
                cur.close()
    
    @staticmethod
    def calculate_streak_days(user_id):
        """Calculate consecutive days of activity"""
        cur = None
        try:
            cur = db_cursor()
            cur.execute("""
                SELECT DISTINCT activity_date
                FROM user_activity 
                WHERE user_id = %s 
                ORDER BY activity_date DESC
                LIMIT 30
            """, [user_id])
            
            dates = [row['activity_date'] for row in cur.fetchall()]
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
    
    @staticmethod
    def get_user_tasks(user_id, limit=50):
        """Get user tasks"""
        cur = None
        try:
            cur = db_cursor()
            cur.execute("""
                SELECT * FROM user_tasks 
                WHERE user_id = %s 
                ORDER BY created_at DESC 
                LIMIT %s
            """, (user_id, limit))
            
            tasks = cur.fetchall()
            return tasks or []
        finally:
            if cur:
                cur.close()
    
    @staticmethod
    def create_task(user_id, text, priority='medium'):
        """Create a new task"""
        cur = None
        try:
            cur = db_cursor()
            cur.execute("""
                INSERT INTO user_tasks (user_id, text, priority, created_at)
                VALUES (%s, %s, %s, NOW())
            """, (user_id, text, priority))
            mysql.connection.commit()
            return cur.lastrowid
        finally:
            if cur:
                cur.close()
    
    @staticmethod
    def update_task(task_id, user_id, updates):
        """Update a task"""
        cur = None
        try:
            cur = db_cursor()
            
            update_fields = []
            values = []
            
            if 'completed' in updates:
                update_fields.append("completed = %s")
                values.append(updates['completed'])
                if updates['completed']:
                    update_fields.append("completed_at = NOW()")
                else:
                    update_fields.append("completed_at = NULL")
            
            if 'text' in updates:
                update_fields.append("text = %s")
                values.append(updates['text'])
            
            if 'priority' in updates:
                update_fields.append("priority = %s")
                values.append(updates['priority'])
            
            if update_fields:
                values.extend([task_id, user_id])
                query = f"""
                    UPDATE user_tasks 
                    SET {', '.join(update_fields)}
                    WHERE id = %s AND user_id = %s
                """
                cur.execute(query, values)
                mysql.connection.commit()
        finally:
            if cur:
                cur.close()
    
    @staticmethod
    def delete_task(task_id, user_id):
        """Delete a task"""
        cur = None
        try:
            cur = db_cursor()
            cur.execute("""
                DELETE FROM user_tasks 
                WHERE id = %s AND user_id = %s
            """, (task_id, user_id))
            mysql.connection.commit()
        finally:
            if cur:
                cur.close()
    
    @staticmethod
    def get_recent_activities(user_id, limit=20):
        """Get recent user activities"""
        cur = None
        try:
            cur = db_cursor()
            cur.execute("""
                SELECT * FROM user_activity_log 
                WHERE user_id = %s 
                ORDER BY created_at DESC 
                LIMIT %s
            """, (user_id, limit))
            
            activities = cur.fetchall()
            return activities or []
        finally:
            if cur:
                cur.close()
    
    @staticmethod
    def log_activity(user_id, activity_type, description, xp_earned=0):
        """Log user activity with XP"""
        cur = None
        try:
            cur = db_cursor()
            cur.execute("""
                INSERT INTO user_activity_log 
                (user_id, activity_type, description, xp_earned, created_at)
                VALUES (%s, %s, %s, %s, NOW())
            """, (user_id, activity_type, description, xp_earned))
            mysql.connection.commit()
            
            # Update user points if XP earned
            if xp_earned > 0:
                UserStats.add_points(user_id, xp_earned)
            
            return cur.lastrowid
        finally:
            if cur:
                cur.close()
    
    @staticmethod
    def start_session(user_id, session_type='study'):
        """Start a focus session"""
        cur = None
        try:
            cur = db_cursor()
            cur.execute("""
                INSERT INTO user_sessions 
                (user_id, session_type, start_time)
                VALUES (%s, %s, NOW())
            """, (user_id, session_type))
            mysql.connection.commit()
            return cur.lastrowid
        finally:
            if cur:
                cur.close()
    
    @staticmethod
    def end_session(session_id, user_id):
        """End a focus session and return duration in minutes"""
        cur = None
        try:
            cur = db_cursor()
            
            # Get session start time
            cur.execute("""
                SELECT start_time FROM user_sessions 
                WHERE id = %s AND user_id = %s AND end_time IS NULL
            """, (session_id, user_id))
            
            session = cur.fetchone()
            if not session:
                return 0
            
            # Update session end time
            cur.execute("""
                UPDATE user_sessions 
                SET end_time = NOW()
                WHERE id = %s AND user_id = %s
            """, (session_id, user_id))
            
            # Calculate duration
            cur.execute("""
                SELECT TIMESTAMPDIFF(MINUTE, start_time, end_time) as duration
                FROM user_sessions 
                WHERE id = %s
            """, [session_id])
            
            duration = cur.fetchone()['duration']
            
            # Log as activity
            UserActivity.log_activity(user_id, 'study', duration)
            
            mysql.connection.commit()
            return duration
        finally:
            if cur:
                cur.close()
    
    @staticmethod
    def get_weekly_progress(user_id):
        """Get weekly progress data for charts"""
        cur = None
        try:
            cur = db_cursor()
            
            # Get last 7 days of activity
            cur.execute("""
                SELECT 
                    DATE(activity_date) as date,
                    SUM(duration_minutes) as study_minutes,
                    COUNT(DISTINCT user_id) as sessions
                FROM user_activity 
                WHERE user_id = %s 
                AND activity_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
                GROUP BY DATE(activity_date)
                ORDER BY date
            """, [user_id])
            
            activity_data = cur.fetchall()
            
            # Get tasks completed per day
            cur.execute("""
                SELECT 
                    DATE(completed_at) as date,
                    COUNT(*) as completed_tasks
                FROM user_tasks 
                WHERE user_id = %s 
                AND completed = 1
                AND completed_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
                GROUP BY DATE(completed_at)
                ORDER BY date
            """, [user_id])
            
            task_data = cur.fetchall()
            
            return {
                'activity': activity_data or [],
                'tasks': task_data or []
            }
        finally:
            if cur:
                cur.close()
    
    @staticmethod
    def get_streak_details(user_id):
        """Get detailed streak information"""
        cur = None
        try:
            cur = db_cursor()
            
            # Get current streak
            current_streak = UserActivity.calculate_streak_days(user_id)
            
            # Get longest streak
            cur.execute("""
                SELECT activity_date
                FROM user_activity 
                WHERE user_id = %s 
                GROUP BY activity_date
                ORDER BY activity_date
            """, [user_id])
            
            dates = [row['activity_date'] for row in cur.fetchall()]
            
            longest_streak = 0
            current_count = 0
            
            for i in range(len(dates)):
                if i == 0 or dates[i] == dates[i-1] + timedelta(days=1):
                    current_count += 1
                    longest_streak = max(longest_streak, current_count)
                else:
                    current_count = 1
            
            # Get this week's activity
            cur.execute("""
                SELECT COUNT(DISTINCT activity_date) as active_days
                FROM user_activity 
                WHERE user_id = %s 
                AND activity_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
            """, [user_id])
            
            week_active_days = cur.fetchone()['active_days']
            
            # Get this month's activity
            cur.execute("""
                SELECT COUNT(DISTINCT activity_date) as active_days
                FROM user_activity 
                WHERE user_id = %s 
                AND activity_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
            """, [user_id])
            
            month_active_days = cur.fetchone()['active_days']
            
            return {
                'current_streak': current_streak,
                'longest_streak': longest_streak,
                'week_active_days': week_active_days,
                'month_active_days': month_active_days,
                'streak_percentage': min((current_streak / 30) * 100, 100) if current_streak else 0
            }
        finally:
            if cur:
                cur.close()