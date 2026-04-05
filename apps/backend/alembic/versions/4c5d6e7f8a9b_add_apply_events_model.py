"""Add apply event model

Revision ID: 4c5d6e7f8a9b
Revises: 3b4c5d6e7f8a
Create Date: 2026-04-06 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4c5d6e7f8a9b'
down_revision = '3b4c5d6e7f8a'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('apply_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('job_id', sa.Integer(), nullable=True),
        sa.Column('resume_variant_id', sa.Integer(), nullable=True),
        sa.Column('event_type', sa.String(), nullable=True),
        sa.Column('target_url', sa.String(), nullable=True),
        sa.Column('metadata_json', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ),
        sa.ForeignKeyConstraint(['resume_variant_id'], ['resume_variants.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_apply_events_id'), 'apply_events', ['id'], unique=False)
    op.create_index(op.f('ix_apply_events_job_id'), 'apply_events', ['job_id'], unique=False)
    op.create_index(op.f('ix_apply_events_resume_variant_id'), 'apply_events', ['resume_variant_id'], unique=False)
    op.create_index(op.f('ix_apply_events_user_id'), 'apply_events', ['user_id'], unique=False)
    op.create_index(op.f('ix_apply_events_event_type'), 'apply_events', ['event_type'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_apply_events_event_type'), table_name='apply_events')
    op.drop_index(op.f('ix_apply_events_user_id'), table_name='apply_events')
    op.drop_index(op.f('ix_apply_events_resume_variant_id'), table_name='apply_events')
    op.drop_index(op.f('ix_apply_events_job_id'), table_name='apply_events')
    op.drop_index(op.f('ix_apply_events_id'), table_name='apply_events')
    op.drop_table('apply_events')
