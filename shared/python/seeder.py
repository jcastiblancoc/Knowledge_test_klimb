import uuid
from models import User
from connection import session
from helpers import get_pwd_context


pwd_context = get_pwd_context()


def run_seeder():
    seeder_admin_user()


def seeder_admin_user():
    user = session.query(User).where(User.role == "Admin").first()

    first_name = "Admin"
    last_name = "Admin"
    full_name = f"{first_name} {last_name}"
    
    if not user:
        admin_user = User(
            id = str(uuid.uuid4()),
            first_name = first_name,
            last_name = last_name,
            full_name = full_name,
            nickname = "Admin",
            email = "admin@admin.com",
            phone = "0000000000",
            password = pwd_context.hash("admin"),
            role = "Admin",
            country = "Colombia",
            state = "Risaralda",
            city = "Pereira"
        )
        session.add(admin_user)
        session.commit()


if __name__ == '__main__':
    run_seeder()