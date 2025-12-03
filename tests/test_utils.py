import unittest
from collage.utils import validate_images
import tempfile
from PIL import Image
import os

class TestUtils(unittest.TestCase):
    def test_validate_images(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            img_paths = []
            for i in range(3):
                path = os.path.join(tmpdir, f'test{i}.jpg')
                Image.new('RGB', (10, 10)).save(path)
                img_paths.append(path)
            self.assertTrue(validate_images(img_paths, 3, 3))
            self.assertFalse(validate_images(img_paths, 4, 4))
            self.assertFalse(validate_images(['fake.jpg'], 1, 1))

if __name__ == '__main__':
    unittest.main()
