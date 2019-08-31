"""empty message

Revision ID: 2192cb37379b
Revises: 7715619cc976
Create Date: 2019-08-30 17:25:07.799929

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2192cb37379b'
down_revision = '7715619cc976'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('article_type', sa.Column('cname', sa.String(length=50), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('article_type', 'cname')
    # ### end Alembic commands ###