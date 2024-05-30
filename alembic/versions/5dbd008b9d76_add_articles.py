"""add articles

Revision ID: 5dbd008b9d76
Revises: f34ad38175f2
Create Date: 2024-05-28 19:27:50.527588

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import String, Integer, DateTime, Date
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '5dbd008b9d76'
down_revision = 'f34ad38175f2'
branch_labels = None
depends_on = None


def upgrade() -> None:
        # создаем временную таблицу для добавления данных
    articles_table = table('articles',
        column('id', Integer),
        column('title', String),
        column('content', String),
        column('author_id', Integer),
        column('published_date', Date)
    )

    op.bulk_insert(articles_table,
        [
            {'id':1, 'title':'Article 1', 'content':'Content 1', 'author_id':1, 'published_date': '2024-01-01'},
            {'id':2, 'title':'Article 2', 'content':'Content 2', 'author_id':2, 'published_date':'2024-01-02'},
            {'id':3, 'title':'Article 3', 'content':'Content 3', 'author_id':3, 'published_date':'2024-01-04'},
        ]
    )

    op.execute("SELECT setval('articles_id_seq', 4);")


def downgrade() -> None:
    pass
