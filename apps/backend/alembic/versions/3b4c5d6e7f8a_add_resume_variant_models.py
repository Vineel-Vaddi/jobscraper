"""Add resume variant models

Revision ID: 3b4c5d6e7f8a
Revises: 2a3b4c5d6e7f
Create Date: 2026-04-06 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3b4c5d6e7f8a'
down_revision = '2a3b4c5d6e7f'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('resume_variants',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('profile_id', sa.Integer(), nullable=True),
        sa.Column('job_id', sa.Integer(), nullable=True),
        sa.Column('base_document_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('jd_summary_json', sa.Text(), nullable=True),
        sa.Column('keyword_alignment_json', sa.Text(), nullable=True),
        sa.Column('skill_gap_json', sa.Text(), nullable=True),
        sa.Column('tailored_resume_json', sa.Text(), nullable=True),
        sa.Column('tailored_resume_text', sa.Text(), nullable=True),
        sa.Column('validator_report_json', sa.Text(), nullable=True),
        sa.Column('ats_score_json', sa.Text(), nullable=True),
        sa.Column('export_docx_storage_key', sa.String(), nullable=True),
        sa.Column('export_pdf_storage_key', sa.String(), nullable=True),
        sa.Column('error_code', sa.String(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['base_document_id'], ['documents.id'], ),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ),
        sa.ForeignKeyConstraint(['profile_id'], ['profiles.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_resume_variants_id'), 'resume_variants', ['id'], unique=False)
    op.create_index(op.f('ix_resume_variants_job_id'), 'resume_variants', ['job_id'], unique=False)
    op.create_index(op.f('ix_resume_variants_profile_id'), 'resume_variants', ['profile_id'], unique=False)
    op.create_index(op.f('ix_resume_variants_user_id'), 'resume_variants', ['user_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_resume_variants_user_id'), table_name='resume_variants')
    op.drop_index(op.f('ix_resume_variants_profile_id'), table_name='resume_variants')
    op.drop_index(op.f('ix_resume_variants_job_id'), table_name='resume_variants')
    op.drop_index(op.f('ix_resume_variants_id'), table_name='resume_variants')
    op.drop_table('resume_variants')
