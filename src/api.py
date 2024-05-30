from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from fastapi import FastAPI, Depends, HTTPException, status
from typing import Optional, List, Dict
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from models.pydantic_models import User_api, Article_api, Token, TokenData, ArticleBase
from models.db_models import User, Article
from db.db import DatabaseManager 
#pip install -U email-validator
# секретный ключ для создания и проверки JWT токенов





SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


app = FastAPI()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

    

async def authenticate_user( username: str, password: str):
    db_manager = DatabaseManager()
    users_dict = await db_manager.get_users_dict()
    await db_manager.close()
    user = next((user for user in users_dict if user['name'] == username), None)
    if not user:
        return False
    if not verify_password(password, user['hashed_password']):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: TokenData):
    user_in_db = await authenticate_user(form_data.username, form_data.password)
    if not user_in_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": form_data.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

async def get_current_user(token: str = Depends(oauth2_scheme)):
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


@app.get("/articles/{article_id}", response_model=Article_api)
async def read_article(article_id: int):
    db_manager = DatabaseManager()
    article = await db_manager.get_article_by_id(article_id)
    await db_manager.close()
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@app.post("/articles/", response_model=Article_api)
async def create_article(article: ArticleBase, current_user: User_api = Depends(get_current_user)):
    new_article = Article(title=article.title, content=article.content,
                        author_id=current_user['id'], published_date=article.published_date)
    db_manager = DatabaseManager()
    await db_manager.add_article(new_article)
    await db_manager.close()
    return new_article

@app.put("/articles/{article_id}", response_model=Article_api)
async def update_article(article_id: int, article: ArticleBase, current_user: User_api = Depends(get_current_user)):
    db_manager = DatabaseManager()
    updated_article = await db_manager.update_article(article_id, article)
    await db_manager.close()
    if updated_article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return updated_article

@app.delete("/articles/{article_id}", response_model=Article_api)
async def delete_article(article_id: int, current_user: User_api = Depends(get_current_user)):
    db_manager = DatabaseManager()
    deleted_article = await db_manager.delete_article(article_id)
    await db_manager.close()
    if deleted_article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return deleted_article

# @app.get("/articles/", response_model=List[Article_api])
# async def read_articles(author_id: Optional[int] = None, date: Optional[str] = None):
#     return await db_manager.get_articles(author_id, date)

@app.get("/articles/", response_model=List[Article_api])
async def read_articles(page: int = 1, per_page: int = 10, author_id: Optional[int] = None, date: Optional[str] = None):
    db_manager = DatabaseManager()
    await db_manager.close()
    return await db_manager.get_articles(page, per_page, author_id, date)
    