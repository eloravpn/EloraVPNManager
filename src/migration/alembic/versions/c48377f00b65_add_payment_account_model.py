"""Add Payment Account Model

Revision ID: c48377f00b65
Revises: b1bc7aad133f
Create Date: 2024-12-18 20:05:10.603209

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c48377f00b65"
down_revision = "b1bc7aad133f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "payment_account",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("card_number", sa.String(length=16), nullable=True),
        sa.Column("account_number", sa.String(length=128), nullable=True),
        sa.Column("bank_name", sa.String(length=128), nullable=True),
        sa.Column("shaba", sa.String(length=128), nullable=True),
        sa.Column("owner_name", sa.String(length=128), nullable=True),
        sa.Column("owner_family", sa.String(length=128), nullable=True),
        sa.Column("enable", sa.Boolean(), nullable=True),
        sa.Column("min_payment_for_bot", sa.BigInteger(), nullable=True),
        sa.Column("min_payment_amount", sa.BigInteger(), nullable=True),
        sa.Column("max_daily_transactions", sa.Integer(), nullable=True),
        sa.Column("max_daily_amount", sa.BigInteger(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("modified_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_payment_account_account_number"),
        "payment_account",
        ["account_number"],
        unique=True,
    )
    op.create_index(
        op.f("ix_payment_account_bank_name"),
        "payment_account",
        ["bank_name"],
        unique=True,
    )
    op.create_index(
        op.f("ix_payment_account_card_number"),
        "payment_account",
        ["card_number"],
        unique=True,
    )
    op.create_index(
        op.f("ix_payment_account_id"), "payment_account", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_payment_account_shaba"), "payment_account", ["shaba"], unique=True
    )
    op.drop_index("ix_config_settings_key", table_name="config_settings")
    op.create_index(
        op.f("ix_config_settings_key"), "config_settings", ["key"], unique=False
    )
    op.add_column(
        "payment", sa.Column("payment_account_id", sa.Integer(), nullable=True)
    )
    op.create_foreign_key(
        None, "payment", "payment_account", ["payment_account_id"], ["id"]
    )
    op.add_column(
        "transaction", sa.Column("payment_account_id", sa.Integer(), nullable=True)
    )
    op.create_foreign_key(
        None, "transaction", "payment_account", ["payment_account_id"], ["id"]
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "transaction", type_="foreignkey")
    op.drop_column("transaction", "payment_account_id")
    op.drop_constraint(None, "payment", type_="foreignkey")
    op.drop_column("payment", "payment_account_id")
    op.drop_index(op.f("ix_config_settings_key"), table_name="config_settings")
    op.create_index("ix_config_settings_key", "config_settings", ["key"], unique=False)
    op.drop_index(op.f("ix_payment_account_shaba"), table_name="payment_account")
    op.drop_index(op.f("ix_payment_account_id"), table_name="payment_account")
    op.drop_index(op.f("ix_payment_account_card_number"), table_name="payment_account")
    op.drop_index(op.f("ix_payment_account_bank_name"), table_name="payment_account")
    op.drop_index(
        op.f("ix_payment_account_account_number"), table_name="payment_account"
    )
    op.drop_table("payment_account")
    # ### end Alembic commands ###