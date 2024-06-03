"""add users

Revision ID: f34ad38175f2
Revises: 1518846f0475
Create Date: 2024-05-28 19:14:51.738858

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import String, Integer, DateTime
from datetime import datetime
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)


# revision identifiers, used by Alembic.
revision = 'f34ad38175f2'
down_revision = '1518846f0475'
branch_labels = None
depends_on = None


def upgrade() -> None:
    users_table = table('users',
        column('id', Integer),
        column('name', String),
        column('email', String),
        column('hashed_password', String),
        column('is_active', sa.Boolean),
        column('role', String)
    )
    op.bulk_insert(users_table,
        [
            {'email':'user1@example.com', 'name':'user1', 'hashed_password':hash_password('password1'), 'is_active':True, 'role':'admin'},
            {'email':'user2@example.com', 'name':'user2', 'hashed_password':hash_password('password2'), 'is_active':True, 'role':'user'},   
            {'email':'user3@example.com', 'name':'user3', 'hashed_password':hash_password('password3'), 'is_active':True, 'role':'user'}
        ]
    )

    op.execute("SELECT setval('users_id_seq', 4);")

def downgrade() -> None:
    pass
