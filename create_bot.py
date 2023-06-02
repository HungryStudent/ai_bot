from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import BoundFilter
from aiogram.dispatcher import Dispatcher
from aiogram import types
from aiogram import Bot

from config import TOKEN, log_on
from config import ADMINS
from typing import Union
from utils import db
import logging

if log_on:
    logging.basicConfig(level=logging.INFO, filename='bot.log', filemode='a',
                        format='%(asctime)s - %(levelname)s - %(message)s')
    log = logging.getLogger("logs")
else:
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    log = logging.getLogger("logs")

stor = MemoryStorage()
bot = Bot(token=TOKEN, parse_mode="HTML")
dp = Dispatcher(bot, storage=stor)


class IsAdminFilter(BoundFilter):
    key = "is_admin"

    def __init__(self, is_admin: bool):
        self.global_admin = is_admin

    async def check(self, obj: Union[types.Message, types.CallbackQuery]):
        user = obj.from_user
        db_user = await db.get_user(user.id)
        if user.id in ADMINS:
            return self.global_admin is True
        if db_user["role"] == "admin":
            return self.global_admin is True
        return self.global_admin is False


dp.filters_factory.bind(IsAdminFilter)
