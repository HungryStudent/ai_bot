from googletrans import Translator
import aiohttp
import asyncio

from config import OPENAPI_TOKEN, SD_TOKEN
from create_bot import bot


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
                return "Error"


async def get_mdjrny(prompt):
    translator = Translator()
    translate = translator.translate(prompt)
    async with aiohttp.ClientSession() as session:
        async with session.post('https://stablediffusionapi.com/api/v3/text2img',
                                json={"key": SD_TOKEN,
                                      "prompt": translate.text,
                                      "samples": 1,
                                      "width": 512,
                                      "height": 512,
                                      "num_inference_steps": 50}) as resp:
            response = await resp.json()
            return response["output"]
