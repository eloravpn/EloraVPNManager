"""Add Reality to InboundSecurity

Revision ID: 1d0e2502f045
Revises: 76945c05dad7
Create Date: 2023-10-26 20:18:04.776891

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "1d0e2502f045"
down_revision = "76945c05dad7"
branch_labels = None
depends_on = None

# Describing of enum
enum_name = "inboundsecurity"
temp_enum_name = f"temp_{enum_name}"
old_values = ("default", "none")
new_values = ("reality", *old_values)
downgrade_to = ("default", "none")  # on downgrade convert [0] to [1]
old_type = sa.Enum(*old_values, name=enum_name)
new_type = sa.Enum(*new_values, name=enum_name)
temp_type = sa.Enum(*new_values, name=temp_enum_name)

# Describing of table
table_name = "inbound_config"
table2_name = "inbound"
column_name = "security"
temp_table = sa.sql.table(table_name, sa.Column(column_name, new_type, nullable=False))
temp_table2 = sa.sql.table(
    table2_name, sa.Column(column_name, new_type, nullable=False)
)


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

    with op.batch_alter_table(table2_name) as batch_op:
        batch_op.alter_column(
            column_name,
            existing_type=old_type,
            type_=temp_type,
            existing_nullable=False,
            postgresql_using=f"{column_name}::text::{temp_enum_name}",
        )

    # remove old enum, create new enum
    old_type.drop(op.get_bind(), checkfirst=False)
    # op.execute('DROP TYPE '+ enum_name + ' CASCADE')
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

    with op.batch_alter_table(table2_name) as batch_op:
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
