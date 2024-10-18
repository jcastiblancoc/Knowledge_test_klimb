from fastapi import HTTPException, status
from models import User
from connection import session
from helpers import get_current_user


async def authenticate_user(token: str):
    """Authenticate user and return user details."""
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    user = get_current_user(token)
    return user