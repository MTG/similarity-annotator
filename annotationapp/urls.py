from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.exercise_list, name='exercise_list'),
    url(r'^(?P<exercise_id>[0-9]+)/sound_list/$', views.sound_list, name='sound_list'),
    url(r'^(?P<exercise_id>[0-9]+)/sound_detail/(?P<sound_id>[0-9]+)$', views.sound_detail, name='sound_detail'),
    url(r'^upload/', views.upload, name='upload')
]
