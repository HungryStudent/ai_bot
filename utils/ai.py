import replicate
import aiohttp
import asyncio

from config import OPENAPI_TOKEN, REPLICATE_API_TOKEN, ya_folder
from create_bot import bot
from utils import db

client = replicate.Client(api_token=REPLICATE_API_TOKEN)
model = client.models.get("tstramer/midjourney-diffusion")
version = model.versions.get("436b051ebd8f68d23e83d22de5e198e0995357afef113768c20f0b6fcef23c8b")


async def get_translate(text):
    iam_token = db.get_iam_token()
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
            return response['translations'][0]['text']


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


async def get_mdjrny(prompt):
    translated_prompt = await get_translate(prompt)
    try:
        inputs = {
            'prompt': translated_prompt,
            'prompt_strength': 0.8,
            'num_outputs': 1,
            'num_inference_steps': 50,
            'guidance_scale': 7.5,
            'scheduler': "DPMSolverMultistep",
        }
        prediction = client.predictions.create(version=version, input=inputs)
        while prediction.status != "succeeded":
            await asyncio.sleep(5)
            prediction.reload()
        return prediction.output
    except Exception as e:
        await bot.send_message(796644977, e)
        return "Произошла ошибка, повторите попытку позже"
