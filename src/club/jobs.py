import asyncio
from datetime import datetime
from typing import List

from apscheduler.triggers.cron import CronTrigger
from telebot.apihelper import ApiTelegramException

from src import scheduler, config, logger
from src.club.campaigns import CampaignRegistryBase
from src.club.schemas import ClubProfileCreate
from src.database import GetDB
import src.users.service as user_service
import src.club.service as club_service
from src.telegram import bot
from src.users.models import User


def run_campaigns():

    create_new_club_profiles()
    sync_club_profiles()

    with GetDB() as db:
        for campaign in CampaignRegistryBase.CAMPAIGN_REGISTRY:
            # Get a handle to run the campaign
            campaign_class = CampaignRegistryBase.CAMPAIGN_REGISTRY[campaign]
            campaign_instance = campaign_class()
            campaign_instance.run_campaign(db=db)


def sync_club_profiles():
    with GetDB() as db:
        start = datetime.utcnow().timestamp()

        logger.info("Start sync Club Profile total subset " + str(datetime.now()))

        db_users = user_service.get_users(
            db=db,
            sort=[user_service.UserSortingOptions["-created"]],
            return_with_count=False,
        )

        logger.info(f"Total users is {len(db_users)}")
        for db_user in db_users:
            try:

                referral_users = user_service.get_user_referral_users(db, db_user.id)

                if len(referral_users) > 0:
                    logger.info(
                        f"User: {db_user.full_name} Referral users: {len(referral_users)}"
                    )

                    total_subset = _calculate_referral_count(referral_users)
                    db_club_profile = club_service.get_club_profile(db, db_user.id)

                    logger.info(
                        f"Referral user for {db_user.full_name} count is {total_subset}/{len(referral_users)}"
                    )

                    club_service.update_club_profile_subset(
                        db, db_club_profile, total_subset
                    )

            except Exception as error:
                logger.error(error)

        end = datetime.utcnow().timestamp()
        logger.info(f"Finish sync Club Profile total subset {int(end - start)} Sec")


def create_new_club_profiles():
    with GetDB() as db:
        db_users = user_service.get_users(
            db=db,
            sort=[user_service.UserSortingOptions["-created"]],
            return_with_count=False,
        )
        for db_user in db_users:
            try:
                db_club_profile = club_service.get_club_profile(db, db_user.id)

                if db_club_profile is None:
                    club_pofile = ClubProfileCreate(total_score=0, total_subset=0)

                    club_service.create_club_profile(db, db_user, club_pofile)

                    logger.info(
                        f"New club profile hase been added for {db_user.full_name} [{db_user.id}]"
                    )

            except Exception as error:
                logger.error(error)


def _is_channel_member(db_user: User):
    result = bot.get_chat_member(
        chat_id=f"@{config.TELEGRAM_CHANNEL}", user_id=db_user.telegram_chat_id
    )
    if result.status in ["administrator", "creator", "member"]:
        logger.info(f"User {db_user.full_name} is channel member")
        return True
    else:
        return False


def _calculate_referral_count(users: List[User]):
    count = 0
    for db_user in users:
        try:
            if _is_channel_member(db_user=db_user):
                count += 1
        except ApiTelegramException:
            pass
    return count


scheduler.add_job(
    func=run_campaigns,
    max_instances=1,
    trigger=CronTrigger.from_crontab(config.CLUB_CAMPAIGN_RUN_CRON),
)
