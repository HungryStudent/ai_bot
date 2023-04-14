from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

cancel = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1).add(KeyboardButton("Отмена"))