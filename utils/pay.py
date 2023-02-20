import hashlib

from config import FreeKassa


def get_pay_url(user_id, amount):
    md5 = hashlib.md5()
    md5.update(
        f'{FreeKassa.shop_id}:{amount}:{FreeKassa.secret1}:RUB:{user_id}'.encode('utf-8'))
    pwd = md5.hexdigest()
    pay_url = f"https://pay.freekassa.ru/?m={FreeKassa.shop_id}&oa={amount}&currency=RUB&o={user_id}&s={pwd}"
    return pay_url
