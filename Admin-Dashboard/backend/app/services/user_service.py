from typing import Optional, List
from datetime import datetime
from app.db.firestore import firestore_db
from app.models.user_model import UserCreate, UserInDB, User
from app.core.auth import get_password_hash, verify_password
import uuid

class UserService:
    def __init__(self):
        self.db = firestore_db.db
        self.collection = self.db.collection("users")

    async def create_user(self, user_data: UserCreate) -> UserInDB:
        """Create a new user"""
        # Check if username already exists
        existing_user = await self.get_user_by_username(user_data.username)
        if existing_user:
            raise ValueError("Username already exists")
        
        # Check if email already exists
        existing_email = await self.get_user_by_email(user_data.email)
        if existing_email:
            raise ValueError("Email already exists")
        
        # Create user document
        user_id = str(uuid.uuid4())
        current_time = datetime.utcnow()
        
        user_doc = {
            "user_id": user_id,
            "username": user_data.username,
            "email": user_data.email,
            "full_name": user_data.full_name,
            "hashed_password": get_password_hash(user_data.password),
            "is_active": user_data.is_active,
            "created_at": current_time,
            "updated_at": current_time
        }
        
        # Save to Firestore
        self.collection.document(user_id).set(user_doc)
        
        return UserInDB(**user_doc)

    async def get_user_by_username(self, username: str) -> Optional[UserInDB]:
        """Get user by username"""
        try:
            query = self.collection.where("username", "==", username).limit(1)
            docs = query.stream()
            
            for doc in docs:
                user_data = doc.to_dict()
                return UserInDB(**user_data)
            
            return None
        except Exception as e:
            print(f"Error getting user by username: {e}")
            return None

    async def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        """Get user by email"""
        try:
            query = self.collection.where("email", "==", email).limit(1)
            docs = query.stream()
            
            for doc in docs:
                user_data = doc.to_dict()
                return UserInDB(**user_data)
            
            return None
        except Exception as e:
            print(f"Error getting user by email: {e}")
            return None

    async def get_user_by_id(self, user_id: str) -> Optional[UserInDB]:
        """Get user by ID"""
        try:
            doc = self.collection.document(user_id).get()
            if doc.exists:
                user_data = doc.to_dict()
                return UserInDB(**user_data)
            return None
        except Exception as e:
            print(f"Error getting user by ID: {e}")
            return None

    async def authenticate_user(self, username: str, password: str) -> Optional[UserInDB]:
        """Authenticate user with username and password"""
        user = await self.get_user_by_username(username)
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        if not user.is_active:
            return None
        
        return user

    async def update_user(self, user_id: str, **kwargs) -> Optional[UserInDB]:
        """Update user data"""
        try:
            # Get current user
            current_user = await self.get_user_by_id(user_id)
            if not current_user:
                return None
            
            # Prepare update data
            update_data = {k: v for k, v in kwargs.items() if v is not None}
            update_data["updated_at"] = datetime.utcnow()
            
            # Hash password if provided
            if "password" in update_data:
                update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
            
            # Update in Firestore
            self.collection.document(user_id).update(update_data)
            
            # Return updated user
            return await self.get_user_by_id(user_id)
        except Exception as e:
            print(f"Error updating user: {e}")
            return None

    async def delete_user(self, user_id: str) -> bool:
        """Delete user (soft delete by setting is_active to False)"""
        try:
            update_data = {
                "is_active": False,
                "updated_at": datetime.utcnow()
            }
            self.collection.document(user_id).update(update_data)
            return True
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False

    async def list_users(self, limit: int = 100, offset: int = 0) -> List[User]:
        """List all active users"""
        try:
            query = self.collection.where("is_active", "==", True).limit(limit).offset(offset)
            docs = query.stream()
            
            users = []
            for doc in docs:
                user_data = doc.to_dict()
                # Convert to User model (without sensitive data)
                user = User(
                    user_id=user_data["user_id"],
                    username=user_data["username"],
                    email=user_data["email"],
                    full_name=user_data.get("full_name"),
                    is_active=user_data["is_active"],
                    created_at=user_data["created_at"],
                    updated_at=user_data["updated_at"]
                )
                users.append(user)
            
            return users
        except Exception as e:
            print(f"Error listing users: {e}")
            return []

# Create a global instance
user_service = UserService()
