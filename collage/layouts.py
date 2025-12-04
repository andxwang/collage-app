from typing import List, Tuple

# Layout algorithms for 3, 4, 5 photo collages

def layout_three_vertical(sizes: List[Tuple[int, int]], output_size: Tuple[int, int]):
    """
    Arrange 3 images vertically, sizes can be adjusted.
    Returns a list of (x, y, w, h) for each image.
    """
    width, height = output_size
    heights = [int(height * s[1] / sum([sz[1] for sz in sizes])) for s in sizes]
    positions = []
    y = 0
    for i, h in enumerate(heights):
        positions.append((0, y, width, h))
        y += h
    return positions

def layout_four_vertical(output_size: Tuple[int, int]):
    width, height = output_size
    h = height // 4
    return [(0, i*h, width, h) for i in range(4)]

def layout_four_grid(output_size: Tuple[int, int]):
    width, height = output_size
    w = width // 2
    h = height // 2
    return [(0, 0, w, h), (w, 0, w, h), (0, h, w, h), (w, h, w, h)]

def layout_five_two_three(output_size: Tuple[int, int]):
    width, height = output_size
    w = width // 2
    h = height
    # Left column: 2 photos
    h_left = h // 2
    # Right column: 3 photos
    h_right = h // 3
    positions = [
        (0, 0, w, h_left),
        (0, h_left, w, h_left),
        (w, 0, w, h_right),
        (w, h_right, w, h_right),
        (w, 2*h_right, w, h_right)
    ]
    return positions

def layout_five_three_two(output_size: Tuple[int, int]):
    width, height = output_size
    w = width // 2
    h = height
    # Left column: 3 photos
    h_left = h // 3
    # Right column: 2 photos
    h_right = h // 2
    positions = [
        (0, 0, w, h_left),
        (0, h_left, w, h_left),
        (0, 2*h_left, w, h_left),
        (w, 0, w, h_right),
        (w, h_right, w, h_right)
    ]
    return positions
