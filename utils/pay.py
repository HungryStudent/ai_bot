import hashlib
import hmac
import json
import random
from urllib.parse import urlencode

import requests

from config import FreeKassa, LAVA_API_KEY, LAVA_SHOP_ID, PayOK


def get_pay_url_payok(user_id, amount):
    payment = str(user_id) + "_" + str(random.randint(100000, 999999))
    desc = "Пополнение баланса NeuronAgent"
    currency = "RUB"
    sign_string = '|'.join(
        str(item) for item in
        [amount, payment, PayOK.shop_id, currency, desc, PayOK.secret]
    )
    sign = hashlib.md5(sign_string.encode())

    params = {"amount": amount, "payment": payment, "shop": PayOK.shop_id, "desc": desc, "currency": currency,
              "sign": sign.hexdigest()}

    return "https://payok.io/pay?" + urlencode(params)


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
