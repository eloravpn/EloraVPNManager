"""Add gRPC to InboundNetwork

Revision ID: 6f6fcd3424aa
Revises: 1d0e2502f045
Create Date: 2023-10-27 15:56:31.716036

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "6f6fcd3424aa"
down_revision = "1d0e2502f045"
branch_labels = None
depends_on = None

# Describing of enum
enum_name = "inboundnetwork"
temp_enum_name = f"temp_{enum_name}"
old_values = ("tcp", "ws")
new_values = ("grpc", *old_values)
downgrade_to = ("ws", "tcp")  # on downgrade convert [0] to [1]
old_type = sa.Enum(*old_values, name=enum_name)
new_type = sa.Enum(*new_values, name=enum_name)
temp_type = sa.Enum(*new_values, name=temp_enum_name)

# Describing of table
table_name = "inbound_config"
column_name = "network"


def upgrade() -> None:
    # temp type to use instead of old one
    temp_type.create(op.get_bind(), checkfirst=False)
    op.execute("ALTER TABLE inbound_config ALTER COLUMN network DROP DEFAULT")

    # changing of column type from old enum to new one.
    # SQLite will create temp table for this
    with op.batch_alter_table(table_name) as batch_op:
        batch_op.alter_column(
            column_name,
            existing_type=old_type,
            type_=temp_type,
            existing_nullable=False,
            postgresql_using=f"{column_name}::text::{temp_enum_name}",
        )

    # remove old enum, create new enum
    old_type.drop(op.get_bind(), checkfirst=False)
    new_type.create(op.get_bind(), checkfirst=False)

    # changing of column type from temp enum to new one.
    # SQLite will create temp table for this
    with op.batch_alter_table(table_name) as batch_op:
        batch_op.alter_column(
            column_name,
            existing_type=temp_type,
            type_=new_type,
            existing_nullable=False,
            postgresql_using=f"{column_name}::text::{enum_name}",
        )

    # remove temp enum
    temp_type.drop(op.get_bind(), checkfirst=False)


def downgrade() -> None:
    # TODO
    raise NotImplementedError
