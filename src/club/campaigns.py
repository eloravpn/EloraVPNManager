import math
from typing import Dict, List

from sqlalchemy.orm import Session
from telebot.apihelper import ApiTelegramException

from src import config, logger, messages
from src.club import service as club_service
from src.club.schemas import ClubScoreCreate
from src.telegram import bot
from src.users import service as user_service
from src.users.models import User
from src.users.service import UserSortingOptions


class CampaignRegistryBase(type):
    CAMPAIGN_REGISTRY: Dict[str, "CampaignRegistryBase"] = {}

    def __new__(cls, name, bases, attrs):
        new_cls = type.__new__(cls, name, bases, attrs)
        """
            Here the name of the class is used as key but it could be any class
            parameter.
        """
        cls.CAMPAIGN_REGISTRY[new_cls.__name__] = new_cls
        return new_cls

    @classmethod
    def get_registry(cls):
        return dict(cls.CAMPAIGN_REGISTRY)


class CampaignRegistryBaseClass(metaclass=CampaignRegistryBase):
    """
    Any class that will inherits from CampaignRegistryBaseClass will be included
    inside the dict CampaignRegistryBase.REGISTRY, the key being the name of the
    class and the associated value, the class itself.
    """

    def run_campaign(self, db: Session):
        pass


class ReferralCampaign(CampaignRegistryBaseClass):

    @classmethod
    def _calculate_score(cls, total_subset: int):

        if total_subset < 0:
            return 0

        if 0 <= total_subset <= 30:
            return config.REFERRAL_SCORE_0_TO_30
        elif 31 < total_subset <= 80:
            return config.REFERRAL_SCORE_30_TO_80
        elif 81 < total_subset <= 100:
            return config.REFERRAL_SCORE_80_TO_1000

    @classmethod
    def _is_channel_member(cls, db_user: User):
        result = bot.get_chat_member(
            chat_id=config.TELEGRAM_CHANNEL,
            user_id=db_user.telegram_chat_id,
        )
        if result.status in ["administrator", "creator", "member"]:
            return True
        else:
            return False

    def run_campaign(self, db: Session):
        logger.info(f"Run {self.__class__.__name__}")
        db_users = user_service.get_users(
            db=db,
            limit=100,
            sort=[UserSortingOptions["-created"]],
            return_with_count=False,
        )
        for db_user in db_users:
            try:
                if (
                    db_user.referral_user_id
                    and db_user.referral_user_id > 0
                    and db_user.telegram_chat_id
                ):

                    if self._is_channel_member(db_user=db_user):
                        referral_user = user_service.get_user(
                            db=db, user_id=db_user.referral_user_id
                        )

                        if referral_user is not None:

                            club_score = club_service.get_club_score_by_unique_id(
                                db=db,
                                unique_id=str(db_user.id),
                                campaign_key=self.__class__.__name__,
                            )

                            if club_score is None:
                                db_club_profile = club_service.get_club_profile(
                                    db, referral_user.id
                                )

                                logger.info(
                                    f"Total subset for this user is {db_club_profile.total_subset}"
                                )

                                logger.info(
                                    f"User {db_user.full_name} with create date {db_user.created_at}"
                                    f" invited by {referral_user.full_name}"
                                )

                                club_score = ClubScoreCreate(
                                    unique_id=str(db_user.id),
                                    score=self._calculate_score(
                                        total_subset=db_club_profile.total_subset
                                    ),
                                    campaign_key=self.__class__.__name__,
                                    description=messages.REFERRAL_BONUS_DESCRIPTION.format(
                                        full_name=db_user.full_name
                                    ),
                                )
                                club_service.create_score(
                                    db=db, db_user=referral_user, club_score=club_score
                                )

            except ApiTelegramException:
                pass
            except Exception as error:
                logger.error(error)
