from django.urls import path
from . import views

app_name = 'publish'  # Для темплейтов и конкретизации урла по имени апп

urlpatterns = [
    path('', views.home, name='home'),
    path('slug/<str:slug>/', views.view_post, name='view_post'),
    path('verify/<str:uuid>/', views.verify, name='verify'),
    path('send_mail/', views.send_email, name='send_mail')

]