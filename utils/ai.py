import aiohttp
import requests
from midjourney_api import TNL

import change_token
from config import OPENAPI_TOKEN, ya_folder, midjourney_webhook_url, MJ_API_KEY, TNL_API_KEY
from create_bot import bot
from utils import db

tnl = TNL(TNL_API_KEY)


async def get_translate(text):
    iam_token = await db.get_iam_token()
    async with aiohttp.ClientSession() as session:
        async with session.post('https://translate.api.cloud.yandex.net/translate/v2/translate',
                                headers={'Authorization': f'Bearer {iam_token}',
                                         'Content-Type': 'application/json'},
                                json={
                                    "folderId": ya_folder,
                                    "texts": [text],
                                    "targetLanguageCode": "en"
                                }) as resp:
            response = await resp.json()
            try:
                return response['translations'][0]['text']
            except KeyError:
                await change_token.main()
                return await get_translate(text)


async def get_gpt(prompt):
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
                await bot.send_message(796644977, response["error"]["message"])
                print(f"Ошибка {response}")
                if "That model is currently overloaded with other requests" in response["error"]["message"]:
                    return "Модель ChatGPT сейчас перегружена запросами, повторите запрос позже."
                return "Генерация текста в данный момент недоступна, попробуйте чуть позже"


async def get_mdjrny(prompt, user_id):
    translated_prompt = await get_translate(prompt)
    try:
        res = tnl.imagine(translated_prompt, webhook_override=midjourney_webhook_url, ref=user_id)
        status = res["success"]
    except requests.exceptions.JSONDecodeError:
        status = False
    return {"status": status}
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


def get_choose_mdjrny(buttonMessageId, image_id, user_id):
    res = tnl.button(f"U{image_id}", buttonMessageId, ref=user_id, webhook_override=midjourney_webhook_url + "/choose")
    return {"status": res["success"]}
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
