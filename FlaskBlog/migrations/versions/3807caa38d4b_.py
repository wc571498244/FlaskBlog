"""empty message

Revision ID: 3807caa38d4b
Revises: 7b789e87d05b
Create Date: 2019-08-31 14:56:24.005713

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '3807caa38d4b'
down_revision = '7b789e87d05b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('login_log', 'port')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('login_log', sa.Column('port', mysql.VARCHAR(length=10), nullable=True))
    # ### end Alembic commands ###
