from django.db import models
from django.utils import timezone
import urllib
import requests
import datetime
import flickrapi
from django.conf import settings
from django.core.cache import cache
from tempfile import TemporaryFile
from django.core.files import File
from urllib.parse import urlsplit
from os.path import basename
import cv2
import os
import numpy as np
import uuid

from django.db import transaction

class PhotoSize(models.Model):
    size = models.IntegerField(default=128)

    def __str__(self):
        return str(self.size)


class Photo(models.Model):
    photo_url = models.URLField(default='tutorial:index')
    img_field = models.ImageField(upload_to='upload_collage_photos', unique=True)
    date = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def download_photos_by_url(photo_url):
        """
        Download a photo by url, save it to DB in photo model, return Photo instance
        :param photo_url: url photo(img) to download
        :return: photo model instance
        """
        # file_name = f'collage\photo\\src{str(num)}.jpg'
        try:
            check_photo_exists = Photo.objects.filter(photo_url=photo_url).first()
            if check_photo_exists:
                return Photo.objects.filter(photo_url=photo_url).first()
            else:
                with TemporaryFile() as tf:
                    r = requests.get(photo_url, stream=True)
                    for chunk in r.iter_content(chunk_size=4096):
                        tf.write(chunk)

                    tf.seek(0)
                    with transaction.atomic():
                        photo = Photo()
                        photo.photo_url = photo_url
                        photo.date = timezone.now()
                        photo.img_field.save(basename(urlsplit(photo_url).path), File(tf))

                return photo
        except Exception as e:
            print('download_photos_by_url' + e)
            return None






class CutPhoto(models.Model):
    #photo_src = models.ForeignKey(Photo, on_delete=models.CASCADE, unique=True)
    photo_src = models.OneToOneField(Photo, on_delete=models.CASCADE)
    img_field = models.ImageField(upload_to='cut_collage_photos', unique=True)
    date = models.DateTimeField(auto_now_add=True)

    def face_detect(self, photo_src):
        exists = CutPhoto.objects.filter(photo_src=photo_src).first()

        if exists:
            return exists

        src_img = cv2.imread(photo_src.img_field.path)

        frame_height = src_img.shape[0]
        frame_width = src_img.shape[1]
        iw = 400
        # adjust src_img shape to shape that not less than required size
        # newimg = cv2.resize(oriimg, (int(newX), int(newY)))
        if frame_height < iw:  # height
            scale_coef = iw / frame_height
            src_img = cv2.resize(src_img, (int(src_img.shape[1] * scale_coef), iw))

        elif frame_width < iw:  # width
            scale_coef = iw / frame_width
            src_img = cv2.resize(src_img, (iw, int(src_img.shape[0] * scale_coef)))

        processing_img = src_img.copy()
        frame_height = src_img.shape[0]
        frame_width = src_img.shape[1]

        # resize source image for better processing
        in_height = 300  # initial image height for good face detect
        in_width = int((frame_width / frame_height) * in_height)
        processing_img = cv2.resize(processing_img, (in_width, in_height))

        # get classifier
        # face_cascade = cv2.CascadeClassifier("collage\\haar\\haarcascade_frontalface_default.xml")  # Win style
        face_cascade = cv2.CascadeClassifier("./collage/haar/haarcascade_frontalface_default.xml")  # Ubuntu style
        # face detector
        gray = cv2.cvtColor(processing_img, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=3)
        for (x, y, w, h) in faces:
            processing_img = cv2.rectangle(processing_img, (x, y), (x + w, y + h), (255, 0, 0), 2)

        if not list(faces):
            # draw a red cross:
            cv2.line(processing_img, (5, 5), (15, 15), (0, 0, 255), thickness=2)
            cv2.line(processing_img, (15, 5), (5, 15), (0, 0, 255), thickness=2)
        else:
            cv2.line(processing_img, (5, 5), (7, 14), (0, 255, 0), thickness=2)
            cv2.line(processing_img, (7, 14), (14, 5), (0, 255, 0), thickness=2)
        # roi = Collage.get_roi(int(frame_width / 2), int(frame_height / 2), frame_width, frame_height, iw_h)
        # face_cascade = cv2.CascadeClassifier("collage\\haar\\haarcascade_frontalface_default.xml")
        # out_small_image = src_img[roi[1] - iw_h:roi[1] + iw_h - 1,
        #                   roi[0] - iw_h:roi[0] + iw_h - 1].copy()

        cut_photo = CutPhoto()
        cut_photo.photo_src = photo_src

        Collage.save_mat_to_image_field(processing_img, cut_photo.img_field)
        cut_photo.save()

        return cut_photo



class Collage:

    def get_photos_urls(self):
        flickr = flickrapi.FlickrAPI(
            settings.GLOBAL_SETTINGS['FLICKR_PUBLIC'],
            settings.GLOBAL_SETTINGS['FLICKR_SECRET'],
            cache=True
        )
        flickr.cache = cache

        extras = "url_s"        # 75 pixels per side and above
        if self.photo_size == 128:
            extras = "url_q"    # 150 pixels per side and above
        else:
            extras = "url_n"    # 320 pixels per side and above

        photos = flickr.walk(text=self.photo_tag,
                             per_page=int(self.photo_number*1.2),  # may be you can try different numbers..
                             extras=extras
                             )
        urls = []
        num_of_photos = self.photo_number - 1
        for i, photo in enumerate(photos):
            url = photo.get(extras, 'no url')
            if url != 'no url':  # if url is empty - pass it and increment photo number
                urls.append(url)
            else:
                num_of_photos += 1
            if i >= num_of_photos:
                break
        return urls
    #
    def download_photos_by_url(self, photo_url):
        """
        Download a photo by url, save it to DB in photo model, return Photo instance
        :param photo_url: url photo(img) to download
        :return: photo model instance
        """
        # file_name = f'collage\photo\\src{str(num)}.jpg'
        try:
            check_photo_exists = Photo.objects.filter(photo_url=photo_url).first()
            if check_photo_exists:
                collage_inst = check_photo_exists.collage_set.filter(id=self.id)
                if collage_inst and collage_inst.photo_size == self.photo_size:
                    return Photo.objects.filter(photo_url=photo_url).first()
        except Exception as e:
            print('download_photos_by_url' + e)
        finally:

            with TemporaryFile() as tf:
                r = requests.get(photo_url, stream=True)
                for chunk in r.iter_content(chunk_size=4096):
                    tf.write(chunk)

                tf.seek(0)
                with transaction.atomic():
                    photo = Photo()
                    photo.photo_url = photo_url
                    photo.date = timezone.now()
                    photo.img_field.save(basename(urlsplit(photo_url).path), File(tf))

            return photo


    @classmethod
    def get_roi(cls, x_c: int, y_c: int, i_w: int, i_h: int, iw_h: int):
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

        if x_c + iw_h > i_w and outx_c - (iw_h - (i_w - x_c)) > iw_h:
            outx_c -= iw_h - (i_w - x_c)
        elif x_c - iw_h < 0 and outx_c + (iw_h - x_c) < i_w:
            outx_c += iw_h - x_c

        if y_c + iw_h > i_h and outy_c - (iw_h - (i_h - y_c)) > iw_h:
            outy_c -= iw_h - (i_h - y_c)
        elif y_c - iw_h < 0 and outy_c + (iw_h - y_c) < i_w:
            outy_c += iw_h - y_c

        assert outx_c >= iw_h, 'outx_c {} + iw_h {}'.format(outx_c, iw_h)
        assert outy_c >= iw_h, 'outy_c {} + iw_h {}'.format(outy_c, iw_h)

        return outx_c, outy_c

    @classmethod
    def resize_img(cls, collage, photo):
        """
        Resize input image to some size
        :param photo: source photo instance
        :param collage: collage with photo src_img
        :return: resized image, type: numpy.ndarray
        """
        exists = CutPhoto.objects.filter(photo_src=photo).first()

        if exists:
            return

        iw = collage.photo_size.size
        iw_h = collage.photo_size.size >> 1  # half of img width
        src_img = cv2.imread(photo.img_field.path)



        frame_height = src_img.shape[0]
        frame_width = src_img.shape[1]

        # adjust src_img shape to shape that not less than required size
        # newimg = cv2.resize(oriimg, (int(newX), int(newY)))
        if frame_height < iw:  # height
            scale_coef = iw / frame_height
            src_img = cv2.resize(src_img, (int(src_img.shape[1]*scale_coef), iw))

        elif frame_width < iw: # width
            scale_coef = iw / frame_width
            src_img = cv2.resize(src_img, (iw, int(src_img.shape[0] * scale_coef)))

        processing_img = src_img.copy()
        frame_height = src_img.shape[0]
        frame_width = src_img.shape[1]

        # resize source image for better processing
        in_height = 300  # initial image height for good face detect
        in_width = int((frame_width / frame_height) * in_height)
        processing_img = cv2.resize(processing_img, (in_width, in_height))

        # get classifier
        face_cascade = cv2.CascadeClassifier("collage\\haar\\haarcascade_frontalface_default.xml")

        # face detector
        faces = face_cascade.detectMultiScale(cv2.cvtColor(processing_img,
                                                           cv2.COLOR_BGR2GRAY))
        roi = (0,0)
        # choose the first face, find center of rect
        if not list(faces):  # if no face detected select the middle of the picture
            roi = Collage.get_roi(int(frame_width / 2), int(frame_height / 2), frame_width, frame_height, iw_h)

        else:  # faces are detected, select one of them
            x_center = int((faces[0][0] + faces[0][2] / 2) * (frame_width / in_width))
            y_center = int((faces[0][1] + faces[0][3] / 2) * (frame_height / in_height))
            roi = Collage.get_roi(x_center, y_center, frame_width, frame_height, iw_h)



            # cv2.resize(src_img, fx=scale_coef, fy=scale_coef)

        out_small_image = src_img[roi[1] - iw_h:roi[1] + iw_h - 1,
                          roi[0] - iw_h:roi[0] + iw_h - 1].copy()
        if not list(faces):
        # draw a red cross:
            cv2.line(out_small_image, (5, 5), (15, 15), (0, 0, 255), thickness=2)
            cv2.line(out_small_image, (15, 5), (5, 15), (0, 0, 255), thickness=2)
        else:
            cv2.line(out_small_image, (5, 5), (7, 14), (0, 255, 0), thickness=2)
            cv2.line(out_small_image, (7, 14), (14, 5), (0, 255, 0), thickness=2)
        #roi = Collage.get_roi(int(frame_width / 2), int(frame_height / 2), frame_width, frame_height, iw_h)
        #face_cascade = cv2.CascadeClassifier("collage\\haar\\haarcascade_frontalface_default.xml")
        # out_small_image = src_img[roi[1] - iw_h:roi[1] + iw_h - 1,
        #                   roi[0] - iw_h:roi[0] + iw_h - 1].copy()


        cut_photo = CutPhoto()
        cut_photo.photo_src = photo

        Collage.save_mat_to_image_field(out_small_image, cut_photo.img_field)
        cut_photo.save()

    @classmethod
    def save_mat_to_image_field(cls, image, img_field):

        file_path = settings.MEDIA_ROOT + '\\_temp.jpg'  # Win style
        file_path = settings.MEDIA_ROOT + '/_temp.jpg'  # Ubuntu style
        cv2.imwrite(file_path, image)

        with open(file_path, 'rb') as photo_file:
            f_name = uuid.uuid4().hex[:6]
            f_django = File(photo_file)
            img_field.save(
                f_name,
                f_django,
            )

        try:
            os.remove(file_path)
        except Exception:
            print(Exception)


    def generate_collage(self):
        photos = self.photos.all()

        rows = int(self.photo_number / self.cols_number)
        size = self.photo_size.size

        big_img = np.zeros(
            (size * rows, size * self.cols_number, 3),
            np.uint8
        )

        imgs = []
        for photo in photos:
            cut_photo = photo.cutphoto
            img = cv2.imread(cut_photo.img_field.path)
            imgs.append(img)
        try:
            for row in range(rows):
                for col in range(self.cols_number):
                    big_img[row * size: row * size + size - 1,
                            col * size: col * size + size - 1,
                            :] = imgs[row*self.cols_number + col]
        except Exception as e:
            print(e)


        Collage.save_mat_to_image_field(big_img, self.final_img)






