"""init tables

Revision ID: 1c7635662047
Revises: 
Create Date: 2023-11-05 17:36:56.117875

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1c7635662047'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('User',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('password', sa.String(), nullable=True),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('picture', sa.String(), nullable=True),
    sa.Column('is_provider', sa.Boolean(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('token1', sa.String(), nullable=True),
    sa.Column('token2', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('Stadium',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('address', sa.String(), nullable=True),
    sa.Column('picture', sa.String(), nullable=True),
    sa.Column('area', sa.Float(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('created_user', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['created_user'], ['User.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('StadiumAvailableTime',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('stadium_id', sa.Integer(), nullable=False),
    sa.Column('weekday', sa.Integer(), nullable=False),
    sa.Column('start_time', sa.Integer(), nullable=False),
    sa.Column('end_time', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['stadium_id'], ['Stadium.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('StadiumCourt',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('stadium_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('max_number_of_people', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['stadium_id'], ['Stadium.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Order',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('stadium_court_id', sa.Integer(), nullable=False),
    sa.Column('renter_id', sa.Integer(), nullable=True),
    sa.Column('datetime', sa.DateTime(timezone=True), nullable=True),
    sa.Column('start_time', sa.Integer(), nullable=False),
    sa.Column('end_time', sa.Integer(), nullable=False),
    sa.Column('status', sa.Integer(), nullable=False),
    sa.Column('is_matching', sa.Boolean(), nullable=False),
    sa.Column('created_time', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['renter_id'], ['User.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['stadium_court_id'], ['StadiumCourt.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('StadiumCourtDisable',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('stadium_court_id', sa.Integer(), nullable=False),
    sa.Column('datetime', sa.DateTime(timezone=True), nullable=True),
    sa.Column('start_time', sa.Integer(), nullable=False),
    sa.Column('end_time', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['stadium_court_id'], ['StadiumCourt.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Team',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('order_id', sa.Integer(), nullable=False),
    sa.Column('max_number_of_member', sa.Integer(), nullable=False),
    sa.Column('orig_member_number', sa.Integer(), nullable=False),
    sa.Column('level_requirement', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['order_id'], ['Order.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('TeamMember',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('team_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['team_id'], ['Team.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['User.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('TeamMember')
    op.drop_table('Team')
    op.drop_table('StadiumCourtDisable')
    op.drop_table('Order')
    op.drop_table('StadiumCourt')
    op.drop_table('StadiumAvailableTime')
    op.drop_table('Stadium')
    op.drop_table('User')
    # ### end Alembic commands ###
