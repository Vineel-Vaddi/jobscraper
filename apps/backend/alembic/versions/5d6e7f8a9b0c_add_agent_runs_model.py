"""Add agent runs model

Revision ID: 5d6e7f8a9b0c
Revises: 4c5d6e7f8a9b
Create Date: 2026-04-06 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5d6e7f8a9b0c'
down_revision = '4c5d6e7f8a9b'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('agent_runs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('run_type', sa.String(), nullable=True),
        sa.Column('target_entity_type', sa.String(), nullable=True),
        sa.Column('target_entity_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('duration_ms', sa.Integer(), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=True),
        sa.Column('error_code', sa.String(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('metadata_json', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_agent_runs_id'), 'agent_runs', ['id'], unique=False)
    op.create_index(op.f('ix_agent_runs_user_id'), 'agent_runs', ['user_id'], unique=False)
    op.create_index(op.f('ix_agent_runs_run_type'), 'agent_runs', ['run_type'], unique=False)
    op.create_index(op.f('ix_agent_runs_status'), 'agent_runs', ['status'], unique=False)
    op.create_index(op.f('ix_agent_runs_target_entity_type'), 'agent_runs', ['target_entity_type'], unique=False)
    op.create_index(op.f('ix_agent_runs_target_entity_id'), 'agent_runs', ['target_entity_id'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_agent_runs_target_entity_id'), table_name='agent_runs')
    op.drop_index(op.f('ix_agent_runs_target_entity_type'), table_name='agent_runs')
    op.drop_index(op.f('ix_agent_runs_status'), table_name='agent_runs')
    op.drop_index(op.f('ix_agent_runs_run_type'), table_name='agent_runs')
    op.drop_index(op.f('ix_agent_runs_user_id'), table_name='agent_runs')
    op.drop_index(op.f('ix_agent_runs_id'), table_name='agent_runs')
    op.drop_table('agent_runs')
