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

# model.py
class PhotoSize(models.Model):
    size = models.IntegerField(default=128)

    def __str__(self):
        return str(self.size)


class Photo(models.Model):
    photo_url = models.URLField(default='tutorial:index')
    img_field = models.ImageField(upload_to='upload_collage_photos', unique=True)
    valid = models.BooleanField(default=True)
    date = models.DateTimeField(auto_now_add=True)


class CutPhoto(models.Model):

    photo_src = models.OneToOneField(Photo, on_delete=models.CASCADE)
    img_field = models.ImageField(upload_to='cut_collage_photos', unique=True)
    date = models.DateTimeField(auto_now_add=True)


# Create your models here.
class Collage(models.Model):

    photo_number = models.IntegerField(default=10)
    cols_number = models.IntegerField(default=5)
    create_date = models.DateTimeField(auto_now_add=True)
    photo_tag = models.CharField(max_length=30, default='women')
    photo_size = models.ForeignKey(PhotoSize, on_delete=models.CASCADE, blank=True)
    #photo_size = models.IntegerField()
    photos = models.ManyToManyField(Photo, blank=True)

    final_img = models.ImageField(upload_to='collages', blank=True)

    def __str__(self):
        return 'Collage N = {0}; ' \
               'Size = {1}; ' \
               'Cols num = {2}; ' \
               'Size = {3}---'\
               'Date = {4}'\
                .format(self.photo_number,
                        self.photo_size,
                        self.cols_number,
                        self.photo_size.size,
                        self.create_date.strftime("%d %b %Y %H:%M:%S"),
                        )

    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=3) <= self.create_date <= now

    # наводим красоту для метода при отображении списка вопросов в админке
    was_published_recently.admin_order_field = 'pub_date'
    was_published_recently.boolean = True
    was_published_recently.short_description = 'Published recently?'

    # models.py
    def get_photos_urls(self):

        flickr = flickrapi.FlickrAPI(
            settings.GLOBAL_SETTINGS['FLICKR_PUBLIC'],
            settings.GLOBAL_SETTINGS['FLICKR_SECRET'],
            cache=True
        )

        # экстра-параметр размера изображений (75 пикселей)
        extras = "url_s"
        if self.photo_size == 128:
            extras = "url_q"    # 150 pixels per side and above
        else:
            extras = "url_n"    # 320 pixels per side and above

        # создаём генератор ссылок
        photos = flickr.walk(text=self.photo_tag,
                             per_page=20,
                             extras=extras
                             )
        urls = []  # список ссылок

        # извлекаем ссылки
        for i, photo in enumerate(photos):
            urls.append(photo.get(extras, 'no url'))
            if i >= self.photo_number - 1:
                break

        return urls
    # models.py
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
            ptint('download_photos_by_url' + e)
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
    #
    def get_cv2_images(self):
        photos_to_cut = self.photos.all();

        images = []
        for photo in photos_to_cut:
            Collage.resize_img(self, photo)

        return images


    @classmethod
    def save_mat_to_image_field(cls, image, img_field):

        file_path = settings.MEDIA_ROOT + '\\_temp.jpg'
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

    # models.py
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
                    :] = imgs[row * self.cols_number + col]
        except Exception as e:
            print(e)

        Collage.save_mat_to_image_field(big_img, self.final_img)


    # model.py
    def resize_img(self, photo):
        """
        Resize input image to some size
        :param photo: source photo instance
        :param collage: collage with photo src_img
        :return: resized image, type: numpy.ndarray
        """
        exists = CutPhoto.objects.filter(photo_src=photo).first()

        if exists:
            return

        iw_h = self.photo_size.size >> 1  # half of img width
        src_img = cv2.imread(photo.img_field.path)
        frame_height = src_img.shape[0]
        frame_width = src_img.shape[1]

        roi = get_roi(int(frame_width / 2), int(frame_height / 2), frame_width, frame_height, iw_h)
        #face_cascade = cv2.CascadeClassifier("collage\\haar\\haarcascade_frontalface_default.xml")
        out_small_image = src_img[roi[1] - iw_h:roi[1] + iw_h - 1,
                          roi[0] - iw_h:roi[0] + iw_h - 1].copy()

        cut_photo = CutPhoto()
        cut_photo.photo_src = photo

        Collage.save_mat_to_image_field(out_small_image, cut_photo.img_field)
        cut_photo.save()


# models.py
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

    return (outx_c, outy_c)