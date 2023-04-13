import requests

from utils import db

response = requests.post('https://iam.api.cloud.yandex.net/iam/v1/tokens',
                         headers={'Content-Type': 'application/json'},
                         json={
                             "yandexPassportOauthToken": "y0_AgAAAABWCJPZAATuwQAAAADgwm_JZBZxXwkKT2--2959T82zdRs0O3c"
                         })
db.change_iam_token(response.json()['iamToken'])