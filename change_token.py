import asyncio

import requests

from config import ya_token
from utils import db


async def main():
    response = requests.post('https://iam.api.cloud.yandex.net/iam/v1/tokens',
                             headers={'Content-Type': 'application/json'},
                             json={
                                 "yandexPassportOauthToken": ya_token
                             })
    await db.change_iam_token(response.json()['iamToken'])


if __name__ == "__main__":
    asyncio.run(main())
