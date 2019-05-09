from django.test import TestCase, Client
from collage.models import Collage, PhotoSize
from django.db.utils import IntegrityError
from collage.forms import CollageInputForm
from django.urls import reverse

# Create your tests here.


class CollageModelTests(TestCase):

    def test_collage_creation(self):

        size = PhotoSize.objects.create(size=128)

        collage = Collage.objects.create(
            photo_number=10,
            cols_number=5,
            photo_size=size,
         )
        self.assertTrue(collage)

    def test_collage_creation_without_size(self):

        with self.assertRaises(IntegrityError):
            collage = Collage.objects.create(
                photo_number=10,
                cols_number=5,
             )


class ViewsModelTest(TestCase):
    client = Client()

    def test_load_start_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_load_start_page_alt(self):
        response = self.client.get('/collage/')
        self.assertEqual(response.status_code, 200)

    def test_load_input_page(self):
        response = self.client.get('/collage/input/')
        self.assertEqual(response.status_code, 200)

    def test_load_input_with_form(self):
        response = self.client.get(
            reverse('collage:input'),
            {'client_input': CollageInputForm()}
        )
        self.assertEqual(response.status_code, 200)
