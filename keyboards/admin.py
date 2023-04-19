from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, \
    InlineKeyboardButton

cancel = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1).add(KeyboardButton("Отмена"))

ref_menu = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton('Партнерская программа', callback_data='admin_ref_menu'))
