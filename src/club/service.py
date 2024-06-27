from enum import Enum

from sqlalchemy import and_
from sqlalchemy.orm import Session

from src import config
from src.club.models import ClubScore, ClubProfile
from src.club.schemas import ClubScoreCreate, ClubProfileCreate
from src.commerce import service as commerce_service
from src.commerce.schemas import TransactionCreate, TransactionType
from src.users.models import User

ClubScoreSortingOptions = Enum(
    "ClubScoreSortingOptions",
    {
        "created": ClubScore.created_at.asc(),
        "-created": ClubScore.created_at.desc(),
        "modified": ClubScore.modified_at.asc(),
        "-modified": ClubScore.modified_at.desc(),
        "score": ClubScore.score.asc(),
        "-score": ClubScore.score.desc(),
    },
)


def create_score(db: Session, db_user: User, club_score: ClubScoreCreate) -> ClubScore:
    db_club_score = ClubScore(
        user_id=db_user.id,
        unique_id=club_score.unique_id,
        campaign_key=club_score.campaign_key,
        score=club_score.score,
        description=club_score.description,
    )

    db.add(db_club_score)

    transaction = TransactionCreate(
        user_id=db_user.id,
        description=club_score.description,
        amount=club_score.score * config.CLUB_SCORE_PRICE,
        type=TransactionType.bonus,
    )

    commerce_service.create_transaction(db=db, db_user=db_user, transaction=transaction)

    db.refresh(db_club_score)
    return db_club_score


def create_club_profile(
    db: Session, db_user: User, club_profile: ClubProfileCreate
) -> ClubProfile:
    db_club_profile = ClubProfile(
        user_id=db_user.id,
        total_score=club_profile.total_score,
        total_subset=club_profile.total_subset,
    )

    db.add(db_club_profile)
    db.commit()

    db.refresh(db_club_profile)
    return db_club_profile


def get_club_profile(db: Session, user_id: int) -> ClubProfile:
    return db.query(ClubProfile).filter(and_(ClubProfile.user_id == user_id)).first()


def update_club_profile_subset(
    db: Session, db_club_profile: ClubProfile, total_subset: int
) -> ClubProfile:

    db_club_profile.total_subset = total_subset

    db.commit()
    db.refresh(db_club_profile)

    return db_club_profile


def update_club_profile_score(
    db: Session, db_club_profile: ClubProfile, total_score: int
) -> ClubProfile:

    db_club_profile.total_score = total_score

    db.commit()
    db.refresh(db_club_profile)

    return db_club_profile


def get_club_score_by_unique_id(
    db: Session, unique_id: str, campaign_key: str
) -> ClubScore:
    return (
        db.query(ClubScore)
        .filter(
            and_(
                ClubScore.campaign_key == campaign_key, ClubScore.unique_id == unique_id
            )
        )
        .first()
    )
