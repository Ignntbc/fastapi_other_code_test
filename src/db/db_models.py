from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv
from config import TABLENAME_U, TABLENAME_A, FOREIGN_KEY_U

load_dotenv()

Base = declarative_base()


class User(Base):
    __tablename__ = TABLENAME_U

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String, default='user')
    
    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "is_active": self.is_active,
            "role": self.role,
            "hashed_password": self.hashed_password,
        }
    

class Article(Base):
    __tablename__ = TABLENAME_A

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(String)
    published_date = Column(Date)
    author_id = Column(Integer, ForeignKey(FOREIGN_KEY_U))

    author = relationship("User", back_populates=TABLENAME_A)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "published_date": self.published_date,
            "author_id": self.author_id,
        }

    User.articles = relationship("Article", back_populates="author")
