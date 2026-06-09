"""Add patients and clinical_pages tables

Revision ID: business_002
Revises: initial_001
Create Date: 2026-06-09 12:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = 'business_002'
down_revision = 'initial_001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── patients ──────────────────────────────────────────────────────────────
    op.create_table(
        'patients',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('centre_code', sa.String(length=20), nullable=False),
        sa.Column('hospital_no', sa.String(length=50), nullable=False),
        sa.Column('reg_date', sa.Date(), nullable=True),
        sa.Column('patient_name', sa.String(length=255), nullable=False),
        sa.Column('address', sa.String(length=500), nullable=True),
        sa.Column('age', sa.Integer(), nullable=True),
        sa.Column('gender', sa.String(length=10), nullable=True),
        sa.Column('mobile', sa.String(length=20), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.String(length=36), nullable=True),
        sa.Column('updated_by', sa.String(length=36), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('centre_code', 'hospital_no', name='uq_centre_hospital'),
    )
    op.create_index('ix_patients_centre_code', 'patients', ['centre_code'], unique=False)
    op.create_index('ix_patients_hospital_no', 'patients', ['hospital_no'], unique=False)
    op.create_index('ix_patients_mobile', 'patients', ['mobile'], unique=False)
    op.create_index('ix_patients_patient_name', 'patients', ['patient_name'], unique=False)
    op.create_index('ix_patients_reg_date', 'patients', ['reg_date'], unique=False)
    op.create_index('ix_centre_hospital', 'patients', ['centre_code', 'hospital_no'], unique=False)

    # ── clinical_pages ────────────────────────────────────────────────────────
    op.create_table(
        'clinical_pages',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('centre_code', sa.String(length=20), nullable=False),
        sa.Column('hospital_no', sa.String(length=50), nullable=False),
        sa.Column('page_no', sa.Integer(), nullable=False),
        sa.Column('page_data', sa.JSON(), nullable=True),
        sa.Column('created_by', sa.String(length=36), nullable=True),
        sa.Column('updated_by', sa.String(length=36), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('centre_code', 'hospital_no', 'page_no', name='uq_centre_hospital_page'),
    )
    op.create_index('ix_clinical_pages_centre_code', 'clinical_pages', ['centre_code'], unique=False)
    op.create_index('ix_clinical_pages_hospital_no', 'clinical_pages', ['hospital_no'], unique=False)
    op.create_index('ix_clinical_pages_page_no', 'clinical_pages', ['page_no'], unique=False)
    op.create_index('ix_centre_hospital_page', 'clinical_pages', ['centre_code', 'hospital_no'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_centre_hospital_page', table_name='clinical_pages')
    op.drop_index('ix_clinical_pages_page_no', table_name='clinical_pages')
    op.drop_index('ix_clinical_pages_hospital_no', table_name='clinical_pages')
    op.drop_index('ix_clinical_pages_centre_code', table_name='clinical_pages')
    op.drop_table('clinical_pages')

    op.drop_index('ix_centre_hospital', table_name='patients')
    op.drop_index('ix_patients_reg_date', table_name='patients')
    op.drop_index('ix_patients_patient_name', table_name='patients')
    op.drop_index('ix_patients_mobile', table_name='patients')
    op.drop_index('ix_patients_hospital_no', table_name='patients')
    op.drop_index('ix_patients_centre_code', table_name='patients')
    op.drop_table('patients')
