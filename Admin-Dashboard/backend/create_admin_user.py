#!/usr/bin/env python3
"""
Script to create default admin user for the Smart Parking Admin Dashboard
"""
import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models.user_model import UserCreate
from app.services.user_service import user_service

async def create_default_admin():
    """Create default admin user"""
    try:
        # Check if admin user already exists
        existing_admin = await user_service.get_user_by_username("admin")
        if existing_admin:
            print("Admin user already exists!")
            print(f"Username: {existing_admin.username}")
            print(f"Email: {existing_admin.email}")
            return
        
        # Create admin user
        admin_data = UserCreate(
            username="admin",
            email="admin@smartparking.com",
            full_name="System Administrator",
            password="admin123",  # Change this in production!
            is_active=True
        )
        
        admin_user = await user_service.create_user(admin_data)
        print("Default admin user created successfully!")
        print(f"Username: {admin_user.username}")
        print(f"Email: {admin_user.email}")
        print(f"Password: admin123")
        print("\n⚠️  IMPORTANT: Please change the default password after first login!")
        
    except Exception as e:
        print(f"Error creating admin user: {e}")

if __name__ == "__main__":
    asyncio.run(create_default_admin())
