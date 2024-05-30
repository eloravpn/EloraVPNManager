from telebot import types  # noqa

from src.accounts.models import Account
from src.telegram import utils
from src.telegram.user import captions


class BotUserKeyboard:
    @staticmethod
    def main_menu():
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

        keyboard.add(
            types.InlineKeyboardButton(text=captions.MY_SERVICES),
            types.InlineKeyboardButton(text=captions.GET_TEST_SERVICE),
        )

        keyboard.add(
            types.InlineKeyboardButton(text=captions.BUY_NEW_SERVICE),
            types.InlineKeyboardButton(text=captions.PAYMENT),
        )
        keyboard.add(
            types.InlineKeyboardButton(text=captions.MY_PROFILE),
            types.InlineKeyboardButton(text=captions.PRICE_LIST),
        )

        keyboard.add(
            types.InlineKeyboardButton(text=captions.SUPPORT),
            types.InlineKeyboardButton(text=captions.HELP),
        )
        return keyboard

    @staticmethod
    def channel_menu():
        keyboard = types.InlineKeyboardMarkup(row_width=1)

        keyboard.add(
            types.InlineKeyboardButton(
                text=captions.CHANNEL, url="https://t.me/+8wKN9itc-QdkMDE0"
            ),
            types.InlineKeyboardButton(
                text=captions.I_HAVE_SUBSCRIBED, callback_data="main_menu:"
            ),
        )

        return keyboard

    @staticmethod
    def help_links():
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(
            types.InlineKeyboardButton(
                text="آیفون", url="https://t.me/EloraVPNChannel/210"
            ),
            types.InlineKeyboardButton(
                text="اندروید", url="https://t.me/EloraVPNChannel/72"
            ),
        )

        keyboard.add(
            types.InlineKeyboardButton(
                text="ویندوز", url="https://t.me/EloraVPNChannel/90"
            ),
            types.InlineKeyboardButton(
                text="مک بوک", url="https://t.me/EloraVPNChannel/93"
            ),
        )
        return keyboard

    @staticmethod
    def my_accounts(accounts):
        keyboard = types.InlineKeyboardMarkup()

        for account in accounts:

            expired_at = (
                "Unlimited"
                if not account.expired_at
                else utils.get_jalali_date(account.expired_at.timestamp())
            )

            data_limit = (
                utils.get_readable_size_short(account.data_limit)
                if account.data_limit > 0
                else "Unlimited"
            )

            service_name = captions.ACCOUNT_LIST_ITEM.format(
                data_limit,
                expired_at,
                captions.ENABLE if account.enable else captions.DISABLE,
            )

            if account.user_title:
                service_name = f"{account.user_title} [{data_limit}]"
            keyboard.add(
                types.InlineKeyboardButton(
                    text=service_name,
                    callback_data=f"account_detail:{account.id}",
                )
            )

        return keyboard

    @staticmethod
    def available_services(available_services, account_id: int = 0):
        keyboard = types.InlineKeyboardMarkup(row_width=1)

        for available_service in available_services:
            discount = ""
            if available_service.discount_percent > 0:
                discount = f"({available_service.discount_percent}%)"

            price_readable_plain = ""
            if available_service.price_readable_plain:
                price_readable_plain = (
                    " " + available_service.price_readable_plain + " تومان "
                )

            name = available_service.name + price_readable_plain + discount

            keyboard.add(
                types.InlineKeyboardButton(
                    text=name,
                    callback_data=f"buy_service_step_1:{available_service.id}:{account_id}",
                )
            )

        return keyboard

    @staticmethod
    def my_account(account: Account):
        keyboard = types.InlineKeyboardMarkup()

        keyboard.add(
            types.InlineKeyboardButton(
                text="دریافت QR کد", callback_data=f"qrcode:{account.id}"
            ),
            types.InlineKeyboardButton(
                text="🔄 بروزرسانی", callback_data=f"account_detail:{account.id}"
            ),
            types.InlineKeyboardButton(
                text="✏️ تغییر نام", callback_data=f"change_service_name:{account.id}"
            ),
        )

        if not account.is_test:
            keyboard.add(
                types.InlineKeyboardButton(
                    text="🛍 تمدید سرویس",
                    callback_data=f"recharge_service_1:{account.id}",
                )
            )

        return keyboard

    @staticmethod
    def buy_service_step_1(service_id: int, account_id: int = 0):
        keyboard = types.InlineKeyboardMarkup()

        keyboard.add(
            types.InlineKeyboardButton(text="❌ انصراف", callback_data=f"main_menu:"),
            types.InlineKeyboardButton(
                text="✅ تایید و ادامه",
                callback_data=f"buy_service_step_2:{service_id}:{account_id}",
            ),
        )

        return keyboard

    @staticmethod
    def buy_service_step_2(data: str):
        keyboard = types.InlineKeyboardMarkup()

        keyboard.add(
            types.InlineKeyboardButton(
                text="💳 پرداخت آنلاین", callback_data=f"online_payment:"
            )
        )

        return keyboard

    @staticmethod
    def payment_card_step_1(account_id: int):
        keyboard = types.InlineKeyboardMarkup()

        keyboard.add(
            types.InlineKeyboardButton(
                text="💳 ارسال رسید پرداختی",
                callback_data=f"get_payment_receipt:{account_id}",
            )
        )

        return keyboard
