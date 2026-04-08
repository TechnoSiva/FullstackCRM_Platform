"""Initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-02-28
"""

from alembic import op
import sqlalchemy as sa


revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


user_role = sa.Enum("ADMIN", "MANAGER", "SALES", name="userrole")
lead_status = sa.Enum("NEW", "CONTACTED", "QUALIFIED", "LOST", "WON", name="leadstatus")
opportunity_stage = sa.Enum(
    "PROSPECTING",
    "QUALIFICATION",
    "PROPOSAL",
    "NEGOTIATION",
    "CLOSED_WON",
    "CLOSED_LOST",
    name="opportunitystage",
)


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False, unique=True),
        sa.Column("password", sa.String(length=255), nullable=False),
        sa.Column("role", user_role, nullable=False),
    )
    op.create_index("ix_users_id", "users", ["id"])
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "leads",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("source", sa.String(length=100), nullable=False),
        sa.Column("status", lead_status, nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("assigned_to_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
    )
    op.create_index("ix_leads_id", "leads", ["id"])

    op.create_table(
        "opportunities",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("lead_id", sa.Integer(), sa.ForeignKey("leads.id"), nullable=False),
        sa.Column("deal_value", sa.Float(), nullable=False),
        sa.Column("stage", opportunity_stage, nullable=False),
        sa.Column("probability", sa.Float(), nullable=False),
        sa.Column("expected_close_date", sa.Date(), nullable=True),
    )
    op.create_index("ix_opportunities_id", "opportunities", ["id"])

    op.create_table(
        "activities",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("lead_id", sa.Integer(), sa.ForeignKey("leads.id"), nullable=False),
        sa.Column("type", sa.String(length=80), nullable=False),
        sa.Column("notes", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_activities_id", "activities", ["id"])


def downgrade() -> None:
    op.drop_index("ix_activities_id", table_name="activities")
    op.drop_table("activities")
    op.drop_index("ix_opportunities_id", table_name="opportunities")
    op.drop_table("opportunities")
    op.drop_index("ix_leads_id", table_name="leads")
    op.drop_table("leads")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_index("ix_users_id", table_name="users")
    op.drop_table("users")
    opportunity_stage.drop(op.get_bind(), checkfirst=False)
    lead_status.drop(op.get_bind(), checkfirst=False)
    user_role.drop(op.get_bind(), checkfirst=False)
