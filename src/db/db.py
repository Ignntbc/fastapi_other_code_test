from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from db.db_models import User, Article
from typing import Optional
from aiocache import cached, Cache, SimpleMemoryCache
from aiocache.serializers import PickleSerializer
from config import REDIS_HOST, REDIS_PORT, DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME

cache = Cache(Cache.REDIS, endpoint=REDIS_HOST, port=REDIS_PORT, serializer=PickleSerializer())

POOL_SIZE = 250


def articles_key_builder(function, self, *args):
    """Функция для кэширования статей"""
    page = args[0] if len(args) > 0 else 'none'
    per_page = args[1] if len(args) > 1 else 'none'
    author_id = args[2] if len(args) > 2 else 'none'
    date = args[3] if len(args) > 3 else 'none'
    return f"get_articles:{page}:{per_page}:{author_id}:{date}"



class DatabaseManager:
    """ Класс для работы с базой данных """
    def __init__(self, test_mode: bool = False):
        if test_mode:
            connection_string = f'postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/test_{DB_NAME}'
        else:
            connection_string = f'postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
        self.engine = create_async_engine(connection_string, pool_size=POOL_SIZE)
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

    async def get_user_id_by_article_id(self, article_id: int) -> int:
        """ Получение user_id из базы данных по ID статьи """
        async with self.async_session_maker() as session:
            result = await session.execute(select(Article).where(Article.id == article_id))
            article = result.scalars().first()
            if article is not None:
                return article.author_id


    @cached(ttl=10, cache=SimpleMemoryCache, key_builder=articles_key_builder)
    async def get_articles(self, page: int = 1, per_page: int = 10, author_id: Optional[int] = None,
                        date: Optional[str] = None) -> list:
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
