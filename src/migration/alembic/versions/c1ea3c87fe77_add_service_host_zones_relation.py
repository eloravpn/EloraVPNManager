"""Add service host zones relation

Revision ID: c1ea3c87fe77
Revises: d986a59ac521
Create Date: 2024-06-07 17:53:24.273209

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c1ea3c87fe77"
down_revision = "d986a59ac521"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "service_host_zone",
        sa.Column("service_id", sa.Integer(), nullable=False),
        sa.Column("host_zone_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["host_zone_id"],
            ["host_zone.id"],
        ),
        sa.ForeignKeyConstraint(
            ["service_id"],
            ["service.id"],
        ),
        sa.PrimaryKeyConstraint("service_id", "host_zone_id"),
    )
    op.drop_constraint("service_host_zone_id_fkey", "service", type_="foreignkey")
    op.drop_column("service", "host_zone_id")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "service",
        sa.Column(
            "host_zone_id",
            sa.INTEGER(),
            server_default=sa.text("1"),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.create_foreign_key(
        "service_host_zone_id_fkey", "service", "host_zone", ["host_zone_id"], ["id"]
    )
    op.drop_table("service_host_zone")
    # ### end Alembic commands ###
