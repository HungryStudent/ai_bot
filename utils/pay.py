import hashlib
import hmac
import json
import random

import requests

from config import FreeKassa, LAVA_API_KEY, LAVA_SHOP_ID


def get_pay_url_freekassa(user_id, amount):
    md5 = hashlib.md5()
    md5.update(
        f'{FreeKassa.shop_id}:{amount}:{FreeKassa.secret1}:RUB:{user_id}'.encode('utf-8'))
    pwd = md5.hexdigest()
    pay_url = f"https://pay.freekassa.ru/?m={FreeKassa.shop_id}&oa={amount}&currency=RUB&o={user_id}&s={pwd}"
    return pay_url


def sortDict(data: dict):
    sorted_tuple = sorted(data.items(), key=lambda x: x[0])
    return dict(sorted_tuple)


def get_pay_url_lava(user_id, amount):
    payload = {
        "sum": amount,
        "orderId": str(user_id) + ":" + str(random.randint(10000, 1000000)),
        "shopId": LAVA_SHOP_ID
    }

    payload = sortDict(payload)
    jsonStr = json.dumps(payload).encode()

    sign = hmac.new(bytes(LAVA_API_KEY, 'UTF-8'), jsonStr, hashlib.sha256).hexdigest()
    headers = {"Signature": sign, "Accept": "application/json", "Content-Type": "application/json"}
    res = requests.post("https://api.lava.ru/business/invoice/create", json=payload, headers=headers)
    return res.json()["data"]["url"]
