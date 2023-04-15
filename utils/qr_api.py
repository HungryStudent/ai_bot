from io import BytesIO

import requests


def get_qr_photo(url):
    response = requests.get(
        f'https://api.qrserver.com/v1/create-qr-code/?size=600x600&qzone=2&data={url}')
    return BytesIO(response.content)
