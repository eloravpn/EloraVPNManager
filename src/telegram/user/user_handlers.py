import qrcode as qrcode
from telebot import types, custom_filters
from telebot.apihelper import ApiTelegramException
from telebot.custom_filters import IsReplyFilter
from telebot.formatting import escape_markdown
from telebot.types import ForceReply

from src import config
from src.logger import logger
from src.commerce.exc import (
    MaxOpenOrderError,
    MaxPendingOrderError,
    NoEnoughBalanceError,
)
from src.commerce.schemas import OrderStatus
from src.telegram import bot, utils, payment_bot
from src.telegram.user import captions, messages
from src.telegram.user.keyboard import BotUserKeyboard
from src.users.models import User

change_account_name_message_ids = {}


@bot.message_handler(content_types=["web_app_data"])
def echo_yall(message):
    logger.info(message)
    bot.send_message(message.chat.id, "Thank you!")


class IsSubscribedUser(custom_filters.SimpleCustomFilter):
    # Class will check whether the user is admin or creator in group or not
    key = "is_subscribed_user"

    @staticmethod
    def check(message: types.Message):
        try:
            telegram_user = message.from_user

            referral_user = None

            if isinstance(message, types.Message) and message.text:
                referral_user = IsSubscribedUser.get_referral_user(
                    message_text=message.text
                )

            user = utils.add_or_get_user(
                telegram_user=telegram_user, referral_user=referral_user
            )

            if not config.TELEGRAM_CHANNEL or not user.force_join_channel:
                return True
            else:
                result = bot.get_chat_member(
                    f"@{config.TELEGRAM_CHANNEL}", user_id=message.from_user.id
                )
                if result.status not in ["administrator", "creator", "member"]:
                    bot.send_message(
                        chat_id=message.from_user.id,
                        text=messages.PLEASE_SUBSCRIBE_MESSAGE.format(
                            admin_id=config.TELEGRAM_ADMIN_USER_NAME
                        ),
                        disable_web_page_preview=False,
                        reply_markup=BotUserKeyboard.channel_menu(),
                        parse_mode="markdown",
                    )
                    return False
                else:
                    return True
        except Exception as error:
            logger.error(error)

        return False

    @staticmethod
    def get_referral_user(message_text) -> User:
        user = None
        try:
            if message_text.startswith("/start"):
                split_message_text = message_text.split(" ")
                if len(split_message_text) == 2:
                    referral_code = message_text.split(" ")[1]
                    logger.info(f"Referral code: {referral_code}")
                    user = utils.get_user(user_id=int(referral_code))
        except Exception as error:
            logger.error(error)
        return user


bot.add_custom_filter(IsSubscribedUser())
bot.add_custom_filter(IsReplyFilter())


@bot.message_handler(commands=["game"], is_subscribed_user=True)
def start_game(message: types.Message):
    keyboard = types.InlineKeyboardMarkup(row_width=1)

    keyboard.add(
        types.InlineKeyboardButton(
            text="Lets go!", web_app=types.WebAppInfo(url=config.WEB_APP_URL)
        )
    )

    bot.send_message(
        chat_id=message.from_user.id,
        text="Play!",
        disable_web_page_preview=True,
        reply_markup=keyboard,
        parse_mode="markdown",
    )


# Handle '/start' and '/help'
@bot.message_handler(commands=["help", "start"], is_subscribed_user=True)
def send_welcome(message: types.Message):
    bot.send_message(
        chat_id=message.from_user.id,
        text=messages.WELCOME_MESSAGE.format(
            admin_id=config.TELEGRAM_ADMIN_USER_NAME,
            telegram_channel_url=config.TELEGRAM_CHANNEL_URL,
        ),
        disable_web_page_preview=True,
        reply_markup=BotUserKeyboard.main_menu(),
        parse_mode="markdown",
    )


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
# @bot.message_handler(func=lambda message: True)
# def echo_message(message):
#     bot.reply_to(message, message.text)


@bot.message_handler(regexp=captions.HELP, is_subscribed_user=True)
def help_command(message):
    bot.reply_to(
        message,
        messages.USAGE_HELP_MESSAGE,
        reply_markup=BotUserKeyboard.help_links(),
        parse_mode="html",
    )


@bot.message_handler(regexp=captions.PRICE_LIST, is_subscribed_user=True)
def price_list(message):
    bot.reply_to(message, messages.PRICE_LIST, parse_mode="html")


@bot.message_handler(regexp=captions.MY_PROFILE, is_subscribed_user=True)
def my_profile(message):
    telegram_user = message.from_user
    user = utils.add_or_get_user(telegram_user=telegram_user)

    bot.reply_to(
        message,
        messages.MY_PROFILE.format(
            user_id=user.id,
            bot_user_name=config.BOT_USER_NAME,
            full_name=user.full_name,
            balance=user.balance_readable if user.balance_readable else 0,
            referral_count=utils.get_user_referral_count(telegram_user=telegram_user),
        ),
        parse_mode="html",
    )


@bot.message_handler(regexp=captions.SUPPORT, is_subscribed_user=True)
def support(message):
    bot.reply_to(
        message,
        text=messages.WELCOME_MESSAGE.format(
            telegram_channel_url=config.TELEGRAM_CHANNEL_URL,
            admin_id=config.TELEGRAM_ADMIN_USER_NAME,
        ),
        parse_mode="markdown",
    )


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("get_payment_receipt:"),
    is_subscribed_user=True,
)
def get_payment_receipt(call: types.CallbackQuery):
    account_id = call.data.split(":")[1]

    message = bot.send_message(
        call.from_user.id,
        messages.GET_PAYMENT_RECEIPT_MESSAGE,
        reply_markup=ForceReply(),
    )

    change_account_name_message_ids[f"{message.message_id}:{message.chat.id}"] = (
        account_id
    )

    bot.answer_callback_query(callback_query_id=call.id)


@bot.message_handler(regexp=captions.PAYMENT, is_subscribed_user=True)
def payment(message):
    telegram_user = message.from_user
    user = utils.add_or_get_user(telegram_user=telegram_user)

    payment_accounts = utils.get_available_payment_accounts(user_id=user.id)

    text = messages.NO_BANK_CARD_AVAILABLE.format(
        admin_id=config.TELEGRAM_ADMIN_USER_NAME,
    )

    if payment_accounts:
        text = messages.CARD_PAYMENT_MESSAGE

    bot.reply_to(
        message,
        text=text,
        parse_mode="html",
        disable_web_page_preview=True,
        reply_markup=BotUserKeyboard.payment_card_step_0(
            payment_accounts=payment_accounts
        ),
    )


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("payment_card_step_1:"),
    is_subscribed_user=True,
)
def payment_card_step_1(call: types.CallbackQuery):
    telegram_user = call.from_user
    user = utils.add_or_get_user(telegram_user=telegram_user)

    payment_account_id = call.data.split(":")[1]

    payment_account = utils.get_payment_account(int(payment_account_id))

    card_description = messages.CARD_DESCRIPTION.format(
        payment_notice=payment_account.payment_notice,
        card_number=payment_account.card_number,
        account_number=payment_account.account_number,
        shaba_number=payment_account.shaba,
        bank_name=payment_account.bank_name,
        card_owner=payment_account.owner_family,
    )

    text = messages.PAYMENT_MESSAGE.format(
        telegram_channel_url=config.TELEGRAM_CHANNEL_URL,
        balance=user.balance_readable,
        card_description=card_description,
        admin_id=config.TELEGRAM_ADMIN_USER_NAME,
    )

    bot.edit_message_text(
        text=text,
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=BotUserKeyboard.payment_card_step_1(account_id=0),
        parse_mode="html",
    )


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("my_services:"), is_subscribed_user=True
)
def my_services_call(call: types.CallbackQuery):

    bot.delete_message(chat_id=call.from_user.id, message_id=call.message.id)

    _my_services(call=call)

    bot.answer_callback_query(callback_query_id=call.id)


@bot.message_handler(regexp=captions.MY_SERVICES, is_subscribed_user=True)
def my_services(message: types.Message):

    _my_services(message=message)


def _my_services(message: types.Message = None, call: types.CallbackQuery = None):
    if message:
        telegram_user = message.from_user
    else:
        telegram_user = call.from_user

    user = utils.add_or_get_user(telegram_user=telegram_user)

    my_accounts = sorted(user.accounts, key=lambda x: x.modified_at, reverse=True)

    if not my_accounts:
        if call:
            bot.send_message(
                chat_id=call.from_user.id, text=messages.NO_ACCOUNT_MESSAGE
            )
        else:
            bot.reply_to(message, messages.NO_ACCOUNT_MESSAGE)

    else:
        if call:
            bot.send_message(
                chat_id=call.from_user.id,
                text=messages.ACCOUNT_LIST_MESSAGE,
                reply_markup=BotUserKeyboard.my_accounts(accounts=my_accounts),
                parse_mode="markdown",
            )
        else:
            bot.reply_to(
                message=message,
                text=messages.ACCOUNT_LIST_MESSAGE,
                reply_markup=BotUserKeyboard.my_accounts(accounts=my_accounts),
                parse_mode="markdown",
            )


@bot.message_handler(regexp=captions.GET_TEST_SERVICE, is_subscribed_user=True)
def get_test_service(message):
    telegram_user = message.from_user
    user = utils.add_or_get_user(telegram_user=telegram_user)

    if (
        utils.allow_to_get_new_test_service(user_id=user.id)
        and config.TEST_SERVICE_ID > 0
    ):

        try:
            utils.place_paid_order(
                chat_id=user.telegram_chat_id,
                account_id=0,
                service_id=config.TEST_SERVICE_ID,
            )

            bot.reply_to(
                message,
                messages.GET_TEST_SERVICE_SUCCESS,
                parse_mode="html",
                disable_web_page_preview=True,
            )

            utils.send_message_to_admin(
                messages.GET_TEST_SERVICE_ADMIN_ALERT.format(
                    chat_id=telegram_user.id, full_name=telegram_user.full_name
                ),
                disable_notification=True,
            )

        except Exception as error:
            logger.error(error)
            utils.send_message_to_admin(
                messages.GET_TEST_SERVICE_ERROR_ADMIN_ALERT.format(
                    chat_id=telegram_user.id, full_name=telegram_user.full_name
                ),
                disable_notification=False,
            )

    else:
        bot.reply_to(
            message,
            messages.GET_TEST_SERVICE_NOT_ALLOWED.format(
                day=config.TEST_ACCOUNT_LIMIT_INTERVAL_DAYS,
            ),
            parse_mode="html",
            disable_web_page_preview=True,
        )


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("buy_or_recharge_service:"),
    is_subscribed_user=True,
)
def buy_or_recharge_service_call(call: types.CallbackQuery):

    bot.delete_message(chat_id=call.from_user.id, message_id=call.message.id)

    _buy_or_recharge_service(call=call)

    bot.answer_callback_query(callback_query_id=call.id)


@bot.message_handler(regexp=captions.BUY_OR_RECHARGE_SERVICE, is_subscribed_user=True)
def buy_or_recharge_service_message(message):

    _buy_or_recharge_service(message)


def _buy_or_recharge_service(
    message: types.Message = None, call: types.CallbackQuery = None
):
    available_services = utils.get_available_service()
    if not available_services:
        if call:
            bot.send_message(
                chat_id=call.from_user.id, text=messages.BUY_OR_RECHARGE_SERVICE
            )
        else:
            bot.reply_to(message, messages.BUY_OR_RECHARGE_SERVICE)
    else:
        if call:
            bot.send_message(
                chat_id=call.from_user.id,
                text=messages.BUY_OR_RECHARGE_SERVICE,
                reply_markup=BotUserKeyboard.buy_or_recharge_services(
                    available_services=available_services
                ),
                parse_mode="html",
                disable_web_page_preview=True,
            )
        else:
            bot.reply_to(
                message,
                messages.BUY_OR_RECHARGE_SERVICE,
                reply_markup=BotUserKeyboard.buy_or_recharge_services(
                    available_services=available_services
                ),
                parse_mode="html",
                disable_web_page_preview=True,
            )


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("main_menu:"), is_subscribed_user=True
)
def main_menu(call: types.CallbackQuery):

    bot.delete_message(chat_id=call.from_user.id, message_id=call.message.id)

    bot.send_message(
        chat_id=call.from_user.id,
        text=messages.WELCOME_MESSAGE.format(
            telegram_channel_url=config.TELEGRAM_CHANNEL_URL,
            admin_id=config.TELEGRAM_ADMIN_USER_NAME,
        ),
        disable_web_page_preview=True,
        reply_markup=BotUserKeyboard.main_menu(),
        parse_mode="markdown",
    )

    bot.answer_callback_query(callback_query_id=call.id)


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("online_payment:"), is_subscribed_user=True
)
def online_payment(call: types.CallbackQuery):
    bot.answer_callback_query(
        callback_query_id=call.id,
        show_alert=True,
        text=messages.ONLINE_PAYMENT_IS_DISABLED,
    )


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("recharge_service_1:"),
    is_subscribed_user=True,
)
def recharge_service_1(call: types.CallbackQuery):
    telegram_user = call.from_user

    account_id = call.data.split(":")[1]

    account = utils.get_account(int(account_id))

    service_detail = utils.service_detail(account)

    available_services = utils.get_available_service()

    if not available_services:
        bot.send_message(
            text=messages.BUY_NEW_SERVICE_HELP, chat_id=call.message.chat.id
        )
    bot.reply_to(
        message=call.message,
        text=messages.RECHARGE_SERVICE_HELP.format(service_detail=service_detail),
        reply_markup=BotUserKeyboard.available_services(
            available_services=available_services, account_id=account_id
        ),
        parse_mode="html",
        disable_web_page_preview=True,
    )

    bot.answer_callback_query(callback_query_id=call.id)


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("recharge_service"),
    is_subscribed_user=True,
)
def recharge_service(call: types.CallbackQuery):
    user = utils.add_or_get_user(telegram_user=call.from_user)

    my_accounts = sorted(user.accounts, key=lambda x: x.modified_at, reverse=True)

    if not my_accounts:
        bot.reply_to(call.message, messages.NO_ACCOUNT_MESSAGE)
    else:
        bot.reply_to(
            call.message,
            messages.SELECT_ACCOUNT_TO_RECHARGE_MESSAGE,
            reply_markup=BotUserKeyboard.select_account_to_recharge(
                accounts=my_accounts
            ),
            parse_mode="markdown",
        )

    bot.answer_callback_query(callback_query_id=call.id)


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("buy_service_step_1:"),
    is_subscribed_user=True,
)
def buy_service_step_1(call: types.CallbackQuery):
    telegram_user = call.from_user

    service_id = call.data.split(":")[1]

    account_id = call.data.split(":")[2]

    service = utils.get_service(service_id=int(service_id))

    bot.edit_message_text(
        text=messages.BUY_NEW_SERVICE_CONFIRMATION.format(
            service.name, service.price_readable
        ),
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=BotUserKeyboard.buy_service_step_1(
            service_id=service_id, account_id=account_id
        ),
        parse_mode="html",
    )

    bot.answer_callback_query(callback_query_id=call.id)


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("buy_service_step_2:"),
    is_subscribed_user=True,
)
def buy_service_step_2(call: types.CallbackQuery):
    telegram_user = call.from_user

    service_id = call.data.split(":")[1]
    account_id = call.data.split(":")[2]

    service = utils.get_service(service_id=int(service_id))

    user = utils.add_or_get_user(telegram_user=telegram_user)

    try:
        order = utils.place_paid_order(
            chat_id=telegram_user.id,
            account_id=int(account_id),
            service_id=int(service_id),
        )

        if int(account_id) > 0:
            bot.edit_message_text(
                text=messages.RECHARGE_SERVICE_FINAL.format(order.id),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                parse_mode="html",
            )
        else:
            bot.edit_message_text(
                text=messages.BUY_NEW_SERVICE_FINAL.format(order.id),
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                parse_mode="html",
            )
    except MaxOpenOrderError as error:
        bot.edit_message_text(
            message_id=call.message.message_id,
            chat_id=call.message.chat.id,
            text=messages.NEW_ORDER_MAX_OPEN_ORDERS.format(total="1"),
            parse_mode="html",
        )
    except MaxPendingOrderError as error:
        bot.edit_message_text(
            message_id=call.message.message_id,
            chat_id=call.message.chat.id,
            text=messages.NEW_ORDER_MAX_OPEN_ORDERS.format(total="1"),
            parse_mode="html",
        )
    except NoEnoughBalanceError as error:
        balance = user.balance_readable if user.balance_readable else 0
        bot.edit_message_text(
            message_id=call.message.message_id,
            chat_id=call.message.chat.id,
            text=messages.NEW_ORDER_NO_ENOUGH_BALANCE.format(balance=balance),
            parse_mode="html",
        )

    bot.answer_callback_query(callback_query_id=call.id)


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("buy_service"),
    is_subscribed_user=True,
)
def buy_service(call: types.CallbackQuery):
    available_services = utils.get_available_service()

    if not available_services:
        bot.reply_to(call.message, messages.BUY_NEW_SERVICE_HELP)
    else:
        bot.reply_to(
            call.message,
            messages.BUY_NEW_SERVICE_HELP,
            reply_markup=BotUserKeyboard.available_services(
                available_services=available_services
            ),
            parse_mode="html",
            disable_web_page_preview=True,
        )

    bot.answer_callback_query(callback_query_id=call.id)


@bot.message_handler(content_types=["document", "photo"])
def handle_payment_receipt_docs(message: types.Message):
    try:

        caption = messages.PAYMENT_RECEIPT_DETAIL.format(
            chat_id=message.from_user.id,
            full_name=escape_markdown(str(message.from_user.full_name)),
            username=escape_markdown(str(message.from_user.username)),
            caption=f"{message.caption}",
        )

        caption = caption + utils.get_user_payment_history(message.from_user.id)

        if message.photo:
            photo_index = len(message.photo)
            document_file = bot.get_file(file_id=message.photo[photo_index - 1].file_id)
            document_byte = bot.download_file(file_path=document_file.file_path)
            payment_bot.send_photo(
                chat_id=config.TELEGRAM_ADMIN_ID,
                photo=document_byte,
                caption=caption,
                disable_notification=False,
                parse_mode="html",
            )
        elif message.document:
            document_file = bot.get_file(file_id=message.document.file_id)
            document_byte = bot.download_file(file_path=document_file.file_path)

            payment_bot.send_document(
                chat_id=config.TELEGRAM_ADMIN_ID,
                document=document_byte,
                caption=caption,
                disable_notification=False,
                parse_mode="html",
            )

        bot.send_message(
            message.from_user.id,
            text=messages.GET_PAYMENT_RECEIPT_SUCCESS,
            reply_markup=BotUserKeyboard.main_menu(),
        )

    except Exception as error:
        logger.error(message)
        logger.error(error)
        bot.send_message(
            chat_id=config.TELEGRAM_ADMIN_ID,
            text=f"#Error in forward repayment receipt from "
            + f"{message.from_user.full_name} `{message.from_user.id}`",
            parse_mode="markdown",
        )

        bot.send_message(
            message.from_user.id,
            text=messages.GET_PAYMENT_RECEIPT_ERROR,
            reply_markup=BotUserKeyboard.main_menu(),
        )

        bot.forward_message(
            chat_id=config.TELEGRAM_ADMIN_ID,
            from_chat_id=message.chat.id,
            message_id=message.id,
        )


@bot.message_handler(is_reply=True)
def get_service_name(message: types.Message):
    key = f"{message.reply_to_message.message_id}:{message.chat.id}"
    if key in change_account_name_message_ids:
        db_account = utils.update_account_user_title(
            account_id=change_account_name_message_ids[key], title=message.text
        )

        bot.send_message(
            message.chat.id,
            messages.CHANGE_SERVICE_NAME_SUCCESS,
            reply_markup=BotUserKeyboard.main_menu(),
        )


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("change_service_name:"),
    is_subscribed_user=True,
)
def change_service_name(call: types.CallbackQuery):
    account_id = call.data.split(":")[1]
    message = bot.send_message(
        call.from_user.id,
        messages.PLEASE_ENTER_NEW_SERVICE_NAME,
        reply_markup=ForceReply(),
    )
    change_account_name_message_ids[f"{message.message_id}:{message.chat.id}"] = (
        account_id
    )
    bot.answer_callback_query(callback_query_id=call.id)


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("qrcode:"), is_subscribed_user=True
)
def account_qrcode(call: types.CallbackQuery):
    account_id = call.data.split(":")[1]
    account = utils.get_account(account_id)

    file_name = "./pyqrcode/" + account_id + ".png"

    img = qrcode.make("{}/{}".format(config.SUBSCRIPTION_BASE_URL, account.uuid))
    type(img)  # qrcode.image.pil.PilImage
    img.save(file_name)

    expired_at = (
        "Unlimited"
        if not account.expired_at
        else utils.get_jalali_date(account.expired_at.timestamp())
    )

    bot.send_chat_action(call.from_user.id, "upload_document")
    bot.send_photo(
        caption=captions.ACCOUNT_LIST_ITEM.format(
            utils.get_readable_size_short(account.data_limit),
            expired_at,
            captions.ENABLE if account.enable else captions.DISABLE,
        ),
        chat_id=call.from_user.id,
        photo=open(file_name, "rb"),
    )


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("account_detail:"), is_subscribed_user=True
)
def account_detail(call: types.CallbackQuery):
    telegram_user = call.from_user

    account_id = call.data.split(":")[1]

    account = utils.get_account(account_id)

    percent_traffic_usage = (
        round((account.used_traffic / account.data_limit) * 100, 2)
        if account.data_limit > 0
        else "Unlimited"
    )
    expired_at = (
        "Unlimited"
        if not account.expired_at
        else utils.get_jalali_date(account.expired_at.timestamp())
    )

    db_orders = utils.get_orders(
        account_id=account.id, status=OrderStatus.paid, return_with_count=False
    )

    reserved_service_detail = messages.NO_RESERVED_SERVICE
    has_reserved_service = False

    if db_orders is not None and len(db_orders) > 0:
        has_reserved_service = True
        db_order = db_orders[0]
        if db_order.service_id > 0:
            db_service = utils.get_service(service_id=db_order.service_id)
            if db_service:
                reserved_service_detail = db_service.name

    try:
        bot.edit_message_text(
            message_id=call.message.message_id,
            text=messages.MY_ACCOUNT_MESSAGE.format(
                captions.ENABLE if account.enable else captions.DISABLE,
                account.email,
                account.service_title,
                account.user_title,
                reserved_service_detail,
                expired_at,
                utils.get_readable_size(account.used_traffic),
                utils.get_readable_size(account.data_limit),
                percent_traffic_usage,
                config.SUBSCRIPTION_BASE_URL,
                account.uuid,
            ),
            chat_id=telegram_user.id,
            reply_markup=BotUserKeyboard.my_account(
                account=account, has_reserved_service=has_reserved_service
            ),
            parse_mode="html",
        )
    except ApiTelegramException as error:
        logger.warn(error)
    bot.answer_callback_query(callback_query_id=call.id)


@bot.callback_query_handler(
    func=lambda call: call.data == "user_info", is_subscribed_user=True
)
def restart_command(call: types.CallbackQuery):
    telegram_user = call.from_user

    logger.info(f"Telegram user {telegram_user.full_name} Call {call.data}")

    bot.edit_message_text(
        call.data,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=BotUserKeyboard.main_menu(),
    )
