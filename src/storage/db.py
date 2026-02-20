import aiosqlite
from typing import Optional, List, Dict
from datetime import datetime
from pathlib import Path

from src.config.settings import settings


class Database:
    """Database manager for bot data storage"""
    
    def __init__(self):
        """Initialize database manager"""
        self.db_path = settings.DB_PATH
        self.conn: Optional[aiosqlite.Connection] = None
    
    async def init_db(self):
        """Initialize database and create tables"""
        # Ensure data directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Connect to database
        self.conn = await aiosqlite.connect(self.db_path)
        self.conn.row_factory = aiosqlite.Row
        
        # Create tables
        await self._create_tables()
    
    async def _create_tables(self):
        """Create database tables"""
        async with self.conn.cursor() as cursor:
            # Users table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    has_access INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # User data table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_data (
                    user_id INTEGER PRIMARY KEY,
                    weight REAL,
                    height INTEGER,
                    age INTEGER,
                    goal TEXT,
                    target_weight REAL,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)
            
            # Workout records table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS workout_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    workout_data TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)
            
            # AI requests table
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS ai_requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    question TEXT,
                    response TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)
            
            await self.conn.commit()
    
    async def close(self):
        """Close database connection"""
        if self.conn:
            await self.conn.close()
    
    # User management methods
    
    async def has_access(self, user_id: int) -> bool:
        """Check if user has access"""
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                "SELECT has_access FROM users WHERE user_id = ?",
                (user_id,)
            )
            row = await cursor.fetchone()
            
            if not row:
                # Create user record if doesn't exist
                await cursor.execute(
                    "INSERT INTO users (user_id, has_access) VALUES (?, 0)",
                    (user_id,)
                )
                await self.conn.commit()
                return False
            
            return bool(row['has_access'])
    
    async def grant_access(self, user_id: int):
        """Grant access to user"""
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                "UPDATE users SET has_access = 1 WHERE user_id = ?",
                (user_id,)
            )
            await self.conn.commit()
    
    async def revoke_access(self, user_id: int):
        """Revoke user access"""
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                "UPDATE users SET has_access = 0 WHERE user_id = ?",
                (user_id,)
            )
            await self.conn.commit()
    
    async def get_pending_users(self) -> List[Dict]:
        """Get users waiting for access"""
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                "SELECT user_id, username FROM users WHERE has_access = 0"
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def get_all_users(self) -> List[Dict]:
        """Get all users with access"""
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                "SELECT user_id, username FROM users WHERE has_access = 1"
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def get_user_info(self, user_id: int) -> Optional[Dict]:
        """Get user information"""
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                "SELECT user_id, username, has_access FROM users WHERE user_id = ?",
                (user_id,)
            )
            row = await cursor.fetchone()
            return dict(row) if row else None
    
    async def get_total_users(self) -> int:
        """Get total number of users"""
        async with self.conn.cursor() as cursor:
            await cursor.execute("SELECT COUNT(*) as count FROM users")
            row = await cursor.fetchone()
            return row['count']
    
    async def get_approved_users_count(self) -> int:
        """Get number of approved users"""
        async with self.conn.cursor() as cursor:
            await cursor.execute("SELECT COUNT(*) as count FROM users WHERE has_access = 1")
            row = await cursor.fetchone()
            return row['count']
    
    async def get_pending_users_count(self) -> int:
        """Get number of pending users"""
        async with self.conn.cursor() as cursor:
            await cursor.execute("SELECT COUNT(*) as count FROM users WHERE has_access = 0")
            row = await cursor.fetchone()
            return row['count']
    
    # User data methods
    
    async def get_user_data(self, user_id: int) -> Optional[Dict]:
        """Get user data"""
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                "SELECT * FROM user_data WHERE user_id = ?",
                (user_id,)
            )
            row = await cursor.fetchone()
            return dict(row) if row else None
    
    async def update_user_data(self, user_id: int, **kwargs):
        """Update user data"""
        async with self.conn.cursor() as cursor:
            # Check if user data exists
            await cursor.execute(
                "SELECT user_id FROM user_data WHERE user_id = ?",
                (user_id,)
            )
            exists = await cursor.fetchone()
            
            if exists:
                # Update existing record
                fields = ', '.join([f"{k} = ?" for k in kwargs.keys()])
                values = list(kwargs.values()) + [user_id]
                await cursor.execute(
                    f"UPDATE user_data SET {fields}, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?",
                    values
                )
            else:
                # Insert new record
                fields = ', '.join(['user_id'] + list(kwargs.keys()))
                placeholders = ', '.join(['?'] * (len(kwargs) + 1))
                values = [user_id] + list(kwargs.values())
                await cursor.execute(
                    f"INSERT INTO user_data ({fields}) VALUES ({placeholders})",
                    values
                )
            
            await self.conn.commit()
    
    # Workout records methods
    
    async def add_workout_record(self, user_id: int, workout_data: str):
        """Add workout record"""
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                "INSERT INTO workout_records (user_id, workout_data) VALUES (?, ?)",
                (user_id, workout_data)
            )
            await self.conn.commit()
    
    async def get_workout_records(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Get workout records"""
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                "SELECT * FROM workout_records WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
                (user_id, limit)
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    # AI requests methods
    
    async def get_ai_request_count(self, user_id: int) -> int:
        """Get AI request count for user"""
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                "SELECT COUNT(*) as count FROM ai_requests WHERE user_id = ?",
                (user_id,)
            )
            row = await cursor.fetchone()
            return row['count']
    
    async def increment_ai_request_count(self, user_id: int):
        """Increment AI request count (called after successful request)"""
        # This is handled by add_ai_request, so this method is for compatibility
        pass
    
    async def add_ai_request(self, user_id: int, question: str, response: str):
        """Add AI request record"""
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                "INSERT INTO ai_requests (user_id, question, response) VALUES (?, ?, ?)",
                (user_id, question, response)
            )
            await self.conn.commit()
    
    async def get_ai_history(self, user_id: int, limit: int = 5) -> List[Dict]:
        """Get AI request history"""
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                "SELECT question, response, created_at FROM ai_requests WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
                (user_id, limit)
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def get_total_ai_requests(self) -> int:
        """Get total number of AI requests"""
        async with self.conn.cursor() as cursor:
            await cursor.execute("SELECT COUNT(*) as count FROM ai_requests")
            row = await cursor.fetchone()
            return row['count']