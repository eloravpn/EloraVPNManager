from typing import List

from pydantic import BaseModel

from telebot import types


class Keyboard(BaseModel):
    text: str
    callback_data: str = None
    url: str = None

    def to_json(self):
        return {"text": self.text, "callback_data": self.callback_data, "url": self.url}


class KeyboardFactory:
    @staticmethod
    def from_keyboard(keyboards: List[Keyboard]):
        json_keyboards = []
        for keyboard in keyboards:
            json_keyboards.append(keyboard.to_json())

        return json_keyboards

    @staticmethod
    def from_json_string(keyboards_dict: str) -> types.ReplyKeyboardMarkup:

        keyboards = []
        for keyboard_dict in keyboards_dict:
            keyboards.append(
                types.InlineKeyboardButton(
                    text=keyboard_dict["text"],
                    url=keyboard_dict["url"],
                    callback_data=keyboard_dict["callback_data"],
                )
            )

        return types.InlineKeyboardMarkup([keyboards])
