import json
import urllib.parse


CONFIG = {
    "Fiji": {"start_year": 2000, "end_year": 2010},
    "Tonga": {"start_year": 2000, "end_year": 2010},
}


def json_encode_config(config: dict) -> str:
    json_str = json.dumps(config)
    encoded_json = urllib.parse.quote(json_str)
    return encoded_json


def json_decode_config(encoded_config: str) -> dict:
    return json.loads(encoded_config)
