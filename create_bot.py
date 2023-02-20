from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher

from config import TOKEN, log_on
from aiogram import Bot
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