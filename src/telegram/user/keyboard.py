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
        keyboard = types.InlineKeyboardMarkup(resize_keyboard=True)

        keyboard.add(
            types.InlineKeyboardButton(text=captions.CHANNEL, url="https://t.me/+8wKN9itc-QdkMDE0")
        )

        return keyboard

    @staticmethod
    def confirm_action(action: str, username: str = None):
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(
            types.InlineKeyboardButton(
                text='Yes',
                callback_data=f"confirm:{action}:{username}"
            ),
            types.InlineKeyboardButton(
                text="Hi", url="https://t.me/EloraVPNChannel/72"
            )
        )
        return keyboard

    @staticmethod
    def my_accounts(accounts):
        keyboard = types.InlineKeyboardMarkup()
        for account in accounts:
            print(account.expired_at)
            keyboard.add(
                types.InlineKeyboardButton(
                    text=captions.ACCOUNT_LIST_ITEM.format(utils.get_readable_size_short(account.data_limit),
                                                           utils.get_jalali_date(account.expired_at.timestamp()),
                                                           captions.ENABLE if account.enable else captions.DISABLE),
                    callback_data="{action:user}"

                )
            )

        return keyboard
