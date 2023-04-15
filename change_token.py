import requests

from config import ya_token
from utils import db


def start():
    response = requests.post('https://iam.api.cloud.yandex.net/iam/v1/tokens',
                             headers={'Content-Type': 'application/json'},
                             json={
                                 "yandexPassportOauthToken": ya_token
                             })
    db.change_iam_token(response.json()['iamToken'])


if __name__ == "__main__":
    start()
