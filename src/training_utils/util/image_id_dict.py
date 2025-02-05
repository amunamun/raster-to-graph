import json
import os.path


def get_image_numbers(data_path: str):
    with open(os.path.join(data_path, 'image_numbers.json')) as f:
        d = json.load(f)
    return d