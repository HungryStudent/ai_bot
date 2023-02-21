from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import Update, ChatMember
from aiogram.utils.exceptions import ChatNotFound

from keyboards import user as user_kb
from config import admin_chat, channel_id
from create_bot import bot


class CheckRegMiddleware(BaseMiddleware):
    async def on_pre_process_update(self, update: Update, data: dict):
        return
        if update.message:
            user_id = update.message.from_user.id
        elif update.callback_query:
            user_id = update.callback_query.from_user.id
        else:
            return
        if update.message and '/start' in update.message.text:
            return
        try:
            status: ChatMember = await bot.get_chat_member(channel_id, user_id)
            if status.status == "left":
                if update.callback_query:
                    await update.callback_query.answer("Необходимо вступить в канал")
                else:
                    await bot.send_message(user_id, "Для продолжения подпишитесь на наш канал",
                                           reply_markup=user_kb.partner)

                raise CancelHandler()
        except ChatNotFound as e:
            print(e)
            await bot.send_message(admin_chat, "Проблема с каналом партнером")
