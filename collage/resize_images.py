'''
module opens images on disc and cut them to desired size
new photos store on disc with a new name: add char 'p' before orig photo name
'''
import os
import timeit
from multiprocessing import Pool
from itertools import repeat
import numpy
import cv2

from . import collage_create


def get_roi(x_c: int, y_c: int, i_w: int, i_h: int, iw_h: int):
    """
    find ROI of image
    :param x_c: center X coord of ROI, pixels (int)
    :param y_c: center Y coord of ROI, pixels (int)
    :param i_w: input img width
    :param i_h: input img height
    :param iw_h: half of output img with and height
    :return: tuple(outxc, outyc)
    """
    outx_c = x_c
    outy_c = y_c

    if x_c + iw_h > i_w:
        outx_c -= iw_h - (i_w - x_c)
    elif x_c - iw_h < 0:
        outx_c += iw_h - (x_c)

    if y_c + iw_h > i_h:
        outy_c -= iw_h - (i_h - y_c)
    elif y_c - iw_h < 0:
        outy_c += iw_h - (y_c)

    return (outx_c, outy_c)


def detect_face_opencv_haar(face_cascade: cv2.CascadeClassifier, frame: numpy.ndarray,
                            i_w: int, in_height=300):
    """
    Take haar_cascade and frame (img), search faces in the frame, select face with
    size 'iw'
    :param face_cascade: haarCascade obj
    :param frame: image for face detecting
    :param i_w: out img size
    :param in_height: default height for template img for haarDetector algorithm
    :return: out img (cut to iw)
    """

    iw_h = i_w >> 1  # half of img width

    frame_open_cv_haar = frame.copy()
    frame_height = frame_open_cv_haar.shape[0]
    frame_width = frame_open_cv_haar.shape[1]

    in_width = int((frame_width / frame_height) * in_height)

    frame_open_cv_haar_small = cv2.resize(frame_open_cv_haar, (in_width, in_height))

    faces = face_cascade.detectMultiScale(cv2.cvtColor(frame_open_cv_haar_small,
                                                       cv2.COLOR_BGR2GRAY))

    # choose the first face, find center of rect
    if not list(faces):  # if no face detected select the middle of the picture
        roi = get_roi(int(frame_width / 2), int(frame_height / 2), frame_width, frame_height, iw_h)
        out_small_image = frame_open_cv_haar[roi[1] - iw_h:roi[1] + iw_h - 1,
                                             roi[0] - iw_h:roi[0] + iw_h - 1].copy()
    else:  # faces are detected, select one of them
        x_center = int((faces[0][0] + faces[0][2] / 2) * (frame_width / in_width))
        y_center = int((faces[0][1] + faces[0][3] / 2) * (frame_height / in_height))
        roi = get_roi(x_center, y_center, frame_width, frame_height, iw_h)
        out_small_image = frame_open_cv_haar[roi[1] - iw_h:roi[1] + iw_h - 1,
                                             roi[0] - iw_h:roi[0] + iw_h - 1].copy()

    # logger.debug(VisualRecord("Haar face detector " + str(datetime.datetime.utcnow()),
    #                           [frame_open_cv_haar, out_small_image], "bla bla", fmt="png"))

    return out_small_image


def resize_image_haar(cascade: cv2.CascadeClassifier, src_image: numpy.ndarray, p_w: int):
    """doc"""
    out_small_image = detect_face_opencv_haar(cascade, src_image, p_w)
    return out_small_image


def open_im_resize_and_save(path_list: list, i_w: int):
    '''
    Imgs processing: open imgs with path in path_list, resize and save on disk
    :param path_list: string list with path imgs
    :param i_w: out image width
    :return:  nothing. Result photos save on disk
    '''
    face_cascade = cv2.CascadeClassifier("haar\\haarcascade_frontalface_default.xml")
    for path_f in path_list:
        src_im = cv2.imread(path_f)
        temp_img = numpy.zeros((i_w - 1, i_w - 1, 3), numpy.uint8)  # empty image
        temp_img[:, :, 2] = 255  # red color temlate with size 256x256 pixels

        # for real photo apply haar face detector and resize photo by faces
        if not src_im.shape[0] == src_im.shape[1] & src_im.shape[0] == i_w - 1:
            temp_img = resize_image_haar(face_cascade, src_im, i_w)

        # save result photo
        c_dir, file = path_f.split('\\')
        cv2.imwrite(c_dir + "\\" + "p" + file, temp_img)

    print("List of " + str(len(path_list)) + " images saved. " + " PID = " + str(os.getpid()))


def generate_list_of_paths(template_start, template_end, number_of_imgs):
    """doc"""
    out_list = []
    for i in range(number_of_imgs):
        out_list.append(template_start + str(i) + template_end)
    return out_list


def main(num_i: int, i_w: int, collage_cols: int):
    """
    Open photo in "photo" folder of proj dir.
    Compute and form lists of images for parallel image processing.
    Detect faces in the each image and cut them with size IM_WIDTH x IM_WIDTH
    Save small images with a new name in 'photo' dir.

    Sequence of funcs calls:
        - main() calls generate_list_of_paths() - create list with photo paths
        - main() calls openim_resize_and_save() in parallel mode;
        - openim_resize_and_save() processes each photo in list: open, resize and save
        - in the loop by list elements openim_resize_and_save() calls a
        resize_image_haar() that resize imgs
        - resize_image_haar() calls face detector detectFaceOpenCVHaar() that return
        cut photo with final size
        - detectFaceOpenCVHaar() calls get_roi() for checking and changing roi
        - get_roi() returns result roi for  detectFaceOpenCVHaar()
        - detectFaceOpenCVHaar()returns result photo for resize_image_haar()
        - resize_image_haar() returns photo to openim_resize_and_save()
        - openim_resize_and_save() saves result photo on disk
        - main() calls collage_create module and finishes itself
    """
    print("\nStart detecting faces and resize images in parallel mode")

    # of CPUs
    cpus = os.cpu_count()
    # generate a list of images paths
    pathes = generate_list_of_paths("photo\\i0000", ".jpg", num_i)

    photos_by_process = int(num_i / cpus)
    delim = num_i % cpus  # idx starts from 0 but photo from 1 => d decremented by 1

    splitted_list = []

    for i in range(cpus):
        splitted_list.append(i)
        splitted_list[i] = []
        for j in range(photos_by_process):
            splitted_list[i].append(pathes[j + photos_by_process * i])

    # to last list add the last d paths
    for k in range(delim):
        splitted_list[i].append(pathes[k + photos_by_process * cpus])

    # form list from lists
    final_list = [i for i in splitted_list]
    #final_list.append(i) for i in range(len(splitted_list))
        #final_list.append(splitted_list[i])
    t_0 = timeit.time.time()

    # openim_resize_and_save(final_list[3])
    # START parallel execution of functions
    #open_im_resize_and_save(final_list[0], i_w)

    with Pool(processes=cpus) as pool:
        pool.starmap(open_im_resize_and_save, zip(final_list, repeat(i_w)))

    t_1 = timeit.time.time()
    print("execution time: {:.3f}".format(t_1 - t_0) + "s. (Only detecting faces and resize)")

    collage_create.main(num_i, i_w, collage_cols)

if __name__ == "__main__":
    # PERFOMANCE ESTIMATION
    # ~6 сек за цикл сохранения 50 фоток
    # 1 way. print(timeit.timeit("openim_resize_and_save()", setup="from __main__ import
    #                           openim_resize_and_save", number = 2))
    # 2 way. extime = float(timeit.Timer(openim_resize_and_save).timeit(number=3))/3
    # print(extime)
    main(10, 128, 5)
