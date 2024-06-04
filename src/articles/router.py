from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from articles.pydantic_models import Article_api, ArticleBase, User_api
from db.db_models import Article
from auth.auth import get_current_user
from db.db import DatabaseManager
from fastapi import Query
from datetime import date

router = APIRouter(
    prefix="/articles",
    tags=["articles"]
)

@router.get("/{article_id}", response_model=Article_api)
async def read_article(article_id: int,
                        db_manager: DatabaseManager = Depends(DatabaseManager)):
    article = await db_manager.get_article_by_id(article_id)
    await db_manager.close()
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return article

@router.post("/", response_model=Article_api)
async def create_article(
    article: ArticleBase, 
    current_user: User_api = Depends(get_current_user),
    db_manager: DatabaseManager = Depends(DatabaseManager)
    ):
    new_article = Article(
        title=article.title, 
        content=article.content,
        author_id=current_user['id'], 
        published_date=article.published_date
    )
    await db_manager.add_article(new_article)
    await db_manager.close()
    return new_article

@router.put("/{article_id}", response_model=Article_api)
async def update_article(article_id: int, article: ArticleBase,
                          current_user: User_api = Depends(get_current_user),
                          db_manager: DatabaseManager = Depends(DatabaseManager)
                          ): 
    updated_article = await db_manager.update_article(article_id, article)
    if updated_article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    user_id = current_user['id']
    author_id = await db_manager.get_user_id_by_article_id(article_id)
    await db_manager.close()
    if current_user['role'] != 'admin' and user_id != author_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return updated_article

@router.delete("/{article_id}", response_model=Article_api)
async def delete_article(article_id: int,
                        current_user: User_api = Depends(get_current_user),
                        db_manager: DatabaseManager = Depends(DatabaseManager)):
    
    user_id = current_user['id']
    author_id = await db_manager.get_user_id_by_article_id(article_id)
    if current_user['role'] != 'admin' and user_id != author_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    deleted_article = await db_manager.delete_article(article_id)
    await db_manager.close()
    if deleted_article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return deleted_article

@router.get("/", response_model=List[Article_api])
async def read_articles(page: int = Query(1, ge=1),
                        per_page: int = Query(10, ge=1, le=200),
                        author_id: Optional[int] = None,
                        date_form: Optional[date] = None,
                        db_manager: DatabaseManager = Depends(DatabaseManager)):

    articles = await db_manager.get_articles(page, per_page, author_id, date_form)
    await db_manager.close()
    return articles