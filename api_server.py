from datetime import datetime

from aiogram.utils.exceptions import ChatNotFound

from config import LAVA_WEBHOOK_KEY, NOTIFY_URL, bug_id
from handlers.users import remove_balance
from keyboards import user as user_kb
from fastapi import FastAPI, Request, Header, HTTPException
from pydantic import BaseModel
from create_bot import bot
from io import BytesIO
from utils import db
import requests
import uvicorn

app = FastAPI()


class LavaWebhook(BaseModel):
    order_id: str
    status: str
    amount: float


async def add_balance(user_id, amount):
    user = await db.get_user(user_id)
    stock = 0
    if not user["is_pay"] and int(datetime.now().timestamp()) - user["new_stock_time"] < 86400:
        stock = int(amount * 0.3)
        await db.update_new_stock_time(user_id, 0)
    elif int(datetime.now().timestamp()) - user["stock_time"] < 86400:
        stock = int(amount * 0.1)
        await db.update_stock_time(user_id, 0)
    requests.delete(NOTIFY_URL + f"/stock/{user_id}")
    await db.update_is_pay(user_id, True)
    await db.add_balance(user_id, amount + stock)
    await db.add_order(user_id, amount, stock)
    await bot.send_message(user_id, f"💰 Успешное пополнение ({amount + stock} руб.)")


@app.get('/api/pay/freekassa')
async def check_pay_freekassa(MERCHANT_ORDER_ID, AMOUNT):
    await add_balance(int(MERCHANT_ORDER_ID), int(AMOUNT))
    return 'YES'


@app.post('/api/pay/lava')
async def check_pay_freekassa(data: LavaWebhook):
    if data.status != "success":
        raise HTTPException(200)
    user_id = int(data.order_id.split(":")[0])
    await add_balance(user_id, int(data.amount))
    raise HTTPException(200)


@app.post('/api/midjourney')
async def get_midjourney(request: Request):
    data = await request.json()
    photo_url = data["imageUrl"]
    user_id = int(data["ref"])
    user = await db.get_user(user_id)
    send_error_msg = False
    if photo_url == '':
        if "content" in data:
            if data["content"] == "Request cancelled due to image filters":
                await bot.send_message(user["user_id"], "Данное фото не прошло фильтры, попробуйте другое")
                send_error_msg = True
        if not send_error_msg:
            await bot.send_message(bug_id, data)
        return
    response = requests.get(photo_url)
    img = BytesIO(response.content)
    await bot.send_photo(user["user_id"], photo=img,
                         reply_markup=user_kb.get_try_prompt_or_choose(data["buttonMessageId"], "main"))
    if user["free_image"] > 0:
        await db.remove_image(user["user_id"])
    else:
        await remove_balance(bot, user["user_id"])
    await db.add_action(user["user_id"], "image")


@app.post('/api/midjourney/choose')
async def get_midjourney(request: Request):
    data = await request.json()
    user_id = int(data["ref"])
    photo_url = data["imageUrl"]
    await bot.send_photo(user_id, photo_url)


@app.post('/api/midjourney_reserve')
async def get_midjourney(user_id: int, request: Request):
    data = await request.json()
    if "imageURL" not in data:
        return
    elif "status" in data:
        if data["status"] == "midjourney-blocked-by-ai-moderation":
            await bot.send_message(user_id, "В запросе есть запрещённое слово. Попробуйте другой запрос")
        elif data["status"] in ["waiting-to-start", "running"]:
            pass
        elif data["status"] == "midjourney-bad-request-other":
            await bot.send_message(user_id, "Произошла ошибка, повторите запрос")
        else:
            pass
        return
    elif "imageURL" not in data:
        return
    photo_url = data["imageURL"]
    response = requests.get(photo_url)
    img = BytesIO(response.content)

    user = await db.get_user(user_id)
    await bot.send_photo(user_id, photo=img,
                         reply_markup=user_kb.get_try_prompt_or_choose(user["task_id"], "reserve"))
    if user["free_image"] > 0:
        await db.remove_image(user_id)
    else:
        await remove_balance(bot, user_id)
    await db.add_action(user_id, "image")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
