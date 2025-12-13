"""
User model and database operations
"""
from ..extensions import mysql
from ..utils.db_helpers import db_cursor

class User:
    @staticmethod
    def create(username, email, phone, password, oauth_provider=None, oauth_id=None):
        """Create a new user"""
        cur = None
        try:
            cur = db_cursor()
            cur.execute("""
                INSERT INTO users (username, email, phone, password, oauth_provider, oauth_id) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (username, email, phone, password, oauth_provider, oauth_id))
            mysql.connection.commit()
            return cur.lastrowid
        finally:
            if cur:
                cur.close()
    
    @staticmethod
    def get_by_email(email):
        """Get user by email"""
        cur = None
        try:
            cur = db_cursor()
            cur.execute("SELECT * FROM users WHERE email = %s", [email])
            row = cur.fetchone()
            # DictCursor already returns a dict, no need to convert
            return row
        finally:
            if cur:
                cur.close()
    
    @staticmethod
    def get_by_phone(phone):
        """Get user by phone"""
        cur = None
        try:
            cur = db_cursor()
            cur.execute("SELECT * FROM users WHERE phone = %s", [phone])
            row = cur.fetchone()
            return row
        finally:
            if cur:
                cur.close()
    
    @staticmethod
    def get_by_id(user_id):
        """Get user by ID"""
        cur = None
        try:
            cur = db_cursor()
            cur.execute("SELECT * FROM users WHERE id = %s", [user_id])
            row = cur.fetchone()
            return row
        finally:
            if cur:
                cur.close()
    
    @staticmethod
    def get_by_oauth(provider, oauth_id):
        """Get user by OAuth provider and ID"""
        cur = None
        try:
            cur = db_cursor()
            cur.execute("""
                SELECT * FROM users WHERE oauth_provider = %s AND oauth_id = %s
            """, (provider, oauth_id))
            row = cur.fetchone()
            return row
        finally:
            if cur:
                cur.close()
    
    @staticmethod
    def update_otp(user_id, otp_code, otp_expiry):
        """Update OTP for user"""
        cur = None
        try:
            cur = db_cursor()
            cur.execute("""
                UPDATE users SET otp_code = %s, otp_expiry = %s WHERE id = %s
            """, (otp_code, otp_expiry, user_id))
            mysql.connection.commit()
        finally:
            if cur:
                cur.close()
    
    @staticmethod
    def update_profile(user_id, username=None, profession=None, bio=None, 
                      profile_photo=None, resume_path=None):
        """Update user profile"""
        cur = None
        try:
            cur = db_cursor()
            updates = []
            values = []
            
            if username:
                updates.append("username = %s")
                values.append(username)
            if profession is not None:
                updates.append("profession = %s")
                values.append(profession)
            if bio is not None:
                updates.append("bio = %s")
                values.append(bio)
            if profile_photo:
                updates.append("profile_photo = %s")
                values.append(profile_photo)
            if resume_path:
                updates.append("resume_path = %s")
                values.append(resume_path)
            
            if updates:
                values.append(user_id)
                query = f"UPDATE users SET {', '.join(updates)} WHERE id = %s"
                cur.execute(query, values)
                mysql.connection.commit()
        finally:
            if cur:
                cur.close()
