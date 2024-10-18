
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
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context

def get_oauth2_scheme():
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
    return oauth2_scheme

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
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str):
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No token provided")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        # Aquí debes buscar al usuario en la base de datos con user_id
        user = session.query(User).where(User.email == email).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token")
    
def convert_operation_to_dict(op):
    op_dict = {}
    for key, value in op.__dict__.items():
        if isinstance(value, Decimal):
            op_dict[key] = float(value)  # Convert Decimal to float
        elif isinstance(value, date):
            op_dict[key] = value.isoformat()  # Convert date to string
        elif not key.startswith('_'):  # Exclude internal attributes like _sa_instance_state
            op_dict[key] = value


