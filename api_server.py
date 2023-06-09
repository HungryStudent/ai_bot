from aiogram.utils.exceptions import ChatNotFound
from keyboards import user as user_kb
from fastapi import FastAPI, Request
from create_bot import bot
from io import BytesIO
from utils import db
import requests
import uvicorn

app = FastAPI()


@app.get('/api/pay/freekassa')
async def check_pay_freekassa(MERCHANT_ORDER_ID, AMOUNT):
    await db.add_balance(int(MERCHANT_ORDER_ID), int(AMOUNT))
    try:
        await bot.send_message(int(MERCHANT_ORDER_ID), "💰Баланс успешно пополнен!")
    except ChatNotFound:
        pass
    except Exception as e:
        await bot.send_message(796644977, e)
    return 'YES'


@app.post('/api/midjourney')
async def get_midjourney(request: Request):
    data = await request.json()
    photo_url = data["imageUrl"]
    if photo_url == '':
        await bot.send_message(796644977, data)
    response = requests.get(photo_url)
    img = BytesIO(response.content)
    user_id = int(data["ref"])
    user = await db.get_user(user_id)
    await bot.send_photo(user["user_id"], photo=img,
                         reply_markup=user_kb.get_try_prompt_or_choose(data["buttonMessageId"], "main"))
    if user["free_image"] > 0:
        await db.remove_image(user["user_id"])
    else:
        await db.remove_balance(user["user_id"])
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
        await db.remove_balance(user_id)
    await db.add_action(user_id, "image")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
