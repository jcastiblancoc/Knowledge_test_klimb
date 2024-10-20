
import os

from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
from jose import jwt
from fastapi import HTTPException, status
from connection import session
from models import User
from jose import JWTError, jwt
import logging
from fastapi import Request, HTTPException, Depends
from decimal import Decimal
from datetime import date

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
SECRET_KEY = os.getenv("SECRET_KEY")

def logger():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    return logger

logger_info = logger()

def get_pwd_context():
    return CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_oauth2_scheme():
    return OAuth2PasswordBearer(tokenUrl="token")

def get_password_hash(password: str) -> str:
    pwd_context = get_pwd_context()
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    pwd_context = get_pwd_context()
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)  # Usa timezone.utc
    to_encode["exp"] = expire
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str):
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No token provided")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        user = session.query(User).where(User.email == email).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token")


def get_user_by_email(email: str) -> User:
    return session.query(User).filter(User.email == email).first()

def get_user_by_id(user_id: str) -> User:
    return session.query(User).filter(User.id == user_id).first()


