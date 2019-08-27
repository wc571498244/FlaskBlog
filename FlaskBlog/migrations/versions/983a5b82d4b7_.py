"""empty message

Revision ID: 983a5b82d4b7
Revises: 
Create Date: 2019-08-27 09:04:43.739532

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '983a5b82d4b7'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('article_type',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tag',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('article',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('title', sa.String(length=100), nullable=True),
    sa.Column('content', sa.Text(), nullable=True),
    sa.Column('create_time', sa.DateTime(), nullable=True),
    sa.Column('click_num', sa.Integer(), nullable=True),
    sa.Column('description', sa.String(length=200), nullable=True),
    sa.Column('img', sa.String(length=255), nullable=True),
    sa.Column('article_type', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['article_type'], ['article_type.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('article_tags',
    sa.Column('article_id', sa.Integer(), nullable=False),
    sa.Column('tag_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['article_id'], ['article.id'], ),
    sa.ForeignKeyConstraint(['tag_id'], ['tag.id'], ),
    sa.PrimaryKeyConstraint('article_id', 'tag_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('article_tags')
    op.drop_table('article')
    op.drop_table('tag')
    op.drop_table('article_type')
    # ### end Alembic commands ###