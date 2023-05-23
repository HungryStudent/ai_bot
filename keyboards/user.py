from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, \
    ReplyKeyboardRemove, WebAppInfo

from utils import db
from utils.pay import get_pay_url
from urllib import parse

withdraw_ref_menu = InlineKeyboardMarkup(row_width=2).add(
    InlineKeyboardButton("На банковскую карту", callback_data='withdraw_ref:bank_card')).add(
    InlineKeyboardButton("QIWI", callback_data="withdraw_ref:qiwi"),
    InlineKeyboardButton("На баланс", callback_data="withdraw_ref:balance")
)

about = InlineKeyboardMarkup(row_width=2).add(InlineKeyboardButton("📢Канал проекта", url="https://t.me/NeuronAgent"),
                                              InlineKeyboardButton("🆘Помощь", url="https://t.me/NeuronSupportBot"))

cancel = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1).add(KeyboardButton("Отмена"))

top_up_balance = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("💰Пополнить баланс", callback_data="top_up_balance"))

partner = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("↗️Перейти и подписаться", url="https://t.me/NeuronAgent"),
    InlineKeyboardButton("✅Я подписался", callback_data="check_sub"))

back_to_choose = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("🔙Назад", callback_data="back_to_choose_balance"))


def get_try_prompt(ai_type):
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton("🔄 Другой вариант", callback_data=f"try_prompt:{ai_type}"))


def get_menu(user_id):
    user = db.get_user(user_id)
    if user["default_ai"] == "chatgpt":
        return ReplyKeyboardMarkup(resize_keyboard=True, row_width=2).add(KeyboardButton("💬Текст✅"),
                                                                          KeyboardButton("🎨Изображение"),
                                                                          KeyboardButton("⚙Аккаунт"),
                                                                          KeyboardButton("👨🏻‍💻Поддержка"),
                                                                          KeyboardButton("🤝Партнерская программа"))
    elif user["default_ai"] == "image":
        return ReplyKeyboardMarkup(resize_keyboard=True, row_width=2).add(KeyboardButton("💬Текст"),
                                                                          KeyboardButton("🎨Изображение✅"),
                                                                          KeyboardButton("⚙Аккаунт"),
                                                                          KeyboardButton("👨🏻‍💻Поддержка"),
                                                                          KeyboardButton("🤝Партнерская программа"))
    else:
        return ReplyKeyboardMarkup(resize_keyboard=True, row_width=2).add(KeyboardButton("💬Текст"),
                                                                          KeyboardButton("🎨Изображение"),
                                                                          KeyboardButton("⚙Аккаунт"),
                                                                          KeyboardButton("👨🏻‍💻Поддержка"),
                                                                          KeyboardButton("🤝Партнерская программа"))


def get_pay(user_id):
    return InlineKeyboardMarkup(row_width=3).add(
        InlineKeyboardButton("200₽", web_app=WebAppInfo(url=get_pay_url(user_id, 200))),
        InlineKeyboardButton("500₽", web_app=WebAppInfo(url=get_pay_url(user_id, 500))),
        InlineKeyboardButton("1000₽", web_app=WebAppInfo(url=get_pay_url(user_id, 1000)))).add(
        InlineKeyboardButton("💰Другая сумма", callback_data="other_amount")).add(
        InlineKeyboardButton("🔙Назад", callback_data="back_to_profile")
    )


def get_other_pay(user_id, amount):
    return InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton("Оплатить", web_app=WebAppInfo(url=get_pay_url(user_id, amount))),
        InlineKeyboardButton("🔙Назад", callback_data="back_to_choose_balance"))


def get_ref_menu(url):
    text_url = parse.quote(url)
    url = f'https://t.me/share/url?url={text_url}'
    return InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton('📩Поделится ссылкой', url=url),
                                                 InlineKeyboardButton('💳Вывод средств',
                                                                      callback_data='withdraw_ref_menu'),
                                                 InlineKeyboardButton('🔙Назад', callback_data='check_sub'))


def get_try_prompt_or_choose(buttonMessageId):
    return InlineKeyboardMarkup(row_width=2).add(
        InlineKeyboardButton("u1", callback_data=f"choose_image:{buttonMessageId}:1"),
        InlineKeyboardButton("u2", callback_data=f"choose_image:{buttonMessageId}:2"),
        InlineKeyboardButton("u3", callback_data=f"choose_image:{buttonMessageId}:3"),
        InlineKeyboardButton("u4", callback_data=f"choose_image:{buttonMessageId}:4"),
        InlineKeyboardButton("🔄 Ещё варианты", callback_data=f"try_prompt:image"))
