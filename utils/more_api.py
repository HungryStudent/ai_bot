import base64
from io import BytesIO

import aiohttp
import requests
import hashlib
from config import FKWallet, IMGBB_API_KEY

fkwallet_currencies = {'qiwi': 63, 'bank_card': 94}


def get_qr_photo(url):
    response = requests.get(
        f'https://api.qrserver.com/v1/create-qr-code/?size=600x600&qzone=2&data={url}')
    return BytesIO(response.content)


def withdraw_ref_balance(purse, amount, currency):
    sign = hashlib.md5(f'{FKWallet.wallet_id}{fkwallet_currencies[currency]}{amount}{purse}{FKWallet.api_key}'.encode())
    response = requests.post('https://fkwallet.com/api_v1.php', data={
        'wallet_id': FKWallet.wallet_id,
        'purse': purse,
        'amount': amount,
        'desc': 'Перевод',
        'currency': fkwallet_currencies[currency],
        'sign': sign.hexdigest(),
        'action': 'cashout'
    })
    print(response.json())
    return response.json()


async def upload_photo_to_host(photo):
    async with aiohttp.ClientSession() as session:
        payload = {"image": photo}
        async with session.post(
                f'https://api.imgbb.com/1/upload?key={IMGBB_API_KEY}', data=payload) as resp:
            data = await resp.json()
            if "data" not in data:
                return "error"
            return data["data"]["url"]
