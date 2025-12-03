from PIL import Image
from typing import List
import os

def validate_images(image_paths: List[str], min_count: int, max_count: int) -> bool:
    if not (min_count <= len(image_paths) <= max_count):
        return False
    for path in image_paths:
        if not os.path.isfile(path):
            return False
        try:
            Image.open(path)
        except Exception:
            return False
    return True
