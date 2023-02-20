from aiogram.utils.exceptions import ChatNotFound
from fastapi import FastAPI, Request, HTTPException

from keyboards import admin as admin_kb
from keyboards import user as user_kb
from create_bot import bot

import uvicorn

from utils import db

app = FastAPI()


@app.get('/api/pay/freekassa')
async def check_pay_freekassa(MERCHANT_ORDER_ID, AMOUNT):
    db.add_balance(MERCHANT_ORDER_ID, AMOUNT)
    try:
        await bot.send_message(MERCHANT_ORDER_ID, "💰Баланс успешно пополнен!")
    except ChatNotFound:
        pass
    except Exception as e:
        await bot.send_message(796644977, e)
    return 'YES'


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
