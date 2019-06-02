from django.urls import path
from . import views

app_name = 'collage'  # Для темплейтов и конкретизации урла по имени апп

urlpatterns = [

    # ex: /
    path('', views.index, name='index'),
    path('main/', views.main, name='main'),
    path('index/', views.index),
    path('image/<int:img_id>', views.show_image, name='show_image'),

]