"""add topic_id to test_questions

Revision ID: 0c2728a187d5
Revises: d7014212cbd2
Create Date: 2026-04-15 13:39:29.702239

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0c2728a187d5'
down_revision = 'd7014212cbd2'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('test_questions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('topic_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'topics', ['topic_id'], ['id'])


def downgrade():
    with op.batch_alter_table('test_questions', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('topic_id')
