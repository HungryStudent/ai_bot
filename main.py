from io import BytesIO

import requests
from aiogram.utils import executor
from create_bot import dp, bot
from middlewares.check_sub import CheckRegMiddleware
from utils import db
from handlers import admin
from handlers import users


async def on_startup(_):
    db.start()


if __name__ == "__main__":
    dp.middleware.setup(CheckRegMiddleware())
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
