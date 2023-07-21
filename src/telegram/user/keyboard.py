from telebot import types  # noqa


class BotUserKeyboard:

    @staticmethod
    def main_menu():
        keyboard = types.InlineKeyboardMarkup()

        keyboard.add(
            types.InlineKeyboardButton(text='مشاهده پروفایل کاربری', callback_data='user_info'),
            types.InlineKeyboardButton(text='♻️ ری استارت', callback_data='restart'),
        )
        keyboard.add(
            types.InlineKeyboardButton(text='👥 Users', callback_data='users:1')
        )
        keyboard.add(
            types.InlineKeyboardButton(text='➕ Create User', callback_data='add_user')
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
                text='No',
                callback_data=f"cancel"
            )
        )
        return keyboard
