from io import BytesIO

import requests
import hashlib
from config import FKWallet

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
