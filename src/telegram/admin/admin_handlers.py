import logging

from telebot import types

from src import config
from src.accounts.service import get_account
from src.database import GetDB
from src.notification.schemas import NotificationStatus
from src.notification.service import get_notification, update_status
from src.telegram import bot


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("approve_notification:")
)
def approve_notification(call: types.CallbackQuery):
    telegram_user = call.from_user

    notification_id = int(call.data.split(":")[1])
    with GetDB() as db:
        db_notification = get_notification(db=db, notification_id=notification_id)
        db_account = get_account(db=db, account_id=db_notification.account_id)

        try:
            bot.send_message(
                text=db_notification.message,
                chat_id=db_account.user.telegram_chat_id,
                parse_mode="html",
            )

            update_status(
                db=db,
                db_notification=db_notification,
                status=NotificationStatus.sent,
                approve=True,
            )

            bot.edit_message_text(
                text=f"Notification with id <code>{db_notification.id}</code> Approved and Sent to {db_account.user.full_name}!",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                parse_mode="html",
            )
        except Exception as error:
            logging.error(error)
            update_status(
                db=db,
                db_notification=db_notification,
                status=NotificationStatus.failed,
                approve=True,
            )


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("decline_notification:")
)
def decline_notification(call: types.CallbackQuery):
    telegram_user = call.from_user

    notification_id = call.data.split(":")[1]
    with GetDB() as db:
        db_notification = get_notification(db=db, notification_id=notification_id)
        db_account = get_account(db=db, account_id=db_notification.account_id)

        update_status(
            db=db,
            db_notification=db_notification,
            status=NotificationStatus.canceled,
            approve=False,
        )

        bot.edit_message_text(
            text=f"Notification with id <code>{db_notification.id}</code> Declined to sent to {db_account.user.full_name}!",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode="html",
        )
