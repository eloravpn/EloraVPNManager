"""Add Desription To Club Score

Revision ID: 318548385b4c
Revises: fe1a3ae27e35
Create Date: 2024-06-22 20:01:25.978872

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "318548385b4c"
down_revision = "fe1a3ae27e35"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "club_score", sa.Column("description", sa.String(length=4000), nullable=True)
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("club_score", "description")
    # ### end Alembic commands ###
