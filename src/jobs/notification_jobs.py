from datetime import datetime, timedelta

from telebot import types

from src import scheduler, logger, config
from src.accounts.service import (
    get_accounts,
)
from src.database import GetDB
from src.notification.schemas import (
    NotificationUsedTrafficLevel,
    NotificationCreate,
    NotificationType,
    NotificationExpireTimeLevel,
)
from src.notification.service import create_notification, get_notifications
from src.telegram import utils
from src.telegram.user import messages


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
                        db_account=account,
                        notification=NotificationCreate(
                            message=messages.USED_TRAFFIC_NOTIFICATION.format(
                                admin_id=config.TELEGRAM_ADMIN_USER_NAME,
                                used_traffic_percent=min_percent,
                            ),
                            level=level.value,
                            type=NotificationType.used_traffic,
                        ),
                    )
                    send_approval_message(account, db_notification)


def send_approval_message(account, db_notification):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton(
            text="Approve",
            callback_data=f"approve_notification:{db_notification.id}",
        ),
        types.InlineKeyboardButton(
            text="Decline!",
            callback_data=f"decline_notification:{db_notification.id}",
        ),
    )
    utils.send_message_to_admin(
        message=f"Send notification to {account.user.full_name}/ <code>{account.email}</code> \n"
        + db_notification.message,
        keyboard=keyboard,
    )


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
                        db_account=account,
                        notification=NotificationCreate(
                            message=messages.EXPIRE_TIME_NOTIFICATION.format(
                                admin_id=config.TELEGRAM_ADMIN_USER_NAME,
                                days=max_days,
                            ),
                            level=level.value,
                            type=NotificationType.expire_time,
                        ),
                    )
                    send_approval_message(account, db_notification)


def expire_time_notification_job():
    days_to_expire_notification_job(min_days=0, max_days=3)


def used_traffic_notification_job():
    percent_used_traffic_notification_job(min_percent=80, max_percent=95)
    percent_used_traffic_notification_job(min_percent=95, max_percent=100)


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
