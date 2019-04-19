# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from Collag.celery import app
from .models import Collage, Photo, CutPhoto
from django.utils import timezone
import requests
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
from time import sleep

@shared_task
def add(x, y):
    return x + y


@shared_task
def mul(x, y):
    return x * y


@shared_task
def xsum(numbers):
    return sum(numbers)


@shared_task
def launch_processing(collage_id):
    collage = Collage.objects.get(id=collage_id)
    photo_urls = collage.get_photos_urls()

    # download, store and return photos
    for i, url in enumerate(photo_urls):
        new_photo = collage.download_photos_by_url(url)
        new_photo.save()
        collage.photos.add(new_photo)

    return "Collage created. Id = {}, Date = {}".format(collage.id,
            collage.create_date.strftime("%d %b %Y %H:%M:%S"))



@app.task
def test_long_task():
    sleep(3)
    return 'Slept ok'
@shared_task
def test_long_task2():
    sleep(4)
    return 'Slept ok'
