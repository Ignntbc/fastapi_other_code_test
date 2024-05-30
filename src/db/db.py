import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from typing import Dict
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from models.db_models import User, Article
from models.pydantic_models import User_api, Article_api
from typing import Optional
from aiocache import cached, Cache, SimpleMemoryCache
from aiocache.serializers import PickleSerializer

cache = Cache(Cache.REDIS, endpoint="localhost", port=6379, serializer=PickleSerializer())

def articles_key_builder(function, self, *args):
    page = args[0] if len(args) > 0 else 'none'
    per_page = args[1] if len(args) > 1 else 'none'
    author_id = args[2] if len(args) > 2 else 'none'
    date = args[3] if len(args) > 3 else 'none'
    return f"get_articles:{page}:{per_page}:{author_id}:{date}"

# engine = create_async_engine('postgresql+asyncpg://maintainer:postgres@185.233.186.104:6101/postgres')
# Base.metadata.create_all(bind=engine)

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# def hash_password(password: str):
#     return pwd_context.hash(password)


class DatabaseManager:
    def __init__(self):
        connection_string = 'postgresql+asyncpg://maintainer:postgres@185.233.186.104:6101/postgres'
        self.engine = create_async_engine(connection_string, pool_size=250)
        self.async_session_maker = sessionmaker(self.engine, expire_on_commit=False, class_=AsyncSession)

    async def select_user(self) -> list:
        """ Получение пользователя из базы данных """
        async with self.async_session_maker() as session:
            result = await session.execute(select(User))
            users = [row.to_dict() for row in result.scalars()]
            for user in users:
                print(user['id'])
        return users
    
    async def add_user(self, user: User):
        """ Добавление пользователя в базу данных """
        async with self.async_session_maker() as session:
            session.add(user)
            await session.commit()

    async def add_article(self, article: Article):
        """ Добавление статьи в базу данных """
        async with self.async_session_maker() as session:
            session.add(article)
            await session.commit()

    async def get_users_dict(self) -> list:
        """ Получение всех пользователей из базы данных в формате словаря """
        async with self.async_session_maker() as session:
            result = await session.execute(select(User))
            users = result.scalars().all()
            users_dict = [user.to_dict() for user in users]
            return users_dict

    # async def get_articles(self, author_id: Optional[int] = None, date: Optional[str] = None) -> list:
    #     """ Получение статей из базы данных """
    #     async with self.async_session_maker() as session:
    #         query = select(Article)
    #         if author_id is not None:
    #             query = query.where(Article.author_id == author_id)
    #         if date is not None:
    #             query = query.where(Article.published_date == date)
    #         result = await session.execute(query)
    #         articles = [article.to_dict() for article in result.scalars()]
    #         return articles
    @cached(ttl=10, cache=SimpleMemoryCache, key_builder=articles_key_builder)
    async def get_articles(self, page: int = 1, per_page: int = 10, author_id: Optional[int] = None, date: Optional[str] = None) -> list:
        """ Получение статей из базы данных """
        async with self.async_session_maker() as session:
            query = select(Article)
            if author_id is not None:
                query = query.where(Article.author_id == author_id)
            if date is not None:
                query = query.where(Article.published_date == date)
            query = query.offset((page - 1) * per_page).limit(per_page)

            result = await session.execute(query)
            articles = [article.to_dict() for article in result.scalars()]
            return articles

    async def get_user_by_username(self, username: str) -> dict:
        """ Получение пользователя из базы данных по имени пользователя """
        async with self.async_session_maker() as session:
            result = await session.execute(select(User).where(User.name == username))
            user = result.scalars().first()
            if user is not None:
                return user.to_dict()
            
    async def get_article_by_id(self, article_id: int) -> dict:
        """ Получение статьи из базы данных по ID """
        async with self.async_session_maker() as session:
            result = await session.execute(select(Article).where(Article.id == article_id))
            article = result.scalars().first()
            if article is not None:
                return article.to_dict()
            
    async def update_article(self, article_id: int, article: Article) -> dict:
        """ Обновление статьи в базе данных """
        async with self.async_session_maker() as session:
            result = await session.execute(select(Article).where(Article.id == article_id))
            db_article = result.scalars().first()
            if db_article is not None:
                db_article.title = article.title
                db_article.content = article.content
                db_article.published_date = article.published_date
                await session.commit()
                return db_article.to_dict()
            
    async def delete_article(self, article_id: int) -> dict:
        """ Удаление статьи из базы данных """
        async with self.async_session_maker() as session:
            result = await session.execute(select(Article).where(Article.id == article_id))
            db_article = result.scalars().first()
            if db_article is not None:
                session.delete(db_article)
                await session.commit()
                return db_article.to_dict()
    
    async def close(self):
        """ Закрытие соединения с базой данных """
        await self.engine.dispose()




async def main():
    db = DatabaseManager()
    new_article = Article_api(id=3, title="4 Article", content="This is the content of the fourth article.", author_id=1, published_date="2022-01-05")
    await db.add_article(new_article)# Работает дописать проверку на дату ( убрать datetime оставить date)
    # users = await db.get_users_dict()
    # print(users)
    # articles = await db.get_articles_dict()
    # print(articles)
    # await db.select_user()
    # for user in fake_db.values():
    #     await db.add_user(user)
    # for article in articles.values():
    #     await db.add_article(article)


# asyncio.run(main())




