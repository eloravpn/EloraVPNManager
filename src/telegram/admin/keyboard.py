from telebot import types  # noqa

from src.telegram.admin import captions


class BotAdminKeyboard:
    @staticmethod
    def main_menu():
        keyboard = types.InlineKeyboardMarkup()

        keyboard.add(
            types.InlineKeyboardButton(
                text=captions.ACCOUNT_USAGE_REPORTS,
                callback_data="report_account_usage",
            ),
            types.InlineKeyboardButton(
                text=captions.ACCOUNT_USAGE_DETAIL,
                callback_data="account_usage_detail",
            ),
            # types.InlineKeyboardButton(text=captions.GET_TEST_SERVICE),
        )

        keyboard.add(
            types.InlineKeyboardButton(
                text=captions.ORDERS_REPORTS, callback_data="report_orders"
            ),
            types.InlineKeyboardButton(
                text=captions.TRANSACTION_REPORTS, callback_data="report_transaction"
            ),
        )
        # keyboard.add(
        #     types.InlineKeyboardButton(text=captions.MY_PROFILE),
        #     types.InlineKeyboardButton(text=captions.PRICE_LIST),
        # )
        #
        # keyboard.add(
        #     types.InlineKeyboardButton(text=captions.SUPPORT),
        #     types.InlineKeyboardButton(text=captions.HELP),
        # )
        return keyboard
