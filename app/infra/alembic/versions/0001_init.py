"""initial schema

Revision ID: 0001
Revises: 
Create Date: 2025-11-05 00:00:00.000000
"""
from __future__ import annotations
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table('tenants',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('slug', sa.String(), nullable=False, unique=True),
        sa.Column('locale', sa.String(), nullable=False),
        sa.Column('timezone', sa.String(), nullable=False),
        sa.Column('plan', sa.String(), nullable=False),
        sa.Column('plan_status', sa.String(), nullable=False, server_default='trial'),
        sa.Column('next_renewal', sa.TIMESTAMP(timezone=True)),
        sa.Column('trial_until', sa.TIMESTAMP(timezone=True)),
        sa.Column('stars_subscription_id', sa.String()),
        sa.Column('brand', sa.String()),
        sa.Column('logo_url', sa.String()),
    )

    op.create_table('staff',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), index=True),
        sa.Column('tg_user_id', sa.BigInteger(), index=True),
        sa.Column('role', sa.String()),
        sa.Column('name', sa.String()),
        sa.UniqueConstraint('tenant_id', 'tg_user_id', name='uq_staff_user_per_tenant'),
    )

    op.create_table('services',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), index=True),
        sa.Column('name', sa.String()),
        sa.Column('duration_min', sa.Integer()),
        sa.Column('price_stars', sa.Integer()),
        sa.UniqueConstraint('tenant_id', 'name', name='uq_service_name'),
    )

    op.create_table('schedule_rules',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), index=True),
        sa.Column('staff_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('staff.id', ondelete='CASCADE')),
        sa.Column('weekday', sa.Integer()),
        sa.Column('start_min', sa.Integer()),
        sa.Column('end_min', sa.Integer()),
        sa.Column('buffer_min', sa.Integer(), server_default='0'),
    )

    op.create_table('exceptions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), index=True),
        sa.Column('staff_id', postgresql.UUID(as_uuid=True)),
        sa.Column('date', sa.TIMESTAMP(timezone=True)),
        sa.Column('kind', sa.String()),
        sa.Column('window_start_min', sa.Integer()),
        sa.Column('window_end_min', sa.Integer()),
    )

    op.create_table('slots',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), index=True),
        sa.Column('staff_id', postgresql.UUID(as_uuid=True)),
        sa.Column('service_id', postgresql.UUID(as_uuid=True)),
        sa.Column('start_ts', sa.TIMESTAMP(timezone=True)),
        sa.Column('end_ts', sa.TIMESTAMP(timezone=True)),
        sa.Column('status', sa.String(), server_default='free'),
        sa.Column('hold_key', sa.String()),
    )
    op.create_index('ix_slots_lookup', 'slots', ['tenant_id', 'staff_id', 'start_ts'])
    op.create_unique_constraint('uq_slot_unique', 'slots', ['tenant_id', 'staff_id', 'start_ts'])

    op.create_table('clients',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), index=True),
        sa.Column('tg_user_id', sa.BigInteger(), index=True),
        sa.Column('phone', sa.String()),
        sa.Column('name', sa.String()),
        sa.Column('tags', sa.JSON()),
    )
    op.create_unique_constraint('uq_client_per_tenant', 'clients', ['tenant_id', 'tg_user_id'])

    op.create_table('appointments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), index=True),
        sa.Column('client_id', postgresql.UUID(as_uuid=True)),
        sa.Column('staff_id', postgresql.UUID(as_uuid=True)),
        sa.Column('service_id', postgresql.UUID(as_uuid=True)),
        sa.Column('start_ts', sa.TIMESTAMP(timezone=True)),
        sa.Column('end_ts', sa.TIMESTAMP(timezone=True)),
        sa.Column('status', sa.String()),
        sa.Column('origin', sa.String()),
    )
    op.create_index('ix_appt_lookup', 'appointments', ['tenant_id', 'start_ts'])

    op.create_table('templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('tenants.id', ondelete='CASCADE'), index=True),
        sa.Column('key', sa.String()),
        sa.Column('locale', sa.String()),
        sa.Column('content', sa.Text()),
    )
    op.create_unique_constraint('uq_template', 'templates', ['tenant_id', 'key', 'locale'])

    op.create_table('subscriptions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), index=True),
        sa.Column('provider', sa.String()),
        sa.Column('external_id', sa.String(), unique=True),
        sa.Column('status', sa.String()),
        sa.Column('period', sa.String()),
        sa.Column('next_charge_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('cancel_at_period_end', sa.Boolean(), server_default='false'),
    )

    op.create_table('invoices',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True)),
        sa.Column('provider', sa.String()),
        sa.Column('external_id', sa.String(), unique=True),
        sa.Column('amount', sa.Integer()),
        sa.Column('currency', sa.String()),
        sa.Column('status', sa.String()),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True)),
    )

    op.create_table('events',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('kind', sa.String()),
        sa.Column('ext_id', sa.String()),
        sa.Column('idempotency_key', sa.String()),
        sa.Column('payload', sa.JSON()),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True)),
    )
    op.create_index('ix_events_kind_ts', 'events', ['kind', 'created_at'])


def downgrade() -> None:
    for t in ['events','invoices','subscriptions','templates','appointments','clients','slots','exceptions','schedule_rules','services','staff','tenants']:
        op.drop_table(t)
