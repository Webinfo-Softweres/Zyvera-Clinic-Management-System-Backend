import sys
import os
from app.core.database import SessionLocal
from app.models.clinic import Clinic
from app.models.user import User
from app.core.security import hash_password
from app.utils.constants import SUPER_ADMIN, CLINIC_ACTIVE, USER_ACTIVE

def seed_super_admin():
    db = SessionLocal()
    try:
        # Create the Super Admin user without a clinic
        super_username = "superadmin"
        super_password = "SuperSecurePassword123!"
        
        existing_admin = db.query(User).filter(User.username == super_username).first()
        if not existing_admin:
            print("Creating Super Admin User...")
            super_user = User(
                centre_code=None,
                name="System Administrator",
                username=super_username,
                password_hash=hash_password(super_password),
                role=SUPER_ADMIN,
                status=USER_ACTIVE
            )
            db.add(super_user)
            db.commit()
            print(f"✅ Super Admin seeded successfully!")
            print(f"Username: {super_username}")
            print(f"Password: {super_password}")
            print("Please change this password via the API immediately after your first login.")
        else:
            print("Super Admin already exists!")
            
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_super_admin()
