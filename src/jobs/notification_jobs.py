import logging
from datetime import datetime, timedelta

from telebot import types

from src import scheduler, config
from src.logger import logger

from src.accounts.service import (
    get_accounts,
)
from src.database import GetDB
from src.notification.schemas import (
    NotificationUsedTrafficLevel,
    NotificationCreate,
    NotificationType,
    NotificationExpireTimeLevel,
    NotificationStatus,
)
from src.notification.service import (
    create_notification,
    get_notifications,
    update_status,
    NotificationSortingOptions,
)
from src.telegram import utils
from src.telegram.user import messages
from src.telegram.user.keyboard import BotUserKeyboard
from src.users.service import get_user
from src.utils.telebot import KeyboardFactory


def percent_used_traffic_notification_job(min_percent: int, max_percent: int):
    logger.info(
        f"Run percent_used_traffic_notification_job from {min_percent} to {max_percent}"
    )

    level = NotificationUsedTrafficLevel.full_percent_used

    if min_percent == 80:
        level = NotificationUsedTrafficLevel.eighty_percent
    elif min_percent == 95:
        level = NotificationUsedTrafficLevel.ninety_five_percent

    with GetDB() as db:
        for account in get_accounts(
            db=db, filter_enable=True, enable=True, return_with_count=False
        ):
            # account_expire_time = account.expired_at.timestamp() * 1000s
            if (
                min_percent <= account.used_traffic_percent < max_percent
                and account.data_limit != 0
            ):
                logger.info(f"Account: {account.user.full_name}/ {account.email} ")
                logger.info(f"Used traffic percent: {account.used_traffic_percent}")

                notifications, count = get_notifications(
                    db=db,
                    account_id=account.id,
                    notification_type=NotificationType.used_traffic.value,
                    level=level.value,
                )

                logger.info(f"Notification Count: {count}")

                if count == 0:
                    db_notification = create_notification(
                        db=db,
                        db_user=account.user,
                        db_account=account,
                        notification=NotificationCreate(
                            user_id=account.user.id,
                            message=messages.USED_TRAFFIC_NOTIFICATION.format(
                                admin_id=config.TELEGRAM_ADMIN_USER_NAME,
                                account_email=account.email,
                                service_title=account.service_title,
                                used_traffic_percent=min_percent,
                            ),
                            level=level.value,
                            approve=True,
                            type=NotificationType.used_traffic,
                        ),
                    )
                    # utils.send_approval_message(account, db_notification)


def days_to_expire_notification_job(min_days: int, max_days: int):
    today = datetime.now()
    min_days_later = today + timedelta(days=min_days)
    max_days_later = today + timedelta(days=max_days)

    logger.info(
        f"Run days_to_expire_notification_job from {min_days} to {max_days} days later"
    )
    logger.info(f"Min days later: {min_days_later}")
    logger.info(f"Max days later: {max_days_later}")

    level = NotificationExpireTimeLevel.three_day

    with GetDB() as db:
        for account in get_accounts(
            db=db, filter_enable=True, enable=True, return_with_count=False
        ):
            if account.expired_at and account.expired_at < max_days_later:
                logger.info(f"Account: {account.user.full_name}/ {account.email} ")
                logger.info(f"Account expire date: {account.expired_at}")

                notifications, count = get_notifications(
                    db=db,
                    account_id=account.id,
                    notification_type=NotificationType.expire_time.value,
                    level=level.value,
                )
                logger.info(f"Notification Count: {count}")

                if count == 0:
                    db_notification = create_notification(
                        db=db,
                        db_user=account.user,
                        db_account=account,
                        notification=NotificationCreate(
                            user_id=account.user.id,
                            message=messages.EXPIRE_TIME_NOTIFICATION.format(
                                service_title=account.service_title,
                                account_email=account.email,
                                days=max_days,
                            ),
                            approve=True,
                            level=level.value,
                            type=NotificationType.expire_time,
                        ),
                    )
                    # utils.send_approval_message(account, db_notification)


def process_pending_notifications():
    logger.info("Process Pending and approved notifications")
    with GetDB() as db:
        notifications, count = get_notifications(
            db=db,
            limit=config.SEND_PENDING_NOTIFICATION_LIMIT,
            status=NotificationStatus.pending,
            approve=1,
            sort=[NotificationSortingOptions["modified"]],
        )

        for db_notification in notifications:
            if db_notification.user_id:
                db_user = get_user(db=db, user_id=db_notification.user_id)

                try:
                    admin_message = messages.ADMIN_NOTIFICATION.format(
                        type=db_notification.type.value,
                        user_detail=f"{db_user.telegram_profile_full}",
                        message=db_notification.message,
                    )

                    update_status(
                        db=db,
                        db_notification=db_notification,
                        status=NotificationStatus.sent,
                        approve=True,
                    )

                    if db_notification.send_to_admin:
                        utils.send_message_to_admin(
                            message=admin_message,
                            parse_mode="html",
                            disable_notification=True,
                        )
                    keyboard = None

                    if db_notification.keyboard is not None:
                        keyboard = KeyboardFactory.from_json_string(
                            db_notification.keyboard
                        )

                    if db_notification.photo_url:
                        utils.send_photo_to_user(
                            chat_id=db_user.telegram_chat_id,
                            caption=db_notification.message,
                            photo_url=db_notification.photo_url,
                            parse_mode="html",
                            keyboard=(
                                BotUserKeyboard.main_menu()
                                if keyboard is None
                                else keyboard
                            ),
                        )
                    else:
                        utils.send_message_to_user(
                            chat_id=db_user.telegram_chat_id,
                            message=db_notification.message,
                            parse_mode="html",
                            keyboard=(
                                BotUserKeyboard.main_menu()
                                if keyboard is None
                                else keyboard
                            ),
                        )

                except Exception as error:
                    logging.error(error)
                    update_status(
                        db=db,
                        db_notification=db_notification,
                        status=NotificationStatus.failed,
                        approve=True,
                    )


def expire_time_notification_job():
    days_to_expire_notification_job(min_days=0, max_days=3)


def used_traffic_notification_job():
    percent_used_traffic_notification_job(min_percent=80, max_percent=95)
    percent_used_traffic_notification_job(min_percent=95, max_percent=100)


if config.ENABLE_NOTIFICATION_SEND_PENDING_JOBS:
    scheduler.add_job(
        func=process_pending_notifications,
        max_instances=1,
        trigger="interval",
        seconds=config.SEND_PENDING_NOTIFICATION_INTERVAL,
    )

if config.ENABLE_NOTIFICATION_JOBS:
    scheduler.add_job(
        func=used_traffic_notification_job,
        max_instances=1,
        trigger="interval",
        seconds=config.USED_TRAFFIC_NOTIFICATION_INTERVAL,
    )

    scheduler.add_job(
        func=expire_time_notification_job,
        max_instances=1,
        trigger="interval",
        seconds=config.EXPIRE_TIME_NOTIFICATION_INTERVAL,
    )


else:
    logger.warn("Notification jobs are disabled!")
