"""empty message

Revision ID: c47eff618921
Revises: 803e1411a032
Create Date: 2021-05-28 07:53:01.282830

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c47eff618921'
down_revision = '803e1411a032'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'past_shows_count')
    op.drop_column('Venue', 'upcoming_shows_count')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('upcoming_shows_count', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('Venue', sa.Column('past_shows_count', sa.INTEGER(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###