from connection import session
from models import User

users = session.query(User).all()
print(users)