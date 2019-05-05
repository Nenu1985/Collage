from django.urls import path
from . import views

app_name = 'collage'  # Для темплейтов и конкретизации урла по имени апп

urlpatterns = [

    # ex: /
    path('', views.index, name='index'),
    # path('index/', views.index),
    # path('get-photo/<int:collage_id>/', views.get_photo, name='get_photo'),
    # path('create/', views.collage_create, name='create'),
    path('input/', views.collage_input, name='input'),
    # path('save/', views.collage_save, name='save'),
    path('view/<int:collage_id>/', views.collage_view, name='view'),
    # path('view/<int:collage_id>/processing/', views.collage_view_processing, name='processing'),
    # path('view/async', views.async_example, name='async'),
    # path('view/progress', views.progress, name='progress')
]