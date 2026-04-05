"""Phase 7 – polish schema additions

Revision ID: 6e7f8a9b0c1d
Revises: 5d6e7f8a9b0c
Create Date: 2026-04-06 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = '6e7f8a9b0c1d'
down_revision = '5d6e7f8a9b0c'
branch_labels = None
depends_on = None


def upgrade():
    # -- extend job_search_sessions --
    op.add_column('job_search_sessions', sa.Column('is_saved', sa.Boolean(), server_default='false'))
    op.add_column('job_search_sessions', sa.Column('saved_label', sa.String(), nullable=True))
    op.add_column('job_search_sessions', sa.Column('archived_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('job_search_sessions', sa.Column('last_viewed_at', sa.DateTime(timezone=True), nullable=True))

    # -- profile_preferences --
    op.create_table('profile_preferences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('preferred_locations_json', sa.Text(), nullable=True),
        sa.Column('preferred_work_modes_json', sa.Text(), nullable=True),
        sa.Column('preferred_employment_types_json', sa.Text(), nullable=True),
        sa.Column('target_seniority', sa.String(), nullable=True),
        sa.Column('preferred_industries_json', sa.Text(), nullable=True),
        sa.Column('salary_notes', sa.String(), nullable=True),
        sa.Column('exclude_keywords_json', sa.Text(), nullable=True),
        sa.Column('resume_emphasis', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_profile_preferences_user_id', 'profile_preferences', ['user_id'], unique=True)

    # -- role_presets --
    op.create_table('role_presets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('target_titles_json', sa.Text(), nullable=True),
        sa.Column('priority_skills_json', sa.Text(), nullable=True),
        sa.Column('summary_focus', sa.String(), nullable=True),
        sa.Column('preference_overrides_json', sa.Text(), nullable=True),
        sa.Column('pinned_section_rules_json', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_role_presets_user_id', 'role_presets', ['user_id'])

    # -- resume_pins --
    op.create_table('resume_pins',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('source_type', sa.String(), nullable=True),
        sa.Column('source_ref', sa.String(), nullable=True),
        sa.Column('label', sa.String(), nullable=True),
        sa.Column('pin_mode', sa.String(), server_default='locked_if_supported'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_resume_pins_user_id', 'resume_pins', ['user_id'])
    op.create_index('ix_resume_pins_source_type', 'resume_pins', ['source_type'])


def downgrade():
    op.drop_table('resume_pins')
    op.drop_table('role_presets')
    op.drop_table('profile_preferences')
    op.drop_column('job_search_sessions', 'last_viewed_at')
    op.drop_column('job_search_sessions', 'archived_at')
    op.drop_column('job_search_sessions', 'saved_label')
    op.drop_column('job_search_sessions', 'is_saved')
