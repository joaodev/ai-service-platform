import os
import sys
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.security import hash_password
from app.database.session import SessionLocal
from app.models.role import Role
from app.models.user import User


def main() -> None:
    load_dotenv(".env")

    admin_name = os.getenv("ADMIN_NAME", "Platform Admin")
    admin_email = os.getenv("ADMIN_EMAIL", "admin@platform.local")
    admin_password = os.getenv("ADMIN_PASSWORD", "Admin@123")

    db = SessionLocal()
    try:
        role = db.query(Role).filter(Role.name == "ADMIN").first()
        if not role:
            role = Role(name="ADMIN")
            db.add(role)
            db.commit()
            db.refresh(role)

        existing_user = db.query(User).filter(User.email == admin_email).first()
        if existing_user:
            print(f"Admin user already exists: {admin_email}")
            return

        user = User(
            name=admin_name,
            email=admin_email,
            password_hash=hash_password(admin_password),
            role_id=role.id,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        print("Admin user created successfully")
        print(f"email: {user.email}")
        print(f"password: {admin_password}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
