"""add status column for TABLE team_member

Revision ID: f53d264809ee
Revises: 0d9cd3d1f829
Create Date: 2023-11-22 15:28:35.080393

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f53d264809ee'
down_revision = '0d9cd3d1f829'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('TeamMember', sa.Column('status', sa.Integer(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('TeamMember', 'status')
    # ### end Alembic commands ###