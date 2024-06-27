"""Add Club Score model

Revision ID: fe1a3ae27e35
Revises: c1ea3c87fe77
Create Date: 2024-06-12 22:27:17.062645

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "fe1a3ae27e35"
down_revision = "c1ea3c87fe77"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "club_score",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("unique_id", sa.String(length=128), nullable=False),
        sa.Column("campaign_key", sa.String(length=128), nullable=False),
        sa.Column("score", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("modified_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "campaign_key_unique_id_idx",
        "club_score",
        ["unique_id", "campaign_key"],
        unique=True,
    )
    op.create_index(
        op.f("ix_club_score_campaign_key"), "club_score", ["campaign_key"], unique=False
    )
    op.create_index(op.f("ix_club_score_id"), "club_score", ["id"], unique=False)
    op.create_index(
        op.f("ix_club_score_unique_id"), "club_score", ["unique_id"], unique=False
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_club_score_unique_id"), table_name="club_score")
    op.drop_index(op.f("ix_club_score_id"), table_name="club_score")
    op.drop_index(op.f("ix_club_score_campaign_key"), table_name="club_score")
    op.drop_index("campaign_key_unique_id_idx", table_name="club_score")
    op.drop_table("club_score")
    # ### end Alembic commands ###
