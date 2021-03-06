"""empty message

Revision ID: 0bf76680e66e
Revises: 1bde1035444e
Create Date: 2017-08-10 12:30:17.668578

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0bf76680e66e'
down_revision = '1bde1035444e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('repository_link',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('owner', sa.String(), nullable=True),
    sa.Column('repository', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('repository_link')
    # ### end Alembic commands ###
