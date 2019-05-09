# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task, task
from Collag.celery import app
from .models import Collage
from time import sleep
import time
from celery_pb.backend import ProgressRecorder

# tasks.py
from celery import shared_task, task

@shared_task
def launch_processing(collage_id):
    collage = Collage.objects.get(id=collage_id)
    photo_urls = collage.get_photos_urls()

    # download, store and return photos
    for i, url in enumerate(photo_urls):
        new_photo = collage.download_photos_by_url(url)
        new_photo.save()
        collage.photos.add(new_photo)

    # collage.get_cv2_images()
    collage.generate_collage()
    return "Collage created. Id = {}, " \
           "Date = {}".format(collage.id,
                              collage.create_date.strftime("%d %b %Y %H:%M:%S"))


@app.task
def test_long_task():
    sleep(3)
    return 'Slept ok'


@shared_task
def test_long_task2():
    sleep(4)
    return 'Slept ok'


@shared_task(bind=True)
def my_task(self, seconds):
    progress_recorder = ProgressRecorder(self)
    for i in range(seconds):
        time.sleep(1)
        progress_recorder.set_progress(i + 1, seconds)
    return 'done'


@app.task(bind=True)
def my_task2(self):
    time.sleep(1)
    return 'my_task3: {}'.format(self.request.id)


@task(bind=True)
def my_task3(self):
    time.sleep(2)
    return 'my_task3: {}'.format(self.request.id)
