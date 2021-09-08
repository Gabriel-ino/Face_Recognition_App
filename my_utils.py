import json
from typing import AnyStr, Dict
import scrypt


def convert_to_json_binary(info: Dict):
    json_info = json.dumps(info)

    with open('user.json', 'w') as json_file:
        json_file.write(json_info)

    with open('user.json', 'rb') as json_file:
        data = json_file.readlines()
        print(data)

    return data


def encrypting_password(password: AnyStr) -> str:
    return scrypt.hash(password, 'random salt')

