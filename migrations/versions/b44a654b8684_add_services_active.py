"""add services.active

Revision ID: b44a654b8684
Revises: 68de657b0e4d
Create Date: 2026-11-08 03:46:34.335351

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b44a654b8684'
down_revision = '68de657b0e4d'
branch_labels = None
depends_on = None


def upgrade():
    # The column already existed as is_active, so rename it to keep its data
    with op.batch_alter_table('services', schema=None) as batch_op:
        batch_op.alter_column('is_active', new_column_name='active')


def downgrade():
    with op.batch_alter_table('services', schema=None) as batch_op:
        batch_op.alter_column('active', new_column_name='is_active')