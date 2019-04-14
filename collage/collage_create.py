'''
Module generates final collage img from small imgs saved on disc in the 'photo' path
'''
import os
import numpy
from PIL import Image
import cv2
from collage import resize_images


def add_imgs_to_bigimg(big_img: numpy.ndarray, path: str, row: int, col: int, i_w: int):
    """
    Open img from disc in 'path' and insert it into collage img 'big_img'.
    Insert position defined by 'row', 'col' and image width 'i_w'
    :param big_img: collage img
    :param path:    path to img for inserting
    :param row:     row cell
    :param col:     column cell
    :param i_w:     image width
    :return:        nothing: altering an collage img
    """
    img = cv2.imread(path)  # open img
    # check the image size. If less than 'c.IM_WIDTH' fill with empty image
    if img.shape[0] >= i_w - 1 & img.shape[1] >= i_w - 1:
        big_img[row * i_w: row * i_w + i_w - 1, col * i_w: col * i_w + i_w - 1, :] = img
    else:
        img = numpy.zeros((i_w - 1, i_w - 1, 3), numpy.uint8)  # empty image
        img[:, :, 2] = 255  # red color
        big_img[row * i_w: row * i_w + i_w - 1, col * i_w: col * i_w + i_w - 1, :] = img


def main(num_i: int, i_w: int, collage_cols: int):
    """
    Open small images and generate from them a collage
    """
    print("\nGenerating a collage\n")
    collage_rows = int(num_i / collage_cols)

    imgs_paths = resize_images.generate_list_of_paths("photo\\pi0000", ".jpg", num_i)
    big_img = numpy.zeros((i_w * collage_rows, i_w * collage_cols, 3), numpy.uint8)

    for i in range(collage_rows):
        for j in range(collage_cols):
            add_imgs_to_bigimg(big_img, imgs_paths[j + i * collage_cols], i, j, i_w)

    out_path = "photo\\out1.jpg"
    cv2.imwrite(out_path, big_img)
    image = Image.open(out_path)
    im2 = Image.fromarray(big_img)
    print("Complete! Collage image path: " + os.getcwd() + out_path)
    image.show()

# for module test:
if __name__ == "__main__":
    main(10, 256, 2)
