import asyncio
from datetime import datetime
from typing import Annotated

from config import NOTIFY_URL, bug_id
from handlers.users import remove_balance
from keyboards import user as user_kb
from fastapi import FastAPI, Request, HTTPException, Form
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


class PayOKWebhook(BaseModel):
    payment_id: str
    amount: float


async def send_mj_photo(user_id, photo_url, kb):
    try:
        response = requests.get(photo_url, timeout=5)
    except requests.exceptions.Timeout:
        img = photo_url
    except requests.exceptions.ConnectionError:
        img = photo_url
    else:
        img = BytesIO(response.content)
    await bot.send_photo(user_id, photo=img,
                         reply_markup=kb)


async def add_balance(user_id, amount):
    user = await db.get_user(user_id)
    if user is None:
        return
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


@app.post('/api/pay/payok')
async def check_pay_freekassa(payment_id: Annotated[str, Form()], amount: Annotated[str, Form()]):
    user_id = int(payment_id.split("_")[0])
    await add_balance(user_id, int(amount))
    raise HTTPException(200)


@app.post('/api/midjourney')
async def get_midjourney(request: Request):
    data = await request.json()
    photo_url = data["imageUrl"]
    action_id = int(data["ref"])
    action = await db.get_action(action_id)
    user_id = action["user_id"]
    user = await db.get_user(user_id)
    send_error_msg = False
    if photo_url == '':
        msg_text = "Произошла ошибка, повторите попытку позже"
        if "content" in data:
            send_error_msg = True
            if data["content"] == "Request cancelled due to image filters" or data["content"] == "IMAGE_BLOCKED":
                await bot.send_message(user["user_id"], "Данное фото не прошло фильтры, попробуйте другое")
            elif data["content"] == "INVALID_PARAMETER":
                await bot.send_message(user["user_id"], "Произошла ошибка, повторите попытку позже")
            elif data["content"] == "Credits exhausted":
                await bot.send_message(user["user_id"], "Произошла ошибка, повторите попытку позже")
            elif data["content"] == "BANNED_PROMPT":
                await bot.send_message(user["user_id"], "Ваш запрос не прошел фильтры, попробуйте другой")
            elif data["content"] == "FAILED_TO_PROCESS_YOUR_COMMAND":
                pass
            else:
                send_error_msg = False
        if not send_error_msg:
            await bot.send_message(bug_id, data)
            await bot.send_message(user_id, "Произошла ошибка, повторите попытку позже")
        return
    await send_mj_photo(user_id, photo_url, user_kb.get_try_prompt_or_choose(data["buttonMessageId"], "main",
                                                                             include_try=True))
    await db.set_action_get_response(action_id)
    if user["free_image"] > 0:
        await db.remove_image(user["user_id"])
    else:
        await remove_balance(bot, user["user_id"])


@app.post('/api/midjourney/choose')
async def get_midjourney_choose(request: Request):
    data = await request.json()
    action_id = int(data["ref"])
    action = await db.get_action(action_id)
    user_id = action["user_id"]
    photo_url = data["imageUrl"]
    await send_mj_photo(user_id, photo_url, user_kb.get_choose(data["buttonMessageId"]))
    await db.set_action_get_response(action_id)
    await remove_balance(bot, user_id)


@app.post('/api/midjourney/button')
async def get_midjourney_button(request: Request):
    await asyncio.sleep(1)
    data = await request.json()
    action_id = int(data["ref"])
    action = await db.get_action(action_id)
    user_id = action["user_id"]
    photo_url = data["imageUrl"]
    await send_mj_photo(user_id, photo_url, user_kb.get_try_prompt_or_choose(data["buttonMessageId"], "main"))
    user = await db.get_user(user_id)
    await db.set_action_get_response(action_id)
    if user["free_image"] > 0:
        await db.remove_image(user["user_id"])
    else:
        await remove_balance(bot, user["user_id"])


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
                         reply_markup=user_kb.get_try_prompt_or_choose(user["task_id"], "reserve", include_try=True))
    if user["free_image"] > 0:
        await db.remove_image(user_id)
    else:
        await remove_balance(bot, user_id)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
