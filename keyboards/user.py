from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, \
    ReplyKeyboardRemove
from aiogram.utils.callback_data import CallbackData

from utils.pay import get_pay_url

menu = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2).add(KeyboardButton("Задать вопрос"),
                                                                  KeyboardButton("Сгенерировать изображение"),
                                                                  KeyboardButton("Поддержка"))

cancel = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1).add(KeyboardButton("Отмена"))


def get_pay(user_id):
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton("10 запросов - 100 рублей", url=get_pay_url(user_id)))
