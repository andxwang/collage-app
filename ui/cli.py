import argparse
from collage.layouts import layout_three_vertical, layout_four_vertical, layout_four_grid, layout_five_two_three
from collage.renderer import compose_collage
from collage.utils import validate_images
from config import DEFAULT_OUTPUT_SIZE

import sys

def main():
    parser = argparse.ArgumentParser(description='Create a photo collage.')
    parser.add_argument('style', choices=['3-vertical', '4-vertical', '4-grid', '5-2-3'], help='Collage style')
    parser.add_argument('images', nargs='+', help='Paths to images')
    parser.add_argument('-o', '--output', default='collage.jpg', help='Output file name')
    parser.add_argument('-s', '--size', type=str, default=None, help='Output size WxH, e.g. 1080x1920')
    args = parser.parse_args()

    if args.size:
        try:
            w, h = map(int, args.size.lower().split('x'))
            output_size = (w, h)
        except Exception:
            print('Invalid size format. Use WxH, e.g. 1080x1920')
            sys.exit(1)
    else:
        output_size = DEFAULT_OUTPUT_SIZE

    if args.style == '3-vertical':
        if not validate_images(args.images, 3, 3):
            print('Provide exactly 3 valid image paths.')
            sys.exit(1)
        # For now, equal sizes
        sizes = [(output_size[0], output_size[1]//3)]*3
        positions = layout_three_vertical(sizes, output_size)
    elif args.style == '4-vertical':
        if not validate_images(args.images, 4, 4):
            print('Provide exactly 4 valid image paths.')
            sys.exit(1)
        positions = layout_four_vertical(output_size)
    elif args.style == '4-grid':
        if not validate_images(args.images, 4, 4):
            print('Provide exactly 4 valid image paths.')
            sys.exit(1)
        positions = layout_four_grid(output_size)
    elif args.style == '5-2-3':
        if not validate_images(args.images, 5, 5):
            print('Provide exactly 5 valid image paths.')
            sys.exit(1)
        positions = layout_five_two_three(output_size)
    else:
        print('Unknown style.')
        sys.exit(1)

    collage = compose_collage(args.images, positions, output_size)
    collage.save(args.output)
    print(f'Collage saved to {args.output}')

if __name__ == '__main__':
    main()
