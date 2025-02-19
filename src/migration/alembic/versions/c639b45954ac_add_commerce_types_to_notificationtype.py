"""Add commerce types to notificationtype

Revision ID: c639b45954ac
Revises: 42f7b8e1a7af
Create Date: 2023-10-17 20:38:30.870588

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c639b45954ac"
down_revision = "42f7b8e1a7af"
branch_labels = None
depends_on = None

# Describing of enum
enum_name = "notificationtype"
temp_enum_name = f"temp_{enum_name}"
old_values = ("used_traffic", "expire_time")
new_values = ("payment", "order", "transaction", "general", "account", *old_values)
downgrade_to = ("used_traffic", "expire_time")  # on downgrade convert [0] to [1]
old_type = sa.Enum(*old_values, name=enum_name)
new_type = sa.Enum(*new_values, name=enum_name)
temp_type = sa.Enum(*new_values, name=temp_enum_name)


# Describing of table
table_name = "notification"
column_name = "type"
temp_table = sa.sql.table(table_name, sa.Column(column_name, new_type, nullable=False))


def upgrade() -> None:
    # temp type to use instead of old one
    temp_type.create(op.get_bind(), checkfirst=False)

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
