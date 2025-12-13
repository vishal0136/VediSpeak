"""
Course and Module Models for Learning Management System
- Course management and progress tracking
- Module completion and statistics
- Real-time progress updates
"""
from ..extensions import mysql
from datetime import datetime, timedelta
import json


class Course:
    """Course model for managing learning courses"""
    
    @staticmethod
    def get_all_courses():
        """Get all available courses"""
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                SELECT id, title, title_hindi, description, level, duration_hours, 
                       total_modules, category, created_at, updated_at
                FROM courses 
                WHERE is_active = 1 
                ORDER BY sort_order, created_at
            """)
            courses = cur.fetchall()
            cur.close()
            
            return [
                {
                    'id': course['id'],
                    'title': course['title'],
                    'title_hindi': course['title_hindi'],
                    'description': course['description'],
                    'level': course['level'],
                    'duration_hours': course['duration_hours'],
                    'total_modules': course['total_modules'],
                    'category': course['category'],
                    'created_at': course['created_at'],
                    'updated_at': course['updated_at']
                }
                for course in courses
            ]
        except Exception as e:
            print(f"Error getting courses: {e}")
            return []
    
    @staticmethod
    def get_course_by_id(course_id):
        """Get course by ID"""
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                SELECT id, title, title_hindi, description, level, duration_hours, 
                       total_modules, category, created_at, updated_at
                FROM courses 
                WHERE id = %s AND is_active = 1
            """, [course_id])
            course = cur.fetchone()
            cur.close()
            
            if course:
                return {
                    'id': course['id'],
                    'title': course['title'],
                    'title_hindi': course['title_hindi'],
                    'description': course['description'],
                    'level': course['level'],
                    'duration_hours': course['duration_hours'],
                    'total_modules': course['total_modules'],
                    'category': course['category'],
                    'created_at': course['created_at'],
                    'updated_at': course['updated_at']
                }
            return None
        except Exception as e:
            print(f"Error getting course: {e}")
            return None


class Module:
    """Module model for course modules"""
    
    @staticmethod
    def get_course_modules(course_id):
        """Get all modules for a course"""
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                SELECT id, course_id, title, title_hindi, description, module_order, 
                       duration_minutes, content_type, content_data, prerequisites, 
                       is_locked, created_at, updated_at
                FROM modules 
                WHERE course_id = %s AND is_active = 1 
                ORDER BY module_order
            """, [course_id])
            modules = cur.fetchall()
            cur.close()
            
            return [
                {
                    'id': module['id'],
                    'course_id': module['course_id'],
                    'title': module['title'],
                    'title_hindi': module['title_hindi'],
                    'description': module['description'],
                    'module_order': module['module_order'],
                    'duration_minutes': module['duration_minutes'],
                    'content_type': module['content_type'],
                    'content_data': json.loads(module['content_data']) if module['content_data'] else {},
                    'prerequisites': json.loads(module['prerequisites']) if module['prerequisites'] else [],
                    'is_locked': bool(module['is_locked']),
                    'created_at': module['created_at'],
                    'updated_at': module['updated_at']
                }
                for module in modules
            ]
        except Exception as e:
            print(f"Error getting modules: {e}")
            return []
    
    @staticmethod
    def get_module_by_id(module_id):
        """Get module by ID"""
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                SELECT id, course_id, title, title_hindi, description, module_order, 
                       duration_minutes, content_type, content_data, prerequisites, 
                       is_locked, created_at, updated_at
                FROM modules 
                WHERE id = %s AND is_active = 1
            """, [module_id])
            module = cur.fetchone()
            cur.close()
            
            if module:
                return {
                    'id': module['id'],
                    'course_id': module['course_id'],
                    'title': module['title'],
                    'title_hindi': module['title_hindi'],
                    'description': module['description'],
                    'module_order': module['module_order'],
                    'duration_minutes': module['duration_minutes'],
                    'content_type': module['content_type'],
                    'content_data': json.loads(module['content_data']) if module['content_data'] else {},
                    'prerequisites': json.loads(module['prerequisites']) if module['prerequisites'] else [],
                    'is_locked': bool(module['is_locked']),
                    'created_at': module['created_at'],
                    'updated_at': module['updated_at']
                }
            return None
        except Exception as e:
            print(f"Error getting module: {e}")
            return None


class UserProgress:
    """User progress tracking for courses and modules"""
    
    @staticmethod
    def get_user_course_progress(user_id, course_id):
        """Get user's progress for a specific course"""
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                SELECT id, user_id, course_id, modules_completed, total_modules, 
                       progress_percentage, time_spent_minutes, last_accessed, 
                       is_completed, completion_date, created_at, updated_at
                FROM user_course_progress 
                WHERE user_id = %s AND course_id = %s
            """, [user_id, course_id])
            progress = cur.fetchone()
            cur.close()
            
            if progress:
                return {
                    'id': progress['id'],
                    'user_id': progress['user_id'],
                    'course_id': progress['course_id'],
                    'modules_completed': progress['modules_completed'],
                    'total_modules': progress['total_modules'],
                    'progress_percentage': float(progress['progress_percentage']) if progress['progress_percentage'] else 0.0,
                    'time_spent_minutes': progress['time_spent_minutes'],
                    'last_accessed': progress['last_accessed'].isoformat() if progress['last_accessed'] else None,
                    'is_completed': bool(progress['is_completed']),
                    'completion_date': progress['completion_date'].isoformat() if progress['completion_date'] else None,
                    'created_at': progress['created_at'].isoformat() if progress['created_at'] else None,
                    'updated_at': progress['updated_at'].isoformat() if progress['updated_at'] else None
                }
            return None
        except Exception as e:
            print(f"Error getting user course progress: {e}")
            return None
    
    @staticmethod
    def get_user_module_progress(user_id, module_id):
        """Get user's progress for a specific module"""
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                SELECT id, user_id, module_id, progress_percentage, time_spent_minutes, 
                       quiz_score, quiz_attempts, is_completed, completion_date, 
                       last_accessed, created_at, updated_at
                FROM user_module_progress 
                WHERE user_id = %s AND module_id = %s
            """, [user_id, module_id])
            progress = cur.fetchone()
            cur.close()
            
            if progress:
                return {
                    'id': progress['id'],
                    'user_id': progress['user_id'],
                    'module_id': progress['module_id'],
                    'progress_percentage': float(progress['progress_percentage']) if progress['progress_percentage'] else 0.0,
                    'time_spent_minutes': progress['time_spent_minutes'],
                    'quiz_score': float(progress['quiz_score']) if progress['quiz_score'] else None,
                    'quiz_attempts': progress['quiz_attempts'],
                    'is_completed': bool(progress['is_completed']),
                    'completion_date': progress['completion_date'].isoformat() if progress['completion_date'] else None,
                    'last_accessed': progress['last_accessed'].isoformat() if progress['last_accessed'] else None,
                    'created_at': progress['created_at'].isoformat() if progress['created_at'] else None,
                    'updated_at': progress['updated_at'].isoformat() if progress['updated_at'] else None
                }
            return None
        except Exception as e:
            print(f"Error getting user module progress: {e}")
            return None
    
    @staticmethod
    def update_module_progress(user_id, module_id, progress_percentage, time_spent=0, quiz_score=None):
        """Update user's module progress"""
        try:
            cur = mysql.connection.cursor()
            
            # Check if progress record exists
            existing = UserProgress.get_user_module_progress(user_id, module_id)
            
            if existing:
                # Update existing record
                cur.execute("""
                    UPDATE user_module_progress 
                    SET progress_percentage = %s, 
                        time_spent_minutes = time_spent_minutes + %s,
                        quiz_score = COALESCE(%s, quiz_score),
                        quiz_attempts = CASE WHEN %s IS NOT NULL THEN quiz_attempts + 1 ELSE quiz_attempts END,
                        is_completed = %s,
                        completion_date = CASE WHEN %s >= 100 THEN NOW() ELSE completion_date END,
                        last_accessed = NOW(),
                        updated_at = NOW()
                    WHERE user_id = %s AND module_id = %s
                """, [
                    progress_percentage, time_spent, quiz_score, quiz_score,
                    progress_percentage >= 100, progress_percentage,
                    user_id, module_id
                ])
            else:
                # Create new record
                cur.execute("""
                    INSERT INTO user_module_progress 
                    (user_id, module_id, progress_percentage, time_spent_minutes, 
                     quiz_score, quiz_attempts, is_completed, completion_date, 
                     last_accessed, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW(), NOW())
                """, [
                    user_id, module_id, progress_percentage, time_spent,
                    quiz_score, 1 if quiz_score is not None else 0,
                    progress_percentage >= 100,
                    datetime.now() if progress_percentage >= 100 else None
                ])
            
            mysql.connection.commit()
            cur.close()
            
            # Update course progress
            UserProgress._update_course_progress(user_id, module_id)
            
            return True
        except Exception as e:
            print(f"Error updating module progress: {e}")
            mysql.connection.rollback()
            return False
    
    @staticmethod
    def _update_course_progress(user_id, module_id):
        """Update course progress based on module completion"""
        try:
            cur = mysql.connection.cursor()
            
            # Get module's course
            cur.execute("SELECT course_id FROM modules WHERE id = %s", [module_id])
            course_result = cur.fetchone()
            if not course_result:
                return
            
            course_id = course_result['course_id']
            
            # Calculate course progress
            cur.execute("""
                SELECT 
                    COUNT(*) as total_modules,
                    SUM(CASE WHEN ump.is_completed = 1 THEN 1 ELSE 0 END) as completed_modules,
                    AVG(ump.progress_percentage) as avg_progress,
                    SUM(ump.time_spent_minutes) as total_time
                FROM modules m
                LEFT JOIN user_module_progress ump ON m.id = ump.module_id AND ump.user_id = %s
                WHERE m.course_id = %s AND m.is_active = 1
            """, [user_id, course_id])
            
            stats = cur.fetchone()
            total_modules = stats['total_modules'] or 0
            completed_modules = stats['completed_modules'] or 0
            avg_progress = float(stats['avg_progress']) if stats['avg_progress'] else 0.0
            total_time = stats['total_time'] or 0
            
            # Check if course progress record exists
            cur.execute("""
                SELECT id FROM user_course_progress 
                WHERE user_id = %s AND course_id = %s
            """, [user_id, course_id])
            
            if cur.fetchone():
                # Update existing record
                cur.execute("""
                    UPDATE user_course_progress 
                    SET modules_completed = %s,
                        total_modules = %s,
                        progress_percentage = %s,
                        time_spent_minutes = %s,
                        is_completed = %s,
                        completion_date = CASE WHEN %s = %s THEN NOW() ELSE completion_date END,
                        last_accessed = NOW(),
                        updated_at = NOW()
                    WHERE user_id = %s AND course_id = %s
                """, [
                    completed_modules, total_modules, avg_progress, total_time,
                    completed_modules == total_modules, completed_modules, total_modules,
                    user_id, course_id
                ])
            else:
                # Create new record
                cur.execute("""
                    INSERT INTO user_course_progress 
                    (user_id, course_id, modules_completed, total_modules, 
                     progress_percentage, time_spent_minutes, is_completed, 
                     completion_date, last_accessed, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW(), NOW())
                """, [
                    user_id, course_id, completed_modules, total_modules,
                    avg_progress, total_time, completed_modules == total_modules,
                    datetime.now() if completed_modules == total_modules else None
                ])
            
            mysql.connection.commit()
            cur.close()
            
        except Exception as e:
            print(f"Error updating course progress: {e}")
            mysql.connection.rollback()
    
    @staticmethod
    def get_user_overall_stats(user_id):
        """Get user's overall learning statistics"""
        try:
            cur = mysql.connection.cursor()
            
            # Get course statistics
            cur.execute("""
                SELECT 
                    COUNT(*) as total_courses,
                    SUM(CASE WHEN is_completed = 1 THEN 1 ELSE 0 END) as completed_courses,
                    SUM(modules_completed) as total_modules_completed,
                    SUM(time_spent_minutes) as total_time_minutes,
                    AVG(progress_percentage) as avg_progress
                FROM user_course_progress 
                WHERE user_id = %s
            """, [user_id])
            
            course_stats = cur.fetchone()
            
            # Get recent activity
            cur.execute("""
                SELECT DATE(last_accessed) as activity_date, COUNT(*) as modules_accessed
                FROM user_module_progress 
                WHERE user_id = %s AND last_accessed >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                GROUP BY DATE(last_accessed)
                ORDER BY activity_date DESC
                LIMIT 30
            """, [user_id])
            
            recent_activity = cur.fetchall()
            
            # Calculate streak
            cur.execute("""
                SELECT DISTINCT DATE(last_accessed) as activity_date
                FROM user_module_progress 
                WHERE user_id = %s AND last_accessed >= DATE_SUB(NOW(), INTERVAL 365 DAY)
                ORDER BY activity_date DESC
            """, [user_id])
            
            activity_dates = [row['activity_date'] for row in cur.fetchall()]
            
            # Calculate current streak
            streak_days = 0
            current_date = datetime.now().date()
            
            for i, activity_date in enumerate(activity_dates):
                expected_date = current_date - timedelta(days=i)
                if activity_date == expected_date:
                    streak_days += 1
                else:
                    break
            
            cur.close()
            
            return {
                'total_courses': course_stats['total_courses'] or 0,
                'completed_courses': course_stats['completed_courses'] or 0,
                'total_modules_completed': course_stats['total_modules_completed'] or 0,
                'total_time_minutes': course_stats['total_time_minutes'] or 0,
                'avg_progress': round(float(course_stats['avg_progress']) if course_stats['avg_progress'] else 0, 1),
                'streak_days': streak_days,
                'recent_activity': [
                    {'date': str(activity['activity_date']), 'modules': activity['modules_accessed']}
                    for activity in recent_activity
                ]
            }
            
        except Exception as e:
            print(f"Error getting user stats: {e}")
            return {
                'total_courses': 0,
                'completed_courses': 0,
                'total_modules_completed': 0,
                'total_time_minutes': 0,
                'avg_progress': 0,
                'streak_days': 0,
                'recent_activity': []
            }


class Quiz:
    """Quiz model for module assessments"""
    
    @staticmethod
    def get_module_quiz(module_id):
        """Get quiz for a module"""
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                SELECT id, module_id, title, questions_data, passing_score, 
                       time_limit_minutes, max_attempts, created_at, updated_at
                FROM quizzes 
                WHERE module_id = %s AND is_active = 1
            """, [module_id])
            quiz = cur.fetchone()
            cur.close()
            
            if quiz:
                return {
                    'id': quiz['id'],
                    'module_id': quiz['module_id'],
                    'title': quiz['title'],
                    'questions': json.loads(quiz['questions_data']) if quiz['questions_data'] else [],
                    'passing_score': float(quiz['passing_score']) if quiz['passing_score'] else 70.0,
                    'time_limit_minutes': quiz['time_limit_minutes'],
                    'max_attempts': quiz['max_attempts'],
                    'created_at': quiz['created_at'],
                    'updated_at': quiz['updated_at']
                }
            return None
        except Exception as e:
            print(f"Error getting quiz: {e}")
            return None
    
    @staticmethod
    def submit_quiz_attempt(user_id, quiz_id, answers, score):
        """Submit a quiz attempt"""
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                INSERT INTO quiz_attempts 
                (user_id, quiz_id, answers_data, score, completed_at, created_at)
                VALUES (%s, %s, %s, %s, NOW(), NOW())
            """, [user_id, quiz_id, json.dumps(answers), score])
            
            mysql.connection.commit()
            attempt_id = cur.lastrowid
            cur.close()
            
            return attempt_id
        except Exception as e:
            print(f"Error submitting quiz attempt: {e}")
            mysql.connection.rollback()
            return None