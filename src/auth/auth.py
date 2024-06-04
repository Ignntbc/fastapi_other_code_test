from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from typing import Optional
from db.db import DatabaseManager
from config import SECRET_KEY, ALGORITHM


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str):
    """Функция для проверки пароля пользователя"""
    return pwd_context.verify(plain_password, hashed_password)

async def authenticate_user( username: str, password: str, db_manager: DatabaseManager = Depends(DatabaseManager)):
    """ Функция для аутентификации пользователя"""
    users_dict = await db_manager.get_users_dict()
    await db_manager.close()
    user = next((user for user in users_dict if user['name'] == username), None)
    if not user:
        return False
    if not verify_password(password, user['hashed_password']):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Функция для создания токена доступа"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Функция для получения текущего пользователя"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    db_manager = DatabaseManager()
    user = await db_manager.get_user_by_username(username)
    await db_manager.close()
    if user is None:
        raise credentials_exception
    return user