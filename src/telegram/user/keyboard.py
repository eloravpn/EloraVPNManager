from telebot import types  # noqa

from src.telegram import utils
from src.telegram.user import captions


class BotUserKeyboard:

    @staticmethod
    def main_menu():
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

        keyboard.add(
            types.InlineKeyboardButton(text=captions.MY_SERVICES)
        )

        keyboard.add(
            types.InlineKeyboardButton(text=captions.BUY_NEW_SERVICE),
            types.InlineKeyboardButton(text=captions.GET_TEST_SERVICE)
        )
        keyboard.add(
            types.InlineKeyboardButton(text=captions.MY_PROFILE),
            types.InlineKeyboardButton(text=captions.PRICE_LIST)
        )

        keyboard.add(
            types.InlineKeyboardButton(text=captions.SUPPORT),
            types.InlineKeyboardButton(text=captions.HELP)
        )
        return keyboard

    @staticmethod
    def channel_menu():
        keyboard = types.InlineKeyboardMarkup(row_width=1)

        keyboard.add(
            types.InlineKeyboardButton(text=captions.CHANNEL, url="https://t.me/+8wKN9itc-QdkMDE0")
        )

        return keyboard

    @staticmethod
    def help_links():
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(
            types.InlineKeyboardButton(
                text='آیفون',
                url="https://t.me/EloraVPNChannel/80"
            ),
            types.InlineKeyboardButton(
                text="اندروید",
                url="https://t.me/EloraVPNChannel/72"
            )
        )

        keyboard.add(
            types.InlineKeyboardButton(
                text='ویندوز',
                url="https://t.me/EloraVPNChannel/90"
            ),
            types.InlineKeyboardButton(
                text="مک بوک",
                url="https://t.me/EloraVPNChannel/93"
            )
        )
        return keyboard

    @staticmethod
    def my_accounts(accounts):
        keyboard = types.InlineKeyboardMarkup()

        for account in accounts:
            expired_at = "Unlimited" if not account.expired_at else utils.get_jalali_date(
                account.expired_at.timestamp())
            keyboard.add(
                types.InlineKeyboardButton(
                    text=captions.ACCOUNT_LIST_ITEM.format(utils.get_readable_size_short(account.data_limit),
                                                           expired_at,
                                                           captions.ENABLE if account.enable else captions.DISABLE),
                    callback_data=f'account_detail:{account.id}'
                )
            )

        return keyboard

    @staticmethod
    def available_services(available_services):
        keyboard = types.InlineKeyboardMarkup(row_width=1)

        name_icon_map = {"basic": "🥉", "standard": "🥈", "pro": "🥇"}
        name_fa_map = {"basic": "پایه", "standard": "استاندارد", "pro": "پرو"}

        for available_service in available_services:
            available_service = available_service.replace("\n", "")
            available_service = available_service.replace("\r", "")
            month = available_service.split(':')[0]
            name = available_service.split(':')[1]

            traffic = available_service.split(':')[2]
            price = available_service.split(':')[3]
            keyboard.add(
                types.InlineKeyboardButton(
                    text=captions.SERVICE_LIST_ITEM.format(month, name_fa_map[name], traffic, name_icon_map[name]),
                    callback_data=f'buy_service_step_1:{month}:{name}:{traffic}:{price}'
                )
            )

        return keyboard

    @staticmethod
    def my_account(account_id):
        keyboard = types.InlineKeyboardMarkup()

        keyboard.add(
            types.InlineKeyboardButton(
                text="دریافت QR کد",
                callback_data=f"qrcode:{account_id}"
            ),
            types.InlineKeyboardButton(
                text="🔄 بروزرسانی",
                callback_data=f"account_detail:{account_id}"
            )
        )

        return keyboard

    @staticmethod
    def buy_service_step_1(data: str):
        keyboard = types.InlineKeyboardMarkup()

        month = data.split(':')[1]
        name = data.split(':')[2]
        traffic = data.split(':')[3]
        price = data.split(':')[4]

        keyboard.add(

            types.InlineKeyboardButton(

                text="❌ انصراف",
                callback_data=f"main_menu:"
            ),
            types.InlineKeyboardButton(
                text="✅ بله",
                callback_data=f"buy_service_step_2:{month}:{name}:{traffic}:{price}"
            )

        )

        return keyboard

    @staticmethod
    def buy_service_step_2(data: str):
        keyboard = types.InlineKeyboardMarkup()

        month = data.split(':')[1]
        name = data.split(':')[2]
        traffic = data.split(':')[3]
        price = data.split(':')[4]

        keyboard.add(

            types.InlineKeyboardButton(
                text="💳 پرداخت آنلاین",
                callback_data=f"online_payment:"
            )

        )

        return keyboard
