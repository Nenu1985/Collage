from django.urls import path
from . import views

app_name = 'collage'  # Для темплейтов и конкретизации урла по имени апп

urlpatterns = [
    path('', views.index, name='index'),
    path('input/', views.collage_input, name='input'),
    path('view/<int:collage_id>/', views.collage_view, name='view'),
]