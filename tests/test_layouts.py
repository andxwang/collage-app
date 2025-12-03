import unittest
from collage.layouts import layout_three_vertical, layout_four_vertical, layout_four_grid, layout_five_two_three

class TestLayouts(unittest.TestCase):
    def test_three_vertical(self):
        sizes = [(1080, 640)]*3
        output_size = (1080, 1920)
        positions = layout_three_vertical(sizes, output_size)
        self.assertEqual(len(positions), 3)
        self.assertEqual(sum([h for x, y, w, h in positions]), 1920)

    def test_four_vertical(self):
        output_size = (1080, 1920)
        positions = layout_four_vertical(output_size)
        self.assertEqual(len(positions), 4)

    def test_four_grid(self):
        output_size = (1080, 1920)
        positions = layout_four_grid(output_size)
        self.assertEqual(len(positions), 4)

    def test_five_two_three(self):
        output_size = (1080, 1920)
        positions = layout_five_two_three(output_size)
        self.assertEqual(len(positions), 5)

if __name__ == '__main__':
    unittest.main()
