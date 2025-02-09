import json
import urllib.parse


CONFIG = {
    # "filters": [
    #     {
    #         "country": "Fiji",
    #         "start_year": 2000,
    #         "end_year": 2007
    #     },
    #     {
    #         "country": "Tonga",
    #         "start_year": 2000,
    #         "end_year": 2007
    #     },
    #     {
    #         "country": "",
    #         "start_year": 2000,
    #         "end_year": 2007
    #     }
    # ],
    "countries": ["Fiji", "Tonga"],
    "start_year": 2000,
    "end_year": 2007,
}


def json_encode_config(config: dict) -> str:
    json_str = json.dumps(config)
    encoded_json = urllib.parse.quote(json_str)
    return encoded_json


def json_decode_config(encoded_config: str) -> dict:
    return json.loads(encoded_config)
