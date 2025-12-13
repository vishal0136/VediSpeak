"""
Portfolio links model
"""
from ..extensions import mysql
from ..utils.db_helpers import db_cursor

class PortfolioLink:
    @staticmethod
    def create(user_id, platform, url):
        """Create a new portfolio link"""
        cur = None
        try:
            cur = db_cursor()
            cur.execute("""
                INSERT INTO portfolio_links (user_id, platform, url)
                VALUES (%s, %s, %s)
            """, (user_id, platform, url))
            mysql.connection.commit()
            return cur.lastrowid
        finally:
            if cur:
                cur.close()
    
    @staticmethod
    def get_user_links(user_id):
        """Get all portfolio links for a user"""
        cur = None
        try:
            cur = db_cursor()
            cur.execute("""
                SELECT * FROM portfolio_links WHERE user_id = %s ORDER BY added_at DESC
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
    def delete(link_id, user_id):
        """Delete a portfolio link"""
        cur = None
        try:
            cur = db_cursor()
            cur.execute("""
                DELETE FROM portfolio_links WHERE id = %s AND user_id = %s
            """, (link_id, user_id))
            mysql.connection.commit()
        finally:
            if cur:
                cur.close()
