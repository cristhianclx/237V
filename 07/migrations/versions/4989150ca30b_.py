"""empty message

Revision ID: 4989150ca30b
Revises: 8ff6452beaff
Create Date: 2024-03-18 20:22:23.986654

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4989150ca30b'
down_revision = '8ff6452beaff'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('content')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('content', sa.TEXT(), nullable=True))

    # ### end Alembic commands ###