"""empty message

Revision ID: 9f6f81064662
Revises: dd9002dc3648
Create Date: 2017-08-10 16:14:34.765071

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9f6f81064662'
down_revision = 'dd9002dc3648'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('recipe_variable',
    sa.Column('recipe_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=155), nullable=False),
    sa.Column('value', sa.String(length=155), nullable=True),
    sa.ForeignKeyConstraint(['recipe_id'], ['recipe.id'], ),
    sa.PrimaryKeyConstraint('recipe_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('recipe_variable')
    # ### end Alembic commands ###
