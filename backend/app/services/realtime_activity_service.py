"""
Real-time Activity Tracking Service
Handles all real-time user activity, progress tracking, and statistics
"""
from datetime import datetime, timedelta, date
from ..extensions import mysql
from ..utils.db_helpers import db_cursor
import json
from typing import Dict, List, Optional, Tuple

class RealtimeActivityService:
    """Service for managing real-time user activity and statistics"""
    
    # XP Points Configuration
    XP_REWARDS = {
        'module_start': 5,
        'module_complete': 50,
        'quiz_attempt': 10,
        'quiz_pass': 25,
        'practice_session': 15,
        'daily_goal': 30,
        'weekly_goal': 100,
        'streak_milestone': 20,
        'skill_levelup': 40
    }
    
    # Skill Level Thresholds
    SKILL_LEVELS = {
        'Beginner': 0,
        'Elementary': 100,
        'Intermediate': 300,
        'Advanced': 600,
        'Expert': 1000,
        'Master': 1500
    }
    
    @classmethod
    def initialize_user_stats(cls, user_id: int) -> bool:
        """Initialize real-time stats for a new user"""
        cur = None
        try:
            cur = db_cursor()
            
            # Create user stats entry
            cur.execute("""
                INSERT IGNORE INTO user_stats_realtime (user_id)
                VALUES (%s)
            """, [user_id])
            
            # Create skill development entries
            skills = ['alphabet', 'numbers', 'vocabulary', 'grammar', 'conversation', 'comprehension']
            for skill in skills:
                cur.execute("""
                    INSERT IGNORE INTO skill_development (user_id, skill_category)
                    VALUES (%s, %s)
                """, (user_id, skill))
            
            # Create weekly goal
            week_start = date.today() - timedelta(days=date.today().weekday())
            cur.execute("""
                INSERT IGNORE INTO weekly_goals (user_id, week_start_date)
                VALUES (%s, %s)
            """, (user_id, week_start))
            
            mysql.connection.commit()
            return True
        except Exception as e:
            print(f"Error initializing user stats: {e}")
            return False
        finally:
            if cur:
                cur.close()
    
    @classmethod
    def log_activity(cls, user_id: int, activity_type: str, **kwargs) -> int:
        """Log user activity and update statistics"""
        cur = None
        try:
            cur = db_cursor()
            
            # Extract parameters
            module_id = kwargs.get('module_id')
            description = kwargs.get('description', '')
            duration_minutes = kwargs.get('duration_minutes', 0)
            metadata = kwargs.get('metadata', {})
            
            # Calculate XP earned
            xp_earned = cls.XP_REWARDS.get(activity_type, 0)
            
            # Special XP calculations
            if activity_type == 'practice_session' and duration_minutes > 0:
                xp_earned += min(duration_minutes // 5, 20)  # Bonus XP for longer sessions
            
            # Log the activity
            cur.execute("""
                INSERT INTO activity_log_realtime 
                (user_id, activity_type, module_id, description, xp_earned, duration_minutes, metadata)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (user_id, activity_type, module_id, description, xp_earned, duration_minutes, json.dumps(metadata)))
            
            activity_id = cur.lastrowid
            
            # Update user stats
            cls._update_user_stats(cur, user_id, activity_type, xp_earned, duration_minutes, module_id)
            
            # Update daily summary
            cls._update_daily_summary(cur, user_id, activity_type, duration_minutes, xp_earned)
            
            # Update weekly goals
            cls._update_weekly_goals(cur, user_id, activity_type, duration_minutes)
            
            # Update skill development
            if module_id:
                cls._update_skill_development(cur, user_id, module_id, xp_earned)
            
            mysql.connection.commit()
            return activity_id
        except Exception as e:
            print(f"Error logging activity: {e}")
            return 0
        finally:
            if cur:
                cur.close()
    
    @classmethod
    def update_module_progress(cls, user_id: int, module_id: int, progress_data: Dict) -> bool:
        """Update module progress and trigger related activities"""
        cur = None
        try:
            cur = db_cursor()
            
            # Get module name mapping
            module_names = {
                1: "ISL Alphabet & Fingerspelling",
                2: "Numbers & Mathematical Concepts",
                3: "Family & Relationships",
                4: "Colors, Shapes & Objects",
                5: "Time & Calendar Concepts",
                6: "Basic Grammar & Sentence Structure"
            }
            
            module_name = module_names.get(module_id, f"Module {module_id}")
            progress_percentage = progress_data.get('progress_percentage', 0)
            time_spent = progress_data.get('time_spent_minutes', 0)
            quiz_score = progress_data.get('quiz_score', 0)
            
            # Update or insert module progress
            cur.execute("""
                INSERT INTO module_progress_realtime 
                (user_id, module_id, module_name, progress_percentage, time_spent_minutes, quiz_score, is_completed, completion_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                progress_percentage = VALUES(progress_percentage),
                time_spent_minutes = time_spent_minutes + VALUES(time_spent_minutes),
                quiz_score = GREATEST(quiz_score, VALUES(quiz_score)),
                is_completed = VALUES(is_completed),
                completion_date = CASE WHEN VALUES(is_completed) AND NOT is_completed THEN NOW() ELSE completion_date END,
                last_accessed = NOW()
            """, (user_id, module_id, module_name, progress_percentage, time_spent, quiz_score, 
                  progress_percentage >= 100, datetime.now() if progress_percentage >= 100 else None))
            
            # Log appropriate activities
            if progress_percentage >= 100:
                # Check if this is a new completion
                cur.execute("""
                    SELECT is_completed FROM module_progress_realtime 
                    WHERE user_id = %s AND module_id = %s
                """, (user_id, module_id))
                
                result = cur.fetchone()
                if not result or not result['is_completed']:
                    cls.log_activity(user_id, 'module_complete', 
                                   module_id=module_id, 
                                   description=f"Completed {module_name}")
            
            if quiz_score > 0:
                quiz_passed = quiz_score >= 70  # Assuming 70% is passing
                activity_type = 'quiz_pass' if quiz_passed else 'quiz_attempt'
                cls.log_activity(user_id, activity_type,
                               module_id=module_id,
                               description=f"Quiz score: {quiz_score}%",
                               metadata={'score': quiz_score})
            
            if time_spent > 0:
                cls.log_activity(user_id, 'practice_session',
                               module_id=module_id,
                               duration_minutes=time_spent,
                               description=f"Studied {module_name}")
            
            mysql.connection.commit()
            return True
        except Exception as e:
            print(f"Error updating module progress: {e}")
            return False
        finally:
            if cur:
                cur.close()
    
    @classmethod
    def get_user_dashboard_stats(cls, user_id: int) -> Dict:
        """Get comprehensive dashboard statistics for user"""
        cur = None
        try:
            cur = db_cursor()
            
            # Get basic stats
            cur.execute("""
                SELECT * FROM user_stats_realtime WHERE user_id = %s
            """, [user_id])
            basic_stats = cur.fetchone() or {}
            
            # Get today's activity
            cur.execute("""
                SELECT 
                    COALESCE(SUM(duration_minutes), 0) as today_minutes,
                    COALESCE(SUM(xp_earned), 0) as today_xp,
                    COUNT(*) as today_activities
                FROM activity_log_realtime 
                WHERE user_id = %s AND DATE(created_at) = CURDATE()
            """, [user_id])
            today_stats = cur.fetchone() or {}
            
            # Get weekly progress
            cur.execute("""
                SELECT 
                    current_study_minutes,
                    study_minutes_goal,
                    current_modules,
                    modules_goal,
                    current_practice_sessions,
                    practice_sessions_goal
                FROM weekly_goals 
                WHERE user_id = %s AND week_start_date = DATE_SUB(CURDATE(), INTERVAL WEEKDAY(CURDATE()) DAY)
            """, [user_id])
            weekly_stats = cur.fetchone() or {}
            
            # Get skill levels
            cur.execute("""
                SELECT skill_category, skill_level, xp_points 
                FROM skill_development 
                WHERE user_id = %s
                ORDER BY skill_category
            """, [user_id])
            skills = cur.fetchall() or []
            
            # Get recent activities
            cur.execute("""
                SELECT activity_type, description, xp_earned, created_at, module_id
                FROM activity_log_realtime 
                WHERE user_id = %s 
                ORDER BY created_at DESC 
                LIMIT 10
            """, [user_id])
            recent_activities = cur.fetchall() or []
            
            # Get active modules
            cur.execute("""
                SELECT module_id, module_name, progress_percentage, time_spent_minutes, last_accessed
                FROM module_progress_realtime 
                WHERE user_id = %s AND progress_percentage > 0 AND progress_percentage < 100
                ORDER BY last_accessed DESC
                LIMIT 5
            """, [user_id])
            active_modules = cur.fetchall() or []
            
            # Calculate streak details
            streak_info = cls._calculate_streak_details(cur, user_id)
            
            # Calculate skill level
            total_xp = basic_stats.get('total_xp_points', 0)
            skill_level = cls._get_skill_level_from_xp(total_xp)
            
            return {
                'basic_stats': {
                    'total_study_hours': round(basic_stats.get('total_study_minutes', 0) / 60, 1),
                    'modules_completed': basic_stats.get('modules_completed', 0),
                    'total_xp_points': total_xp,
                    'skill_level': skill_level,
                    'current_streak': basic_stats.get('current_streak_days', 0),
                    'longest_streak': basic_stats.get('longest_streak_days', 0)
                },
                'today_stats': {
                    'study_minutes': today_stats.get('today_minutes', 0),
                    'study_hours': round(today_stats.get('today_minutes', 0) / 60, 1),
                    'xp_earned': today_stats.get('today_xp', 0),
                    'activities_count': today_stats.get('today_activities', 0)
                },
                'weekly_progress': {
                    'study_minutes': weekly_stats.get('current_study_minutes', 0),
                    'study_goal': weekly_stats.get('study_minutes_goal', 300),
                    'modules_completed': weekly_stats.get('current_modules', 0),
                    'modules_goal': weekly_stats.get('modules_goal', 2),
                    'practice_sessions': weekly_stats.get('current_practice_sessions', 0),
                    'practice_goal': weekly_stats.get('practice_sessions_goal', 10)
                },
                'skills': skills,
                'recent_activities': recent_activities,
                'active_modules': active_modules,
                'streak_info': streak_info
            }
        except Exception as e:
            print(f"Error getting dashboard stats: {e}")
            return {}
        finally:
            if cur:
                cur.close()
    
    @classmethod
    def get_live_activity_feed(cls, user_id: int, limit: int = 20) -> List[Dict]:
        """Get live activity feed for real-time updates"""
        cur = None
        try:
            cur = db_cursor()
            
            cur.execute("""
                SELECT 
                    al.activity_type,
                    al.description,
                    al.xp_earned,
                    al.duration_minutes,
                    al.created_at,
                    al.module_id,
                    mp.module_name
                FROM activity_log_realtime al
                LEFT JOIN module_progress_realtime mp ON al.module_id = mp.module_id AND al.user_id = mp.user_id
                WHERE al.user_id = %s 
                ORDER BY al.created_at DESC 
                LIMIT %s
            """, (user_id, limit))
            
            activities = cur.fetchall() or []
            
            # Format activities for display
            formatted_activities = []
            for activity in activities:
                formatted_activity = {
                    'type': activity['activity_type'],
                    'description': activity['description'],
                    'xp_earned': activity['xp_earned'],
                    'duration_minutes': activity['duration_minutes'],
                    'timestamp': activity['created_at'],
                    'module_name': activity.get('module_name'),
                    'time_ago': cls._format_time_ago(activity['created_at'])
                }
                formatted_activities.append(formatted_activity)
            
            return formatted_activities
        except Exception as e:
            print(f"Error getting activity feed: {e}")
            return []
        finally:
            if cur:
                cur.close()
    
    @classmethod
    def get_weekly_chart_data(cls, user_id: int) -> Dict:
        """Get data for weekly progress charts"""
        cur = None
        try:
            cur = db_cursor()
            
            # Get last 7 days of activity
            cur.execute("""
                SELECT 
                    DATE(created_at) as activity_date,
                    SUM(duration_minutes) as study_minutes,
                    SUM(xp_earned) as xp_earned,
                    COUNT(CASE WHEN activity_type = 'practice_session' THEN 1 END) as practice_sessions,
                    COUNT(CASE WHEN activity_type = 'module_complete' THEN 1 END) as modules_completed
                FROM activity_log_realtime 
                WHERE user_id = %s 
                AND created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
                GROUP BY DATE(created_at)
                ORDER BY activity_date
            """, [user_id])
            
            weekly_data = cur.fetchall() or []
            
            # Fill in missing days with zeros
            chart_data = {
                'labels': [],
                'study_minutes': [],
                'xp_earned': [],
                'practice_sessions': [],
                'modules_completed': []
            }
            
            # Create a complete 7-day range
            for i in range(7):
                day = date.today() - timedelta(days=6-i)
                chart_data['labels'].append(day.strftime('%a'))
                
                # Find data for this day
                day_data = next((d for d in weekly_data if d['activity_date'] == day), None)
                
                if day_data:
                    chart_data['study_minutes'].append(day_data['study_minutes'] or 0)
                    chart_data['xp_earned'].append(day_data['xp_earned'] or 0)
                    chart_data['practice_sessions'].append(day_data['practice_sessions'] or 0)
                    chart_data['modules_completed'].append(day_data['modules_completed'] or 0)
                else:
                    chart_data['study_minutes'].append(0)
                    chart_data['xp_earned'].append(0)
                    chart_data['practice_sessions'].append(0)
                    chart_data['modules_completed'].append(0)
            
            return chart_data
        except Exception as e:
            print(f"Error getting chart data: {e}")
            return {}
        finally:
            if cur:
                cur.close()
    
    @classmethod
    def start_live_session(cls, user_id: int, session_type: str = 'study', module_id: int = None) -> int:
        """Start a live learning session"""
        cur = None
        try:
            cur = db_cursor()
            
            cur.execute("""
                INSERT INTO live_sessions (user_id, session_type, module_id)
                VALUES (%s, %s, %s)
            """, (user_id, session_type, module_id))
            
            session_id = cur.lastrowid
            
            # Log session start activity
            cls.log_activity(user_id, 'module_start' if module_id else 'practice_session',
                           module_id=module_id,
                           description=f"Started {session_type} session")
            
            mysql.connection.commit()
            return session_id
        except Exception as e:
            print(f"Error starting session: {e}")
            return 0
        finally:
            if cur:
                cur.close()
    
    @classmethod
    def end_live_session(cls, session_id: int, user_id: int) -> Dict:
        """End a live learning session and return summary"""
        cur = None
        try:
            cur = db_cursor()
            
            # Get session details
            cur.execute("""
                SELECT * FROM live_sessions 
                WHERE id = %s AND user_id = %s AND is_active = TRUE
            """, (session_id, user_id))
            
            session = cur.fetchone()
            if not session:
                return {}
            
            # Calculate duration
            duration_minutes = int((datetime.now() - session['start_time']).total_seconds() / 60)
            
            # Update session
            cur.execute("""
                UPDATE live_sessions 
                SET end_time = NOW(), duration_minutes = %s, is_active = FALSE
                WHERE id = %s
            """, (duration_minutes, session_id))
            
            # Log session completion
            cls.log_activity(user_id, 'practice_session',
                           module_id=session.get('module_id'),
                           duration_minutes=duration_minutes,
                           description=f"Completed {session['session_type']} session")
            
            mysql.connection.commit()
            
            return {
                'duration_minutes': duration_minutes,
                'session_type': session['session_type'],
                'module_id': session.get('module_id'),
                'xp_earned': cls.XP_REWARDS.get('practice_session', 0) + min(duration_minutes // 5, 20)
            }
        except Exception as e:
            print(f"Error ending session: {e}")
            return {}
        finally:
            if cur:
                cur.close()
    
    # Private helper methods
    @classmethod
    def _update_user_stats(cls, cur, user_id: int, activity_type: str, xp_earned: int, duration_minutes: int, module_id: int = None):
        """Update user statistics"""
        # Update basic stats
        cur.execute("""
            UPDATE user_stats_realtime 
            SET 
                total_study_minutes = total_study_minutes + %s,
                total_xp_points = total_xp_points + %s,
                modules_completed = modules_completed + %s,
                last_activity_date = CURDATE(),
                skill_level = %s
            WHERE user_id = %s
        """, (
            duration_minutes,
            xp_earned,
            1 if activity_type == 'module_complete' else 0,
            cls._get_skill_level_from_xp_query(cur, user_id, xp_earned),
            user_id
        ))
        
        # Update streak
        cls._update_streak(cur, user_id)
    
    @classmethod
    def _update_daily_summary(cls, cur, user_id: int, activity_type: str, duration_minutes: int, xp_earned: int):
        """Update daily activity summary"""
        cur.execute("""
            INSERT INTO daily_activity_summary 
            (user_id, activity_date, total_study_minutes, quizzes_completed, practice_sessions, xp_earned)
            VALUES (%s, CURDATE(), %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            total_study_minutes = total_study_minutes + VALUES(total_study_minutes),
            quizzes_completed = quizzes_completed + VALUES(quizzes_completed),
            practice_sessions = practice_sessions + VALUES(practice_sessions),
            xp_earned = xp_earned + VALUES(xp_earned)
        """, (
            user_id,
            duration_minutes,
            1 if activity_type in ['quiz_attempt', 'quiz_pass'] else 0,
            1 if activity_type == 'practice_session' else 0,
            xp_earned
        ))
    
    @classmethod
    def _update_weekly_goals(cls, cur, user_id: int, activity_type: str, duration_minutes: int):
        """Update weekly goals progress"""
        week_start = date.today() - timedelta(days=date.today().weekday())
        
        cur.execute("""
            INSERT INTO weekly_goals (user_id, week_start_date)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE
            current_study_minutes = current_study_minutes + %s,
            current_modules = current_modules + %s,
            current_practice_sessions = current_practice_sessions + %s
        """, (
            user_id,
            week_start,
            duration_minutes,
            1 if activity_type == 'module_complete' else 0,
            1 if activity_type == 'practice_session' else 0
        ))
    
    @classmethod
    def _update_skill_development(cls, cur, user_id: int, module_id: int, xp_earned: int):
        """Update skill development based on module"""
        # Map modules to skills
        module_skill_map = {
            1: 'alphabet',
            2: 'numbers',
            3: 'vocabulary',
            4: 'vocabulary',
            5: 'vocabulary',
            6: 'grammar'
        }
        
        skill_category = module_skill_map.get(module_id, 'conversation')
        
        cur.execute("""
            UPDATE skill_development 
            SET 
                xp_points = xp_points + %s,
                skill_level = LEAST(10, 1 + FLOOR((xp_points + %s) / 100)),
                last_practice_date = NOW()
            WHERE user_id = %s AND skill_category = %s
        """, (xp_earned, xp_earned, user_id, skill_category))
    
    @classmethod
    def _update_streak(cls, cur, user_id: int):
        """Update user's activity streak"""
        # Get recent activity dates
        cur.execute("""
            SELECT DISTINCT DATE(created_at) as activity_date
            FROM activity_log_realtime 
            WHERE user_id = %s 
            ORDER BY activity_date DESC
            LIMIT 30
        """, [user_id])
        
        dates = [row['activity_date'] for row in cur.fetchall()]
        
        current_streak = 0
        longest_streak = 0
        
        if dates:
            # Calculate current streak
            today = date.today()
            yesterday = today - timedelta(days=1)
            
            if today in dates:
                current_streak = 1
                check_date = yesterday
                
                while check_date in dates:
                    current_streak += 1
                    check_date -= timedelta(days=1)
            elif yesterday in dates:
                current_streak = 1
                check_date = yesterday - timedelta(days=1)
                
                while check_date in dates:
                    current_streak += 1
                    check_date -= timedelta(days=1)
            
            # Calculate longest streak
            temp_streak = 0
            for i, activity_date in enumerate(dates):
                if i == 0 or activity_date == dates[i-1] - timedelta(days=1):
                    temp_streak += 1
                    longest_streak = max(longest_streak, temp_streak)
                else:
                    temp_streak = 1
        
        # Update user stats
        cur.execute("""
            UPDATE user_stats_realtime 
            SET current_streak_days = %s, longest_streak_days = GREATEST(longest_streak_days, %s)
            WHERE user_id = %s
        """, (current_streak, longest_streak, user_id))
    
    @classmethod
    def _calculate_streak_details(cls, cur, user_id: int) -> Dict:
        """Calculate detailed streak information"""
        cur.execute("""
            SELECT current_streak_days, longest_streak_days 
            FROM user_stats_realtime 
            WHERE user_id = %s
        """, [user_id])
        
        result = cur.fetchone()
        if not result:
            return {'current_streak': 0, 'longest_streak': 0, 'streak_percentage': 0}
        
        current_streak = result['current_streak_days'] or 0
        longest_streak = result['longest_streak_days'] or 0
        
        return {
            'current_streak': current_streak,
            'longest_streak': longest_streak,
            'streak_percentage': min((current_streak / 30) * 100, 100) if current_streak else 0
        }
    
    @classmethod
    def _get_skill_level_from_xp(cls, xp_points: int) -> str:
        """Get skill level based on XP points"""
        for level, threshold in reversed(list(cls.SKILL_LEVELS.items())):
            if xp_points >= threshold:
                return level
        return 'Beginner'
    
    @classmethod
    def _get_skill_level_from_xp_query(cls, cur, user_id: int, additional_xp: int) -> str:
        """Get skill level from database query"""
        cur.execute("""
            SELECT total_xp_points FROM user_stats_realtime WHERE user_id = %s
        """, [user_id])
        
        result = cur.fetchone()
        current_xp = (result['total_xp_points'] if result else 0) + additional_xp
        
        return cls._get_skill_level_from_xp(current_xp)
    
    @classmethod
    def _format_time_ago(cls, timestamp: datetime) -> str:
        """Format timestamp as 'time ago' string"""
        now = datetime.now()
        diff = now - timestamp
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "Just now"