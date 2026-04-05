"""Add job models

Revision ID: 2a3b4c5d6e7f
Revises: 1a2b3c4d5e6f
Create Date: 2026-04-06 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2a3b4c5d6e7f'
down_revision = '1a2b3c4d5e6f'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('job_search_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('source_url', sa.String(), nullable=True),
        sa.Column('source_type', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('ingest_error_code', sa.String(), nullable=True),
        sa.Column('ingest_error_message', sa.Text(), nullable=True),
        sa.Column('raw_result_count', sa.Integer(), nullable=True),
        sa.Column('normalized_result_count', sa.Integer(), nullable=True),
        sa.Column('deduped_result_count', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_job_search_sessions_id'), 'job_search_sessions', ['id'], unique=False)
    
    op.create_table('jobs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('job_search_session_id', sa.Integer(), nullable=True),
        sa.Column('external_job_id', sa.String(), nullable=True),
        sa.Column('source_type', sa.String(), nullable=True),
        sa.Column('source_job_url', sa.String(), nullable=True),
        sa.Column('canonical_job_url', sa.String(), nullable=True),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('company', sa.String(), nullable=True),
        sa.Column('location', sa.String(), nullable=True),
        sa.Column('work_mode', sa.String(), nullable=True),
        sa.Column('employment_type', sa.String(), nullable=True),
        sa.Column('seniority', sa.String(), nullable=True),
        sa.Column('posted_at_raw', sa.String(), nullable=True),
        sa.Column('posted_at_normalized', sa.DateTime(timezone=True), nullable=True),
        sa.Column('description_text', sa.Text(), nullable=True),
        sa.Column('requirements_json', sa.Text(), nullable=True),
        sa.Column('metadata_json', sa.Text(), nullable=True),
        sa.Column('normalization_confidence', sa.String(), nullable=True),
        sa.Column('dedupe_key', sa.String(), nullable=True),
        sa.Column('fit_score', sa.Integer(), nullable=True),
        sa.Column('fit_reasons_json', sa.Text(), nullable=True),
        sa.Column('fit_gaps_json', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['job_search_session_id'], ['job_search_sessions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_jobs_id'), 'jobs', ['id'], unique=False)
    op.create_index(op.f('ix_jobs_external_job_id'), 'jobs', ['external_job_id'], unique=False)
    op.create_index(op.f('ix_jobs_dedupe_key'), 'jobs', ['dedupe_key'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_jobs_dedupe_key'), table_name='jobs')
    op.drop_index(op.f('ix_jobs_external_job_id'), table_name='jobs')
    op.drop_index(op.f('ix_jobs_id'), table_name='jobs')
    op.drop_table('jobs')
    
    op.drop_index(op.f('ix_job_search_sessions_id'), table_name='job_search_sessions')
    op.drop_table('job_search_sessions')
