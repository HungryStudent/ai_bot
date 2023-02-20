from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, \
    ReplyKeyboardRemove
from aiogram.utils.callback_data import CallbackData

from utils.pay import get_pay_url

menu = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2).add(KeyboardButton("💬Текст"),
                                                                  KeyboardButton("🎨Изображение"),
                                                                  KeyboardButton("⚙Аккаунт"),
                                                                  KeyboardButton("👨🏻‍💻Поддержка"))

about = InlineKeyboardMarkup(row_width=2).add(InlineKeyboardButton("📢Канал проекта", url="https://t.me/NeuronAgent"),
                                              InlineKeyboardButton("🆘Помощь", url="https://t.me/NeuronSupportBot"))

cancel = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1).add(KeyboardButton("Отмена"))

top_up_balance = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("💰Пополнить баланс", callback_data="top_up_balance"))

partner = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton("Подписаться", url="https://t.me/NeuronAgent"),
                                                InlineKeyboardButton("Я подписался", callback_data="check_sub"))


def get_pay(user_id):
    return InlineKeyboardMarkup(row_width=3).add(
        InlineKeyboardButton("200₽", url=get_pay_url(user_id, 200)),
        InlineKeyboardButton("500₽", url=get_pay_url(user_id, 500)),
        InlineKeyboardButton("1000₽", url=get_pay_url(user_id, 1000))).add(
        InlineKeyboardButton("💰Другая сумма", callback_data="other_amount")).add(
        InlineKeyboardButton("🔙Назад", callback_data="back_to_profile")
    )


def get_other_pay(user_id, amount):
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton("200₽", url=get_pay_url(user_id, amount)))
