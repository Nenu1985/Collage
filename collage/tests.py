from django.contrib.auth.models import AnonymousUser, User
from django.test import TestCase, Client, RequestFactory
from collage.models import Collage, PhotoSize
from django.db.utils import IntegrityError
from collage.forms import CollageInputForm
from django.urls import reverse
import flickrapi
from django.conf import settings
import requests
from os.path import basename
from tempfile import TemporaryFile
from django.db import transaction
from .models import Photo
from django.utils import timezone
from urllib.parse import urlsplit
from django.core.files import File
from django.shortcuts import get_list_or_404, get_object_or_404

from .views import index
# >>> from django.test.utils import setup_test_environment
# >>> setup_test_environment()
# Create your tests here.


# tests.py
class CollageModelTests(TestCase):

    def test_collage_creation(self):

        self.assertTrue(collage_creation)

    # tests.py
    def test_collage_creation_without_size(self):

        with self.assertRaises(IntegrityError):
            collage = Collage.objects.create(
                photo_number=10,
                cols_number=5,
             )


class ViewsTest(TestCase):

    client = Client()

    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()

    def test_details(self):
        # Create an instance of a GET request.
        request = self.factory.get("/")
        request.user = AnonymousUser()
        col = collage_creation()
        # Test my_view() as if it were deployed at /customer/details
        response = index(request)
        self.assertEqual(response.status_code, 200)

    def test_load_start_page(self):
        size = PhotoSize.objects.create(size=128)

        collage = Collage.objects.create(
            photo_number=10,
            cols_number=5,
            photo_size=size,
        )
        collages = get_object_or_404(Collage.objects.all())
        self.assertTrue(collages, 'Error while creating Collage object')
        response = self.client.get('/collage/')
        self.assertEqual(response.status_code, 200, '/collage/ url is not found')

    def test_load_input_page(self):
        response = self.client.get('/collage/input/')
        self.assertEqual(response.status_code, 200)

    def test_load_input_with_form(self):
        response = self.client.get(
            reverse('collage:input'),
            {'client_input': CollageInputForm()}
        )
        self.assertEqual(response.status_code, 200)


class FlickrTest(TestCase):
    
    def test_flickr_keys(self):
        self.assertEqual(settings.GLOBAL_SETTINGS['FLICKR_PUBLIC'],
                         '1f9874c1a8ea5a85acfd419dd0c2c7e1',
                         'Flickr public key is wrong')

        self.assertEqual(settings.GLOBAL_SETTINGS['FLICKR_SECRET'],
                     '67de04d2825fd397',
                     'Flickr secret key is wrong')

    def test_flickr_api(self):
        flickr = flickrapi.FlickrAPI(
            settings.GLOBAL_SETTINGS['FLICKR_PUBLIC'],
            settings.GLOBAL_SETTINGS['FLICKR_SECRET'],
        )

        extras = 'url_q'        # 150 pixels per side and above

        photos = flickr.walk(text='man',
                             per_page=5,
                             extras=extras
                             )
        retrieved_url = ''
        for i, photo in enumerate(photos):
            url = photo.get(extras, 'no url')
            if url != 'no url':  # if url is empty - pass it and increment photo number
                retrieved_url = url
                break
        self.assertTrue(retrieved_url, 'Flickr didn\'t find any url')
        
        # download a file by url with chunks and create a Photo in db
        with TemporaryFile() as tf:
            r = requests.get(retrieved_url, stream=True)
            for chunk in r.iter_content(chunk_size=4096):
                tf.write(chunk)

            tf.seek(0)
            with transaction.atomic():
                photo = Photo()
                photo.photo_url = retrieved_url
                photo.date = timezone.now()
                photo.img_field.save(basename(urlsplit(retrieved_url).path), File(tf))

        self.assertTrue(photo, 'Photo object didn\'t create')

        self.assertTrue(photo.img_field.url, 'Photo object doesn\'t have a photo url')

        self.assertEqual(photo.photo_url, retrieved_url)


def collage_creation():

    size = PhotoSize.objects.create(size=128)

    collage = Collage.objects.create(
        photo_number=10,
        cols_number=5,
        photo_size=size,
     )
    return collage
