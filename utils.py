import json


def save_json(obj, f):
    with open(f, 'w', encoding='utf-8') as fp:
        json.dump(obj, fp, ensure_ascii=False, indent=4)
