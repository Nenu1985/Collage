from django.conf.urls import url
from django.urls import path
from . import views

app_name = 'celery_progress'
urlpatterns = [
    # url(r'^(?P<task_id>[\w-]+)/$', views.get_progress, name='task_status')
    path('<str:task_id>/', views.get_progress, name='task_status'),
]
