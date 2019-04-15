# -*- coding: utf-8 -*-

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from collage.models import PhotoSize, Collage


# class PhotoForm(forms.ModelForm):
#     class Meta:
#         model = Photo


# class CollageInputForm(forms.Form):
#     photo_num = forms.IntegerField()
#     photo_cols = forms.IntegerField()
#     photo_tag = forms.CharField(max_length=30)
#     sizes = PhotoSize.objects.all().order_by('size')
#     photo_size = forms.ModelChoiceField(queryset=sizes, empty_label=sizes.first(), to_field_name='size')
#     #photo_size = forms.IntegerField()

class CollageInputForm(forms.ModelForm):
    class Meta:
        model = Collage
        exclude = [
            'final_img',
            'photos',
            'create_date',
        ]
    def save(self, commit=True):

        # создаем модель Collage
        inst = super().save(commit=False)
        inst.create_date = timezone.now()

        if commit:
            inst.save()
        return inst
#
# class CollageCreateForm(forms.ModelForm):
#     class Meta:
#         model = Collage
#         fields = [
#             'photo_number',
#             'photo_size',
#             'photos',
#             'cols_number',
#         ]
#         # exclude = [
#         #     'delivered',
#         #     'date_created',
#         #     'date_delivered',
#         #     'delivery',
#         # ]
#
#     def clean(self):
#         data = self.cleaned_data
#         # excluded = data['exclude']
#         #
#         # errors = []
#         # for item in excluded:
#         #     if item in data['extra']:
#         #         errors.append(str(item))
#         #
#         # if errors:
#         #     raise ValidationError(
#         #         'Ingredients [{}] are in extras and excludes!'.format(
#         #             ', '.join(errors)
#         #         )
#         #     )
#         return data
#
#     def save(self, commit=True, photos=None):
#         if photos is None:
#             raise ValueError('Photos were not set')
#
#         # создаем модель Collage
#         inst = super().save(commit=False)
#
#         inst.photos = photos
#
#         if commit:
#             inst.save()
#
#         return inst
