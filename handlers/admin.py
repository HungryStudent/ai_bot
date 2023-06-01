from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext

import keyboards.admin as admin_kb
from create_bot import dp, bot
from config import admin_chat
from tabulate import tabulate
import states.admin as states
from utils import db
import asyncio


@dp.message_handler(chat_id=admin_chat, commands="stats")
async def show_stats(message: Message):
    stats_data = await db.get_stat()
    await message.answer(f"""Количество пользователей: {stats_data['users_count']}
За сегодня: {stats_data['today_users_count']}

Запросов {stats_data['chatgpt_count'] + stats_data['image_count']}
Текст - {stats_data['chatgpt_count']}
Изображение - {stats_data['image_count']}

За сегодня {stats_data['today_chatgpt_count'] + stats_data['today_image_count']}
Текст - {stats_data['today_chatgpt_count']}
Изображение - {stats_data['today_image_count']}

Пополнений: {stats_data['orders_count']}
Повторные оплаты: {stats_data['repeated_orders_count']}
Пополнений за сегодня: {stats_data['today_orders_count']} ({stats_data['today_orders_sum']} руб.)""",
                         reply_markup=admin_kb.ref_menu)


@dp.callback_query_handler(text='admin_ref_menu')
async def admin_ref_menu(call: CallbackQuery):
    inviters_id = await db.get_all_inviters()
    inviters = []
    for inviter_id in inviters_id:
        inviter = await db.get_ref_stat(inviter_id['inviter_id'])
        if inviter['all_income'] is None:
            inviter['all_income'] = 0

        inviters.append(
            {'user_id': inviter_id['inviter_id'], 'refs_count': inviter['count_refs'],
             'orders_count': inviter['orders_count'],
             'all_income': inviter['all_income'], 'available_for_withdrawal': inviter['available_for_withdrawal']})
    sort_inviters = sorted(inviters, key=lambda d: d['all_income'], reverse=True)
    await call.message.answer(
        f'<b>Партнерская статистика</b>\n\n<pre>{tabulate(sort_inviters, tablefmt="jira", numalign="left")}</pre>')
    await call.answer()


@dp.message_handler(commands="balance", user_id=admin_chat)
async def add_balance(message: Message):
    try:
        user_id, value = message.get_args().split(" ")
    except ValueError:
        await message.answer("Команда введена неверно. Используйте /balance {id пользователя} {баланс}")
        return
    await db.add_balance_from_admin(user_id, value)
    await message.answer('Баланс изменён')


@dp.message_handler(commands="send", user_id=admin_chat)
async def enter_text(message: Message):
    await message.answer("Введите текст рассылки", reply_markup=admin_kb.cancel)
    await states.Mailing.enter_text.set()


@dp.message_handler(state=states.Mailing.enter_text, user_id=admin_chat)
async def start_send(message: Message, state: FSMContext):
    await message.answer("Начал рассылку")
    await state.finish()
    users = await db.get_users()
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
