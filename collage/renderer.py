from PIL import Image
from typing import List, Tuple

def compose_collage(image_paths: List[str], positions: List[Tuple[int, int, int, int]], output_size: Tuple[int, int]) -> Image.Image:
    """
    Composes images into a collage based on positions and output size.
    """
    collage = Image.new('RGB', output_size, (255, 255, 255))
    for img_path, (x, y, w, h) in zip(image_paths, positions):
        img = Image.open(img_path).convert('RGB')
        img = img.resize((w, h), Image.Resampling.LANCZOS)
        collage.paste(img, (x, y))
    return collage
