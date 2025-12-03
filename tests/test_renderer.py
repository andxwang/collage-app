import unittest
from collage.renderer import compose_collage
from collage.layouts import layout_three_vertical
import tempfile
from PIL import Image
import os

class TestRenderer(unittest.TestCase):
    def test_compose_collage(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            img_paths = []
            for i in range(3):
                path = os.path.join(tmpdir, f'test{i}.jpg')
                Image.new('RGB', (100, 100)).save(path)
                img_paths.append(path)
            output_size = (300, 300)
            sizes = [(100, 100)]*3
            positions = layout_three_vertical(sizes, output_size)
            collage = compose_collage(img_paths, positions, output_size)
            self.assertEqual(collage.size, output_size)

if __name__ == '__main__':
    unittest.main()
