"""Add user_id to Notification model

Revision ID: 9b69e8d4688e
Revises: c639b45954ac
Create Date: 2023-10-17 21:05:18.249267

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "9b69e8d4688e"
down_revision = "c639b45954ac"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("notification", sa.Column("user_id", sa.Integer(), nullable=True))
    op.create_foreign_key(None, "notification", "user", ["user_id"], ["id"])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "notification", type_="foreignkey")
    op.drop_column("notification", "user_id")
    # ### end Alembic commands ###
