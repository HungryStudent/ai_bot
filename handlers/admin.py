import asyncio

from aiogram.types import Message, CallbackQuery, MediaGroup
from aiogram.dispatcher import FSMContext

from config import admin_chat
from create_bot import dp, bot
import keyboards.admin as admin_kb
import states.admin as states
from utils import db

import datetime


@dp.message_handler(chat_id=admin_chat, commands="stats")
async def show_stats(message: Message):
    stats_data = db.get_stat()
    await message.answer(f"""Количество пользователей: {stats_data['users_count']}
За сегодня: {stats_data['today_users_count']}

Запросов {stats_data['chatgpt_count'] + stats_data['image_count']}
Текст - {stats_data['chatgpt_count']}
Изображение - {stats_data['image_count']}

За сегодня {stats_data['today_chatgpt_count'] + stats_data['today_image_count']}
Текст - {stats_data['today_chatgpt_count']}
Изображение - {stats_data['today_image_count']}

Пополнений: {stats_data['orders_count']} ({stats_data['orders_sum']} руб.)
За сегодня: {stats_data['today_orders_count']} ({stats_data['today_orders_sum']} руб.)""")


@dp.message_handler(commands="balance")
async def add_balance(message: Message):
    try:
        user_id, value = message.get_args().split(" ")
    except ValueError:
        await message.answer("Команда введена неверно. Используйте /balance {id пользователя} {баланс}")
        return
    db.add_balance_from_admin(user_id, value)


@dp.message_handler(commands="send", user_id=admin_chat)
async def enter_text(message: Message):
    await message.answer("Введите текст рассылки", reply_markup=admin_kb.cancel)
    await states.Mailing.enter_text.set()


@dp.message_handler(state=states.Mailing.enter_text, user_id=admin_chat)
async def start_send(message: Message, state: FSMContext):
    await message.answer("Начал рассылку")
    await state.finish()
    users = db.get_users()
    count = 0
    block_count = 0
    for user in users:
        try:
            await message.bot.send_message(user["user_id"], message.text)
            count += 1
        except:
            block_count += 1
        await asyncio.sleep(0.1)
    await message.answer(
        f"Количество получивших сообщение: {count}. Пользователей, заблокировавших бота: {block_count}")
