"""
Achievements and badges model
"""
from ..extensions import mysql
from ..utils.db_helpers import db_cursor

class Achievement:
    @staticmethod
    def create(user_id, badge_title, badge_desc="", module_name="", progress=0, badge_icon="default_badge.png"):
        """Create a new achievement"""
        cur = None
        try:
            cur = db_cursor()
            cur.execute("""
                INSERT INTO achievements 
                (user_id, badge_title, badge_desc, module_name, progress, badge_icon)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (user_id, badge_title, badge_desc, module_name, progress, badge_icon))
            mysql.connection.commit()
            return cur.lastrowid
        finally:
            if cur:
                cur.close()
    
    @staticmethod
    def get_user_achievements(user_id):
        """Get all achievements for a user"""
        cur = None
        try:
            cur = db_cursor()
            cur.execute("""
                SELECT * FROM achievements WHERE user_id = %s ORDER BY earned_date DESC
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
    def mark_earned(achievement_id, user_id):
        """Mark an achievement as earned"""
        cur = None
        try:
            cur = db_cursor()
            cur.execute("""
                UPDATE achievements 
                SET earned_date = CURDATE(), progress = 100 
                WHERE id = %s AND user_id = %s
            """, (achievement_id, user_id))
            mysql.connection.commit()
        finally:
            if cur:
                cur.close()
