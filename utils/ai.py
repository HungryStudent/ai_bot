import aiohttp
import requests
from aiogram import Bot
from midjourney_api import TNL
from googletranslatepy import Translator

import change_token
from config import OPENAPI_TOKEN, ya_folder, midjourney_webhook_url, MJ_API_KEY, TNL_API_KEY, TOKEN
from utils import db

tnl = TNL(TNL_API_KEY)


async def send_error(text):
    my_bot = Bot(TOKEN)
    await my_bot.send_message(796644977, text)


async def reserve_mj(prompt, user_id):
    headers = {
        'Authorization': MJ_API_KEY,
        'Content-Type': 'application/json'
    }
    payload = {
        "callbackURL": midjourney_webhook_url + "_reserve" + f"?user_id={user_id}",
        "prompt": prompt
    }
    res = requests.post("https://api.midjourneyapi.io/v2/imagine", headers=headers, json=payload)
    data = res.json()
    return_data = {}
    if "errors" in data:
        return_data["error"] = {}
        if "Prompt contains banned word" in data["errors"][0]["msg"]:
            return_data["error"]["type"] = "banned word error"
    else:
        return_data["task_id"] = data["taskId"]
    return return_data


async def get_translate(text):
    translator = Translator(target="en")
    translate = translator.translate(text)
    return translate


async def get_gpt(prompt, lang):
    lang_text = {"en": "compose an answer in English", "ru": "составь ответ на русском языке"}
    prompt += f"\n{lang_text[lang]}"
    async with aiohttp.ClientSession() as session:
        async with session.post('https://api.openai.com/v1/completions',
                                headers={'Authorization': f'Bearer {OPENAPI_TOKEN}',
                                         'Content-Type': 'application/json'},
                                json={'model': 'text-davinci-003',
                                      "prompt": prompt,
                                      "max_tokens": 1024,
                                      "temperature": 0.5,
                                      "top_p": 1,
                                      "frequency_penalty": 0,
                                      "presence_penalty": 0
                                      }) as resp:
            response = await resp.json()
            try:
                return response["choices"][0]["text"]
            except KeyError:
                await send_error(response["error"]["message"])
                print(f"Ошибка {response}")
                if "That model is currently overloaded with other requests" in response["error"]["message"]:
                    return "Модель ChatGPT сейчас перегружена запросами, повторите запрос позже."
                return "Генерация текста в данный момент недоступна, попробуйте чуть позже"


async def get_mdjrny(prompt, user_id):
    translated_prompt = await get_translate(prompt)
    try:
        res = tnl.imagine(translated_prompt, webhook_override=midjourney_webhook_url, ref=user_id)
        if "success" not in res or not res["success"]:
            await send_error(res)
            res = await reserve_mj(translated_prompt, user_id)
            mj_api = "reserve"
            status = True
        else:
            mj_api = "main"
            status = True
    except requests.exceptions.JSONDecodeError:
        res = await reserve_mj(translated_prompt, user_id)
        mj_api = "reserve"
        status = True

    error = None
    task_id = None
    if mj_api == "reserve":
        if "error" in res:
            error = res["error"]
        else:
            task_id = res["task_id"]

    return {"status": status, "mj_api": mj_api, "error": error, "task_id": task_id}
    #
    # headers = {
    #     'Authorization': MJ_API_KEY,
    #     'Content-Type': 'application/json'
    # }
    # payload = {
    #     "callbackURL": midjourney_webhook_url + f"?user_id={user_id}",
    #     "prompt": translated_prompt
    # }
    # res = requests.post("https://api.midjourneyapi.io/v2/imagine", headers=headers, json=payload)
    # data = res.json()
    # if "errors" in data:
    #     if "Prompt contains banned word" in data["errors"][0]["msg"]:
    #         return "banned word error"
    # return data["taskId"]


async def get_choose_mdjrny(buttonMessageId, image_id, user_id, mj_api):
    if mj_api == "main":
        try:
            res = tnl.button(f"U{image_id}", buttonMessageId, ref=user_id,
                             webhook_override=midjourney_webhook_url + "/choose")
            return {"status": True}
        except requests.exceptions.JSONDecodeError:
            return {"status": True}
    elif mj_api == "reserve":
        headers = {
            'Authorization': MJ_API_KEY,
            'Content-Type': 'application/json'
        }
        payload = {
            "taskId": buttonMessageId,
            "position": image_id
        }
        res = requests.post("https://api.midjourneyapi.io/v2/upscale", headers=headers, json=payload)
        data = res.json()
        if "errors" in data:
            pass
            return {"status": False, "error": {}}

        return {"status": True, "image_url": data["imageURL"]}
    #
    # headers = {
    #     'Authorization': MJ_API_KEY,
    #     'Content-Type': 'application/json'
    # }
    # payload = {
    #     "taskId": buttonMessageId,
    #     "position": image_id
    # }
    # res = requests.post("https://api.midjourneyapi.io/v2/upscale", headers=headers, json=payload)
    # data = res.json()
    # if "errors" in data:
    #     pass
    # return data["imageURL"]
