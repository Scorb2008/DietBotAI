from typing import Optional, List, Dict
from src.config.settings import settings


class AccessService:
    """Service for managing user access and permissions"""
    
    def __init__(self, db):
        """Initialize access service with database instance"""
        self.db = db
    
    async def is_admin(self, user_id: int) -> bool:
        """Check if user is admin"""
        return user_id == settings.ADMIN_ID
    
    async def check_access(self, user_id: int) -> bool:
        """Check if user has access to the bot"""
        # Admin always has access
        if await self.is_admin(user_id):
            return True
        
        # Check if user has been granted access
        return await self.db.has_access(user_id)
    
    async def grant_access(self, user_id: int) -> bool:
        """Grant access to user"""
        try:
            await self.db.grant_access(user_id)
            return True
        except Exception:
            return False
    
    async def revoke_access(self, user_id: int) -> bool:
        """Revoke user access"""
        try:
            await self.db.revoke_access(user_id)
            return True
        except Exception:
            return False
    
    async def get_pending_users(self) -> List[Dict]:
        """Get list of users waiting for access"""
        return await self.db.get_pending_users()
    
    async def get_all_users(self) -> List[Dict]:
        """Get all users with access"""
        return await self.db.get_all_users()
    
    async def get_user_info(self, user_id: int) -> Optional[Dict]:
        """Get user information"""
        return await self.db.get_user_info(user_id)
    
    async def get_stats(self) -> Dict:
        """Get bot statistics"""
        total_users = await self.db.get_total_users()
        approved_users = await self.db.get_approved_users_count()
        pending_users = await self.db.get_pending_users_count()
        total_ai_requests = await self.db.get_total_ai_requests()
        
        return {
            'total_users': total_users,
            'approved_users': approved_users,
            'pending_users': pending_users,
            'total_ai_requests': total_ai_requests
        }