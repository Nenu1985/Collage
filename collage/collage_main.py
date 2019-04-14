"""
    Main module for collage creating
"""
import argparse
from . import flickr_image_download as flickr

def main(count_photo: int, im_width: int, collage_cols: int):
    """
        main func
    """
    collage_rows = int(count_photo / collage_cols)    # height
    print("It will download {:d} images from flickr.com, resise them to "
          "{:d}".format(count_photo, im_width),
          "x{:d} format.\nGenerate a collage with {:d} cells in a row and "
          "{:d}".format(im_width, collage_cols, collage_rows),
          " cells in a column.")

    flickr.main(count_photo, im_width, collage_cols)



if __name__ == "__main__":

    PARSER = argparse.ArgumentParser(
        description='This app is a solved '
        'task #1 at http://truepositive.ru/hr/. '
        'Example: \'collage_main.py 50 256 10\' will create an image that consists of 50 images'
        'with size of 256x256. The shape of out image will be 10 x 5 cells '
        '(10 - width, 5 - height')

    PARSER.add_argument('count_photo', metavar='N', type=int,
                        help='Number of fotos to download and insert into a collage image',
                        )
    PARSER.add_argument('im_width', metavar='WIDTH', type=int, choices=range(50, 1024),
                        help='Define a size of img. HEIGHT of images will be equal to WIDTH.',
                        )
    PARSER.add_argument('collage_cols', metavar='COLS', type=int,
                        help='Number of columns in a collage img. Number of ROWS = N/COLS.',
                        )

    ARGS = PARSER.parse_args()
    main(ARGS.count_photo, ARGS.im_width, ARGS.collage_cols)
