from aiogram.utils.exceptions import ChatNotFound
from fastapi import FastAPI, Request

from create_bot import bot

import uvicorn
from keyboards import user as user_kb

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


@app.post('/api/midjourney')
async def get_midjourney(request: Request):
    data = await request.json()
    photo_url = data["imageUrl"]
    ds_msg_id = data["originatingMessageId"]
    user = db.get_user_by_ds_msg_id(ds_msg_id)
    await bot.send_photo(user["user_id"], photo_url, reply_markup=user_kb.get_try_prompt('image'))
    if user["free_image"] > 0:
        db.remove_image(user["user_id"])
    else:
        db.remove_balance(user["user_id"])
    db.add_action(user["user_id"], "image")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
