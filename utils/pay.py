import hashlib

from config import FreeKassa, price


def get_pay_url(user_id):
    md5 = hashlib.md5()
    md5.update(
        f'{FreeKassa.shop_id}:{price}:{FreeKassa.secret1}:RUB:{user_id}'.encode('utf-8'))
    pwd = md5.hexdigest()
    pay_url = f"https://pay.freekassa.ru/?m={FreeKassa.shop_id}&oa={price}&currency=RUB&o={user_id}&s={pwd}"
    return pay_url
