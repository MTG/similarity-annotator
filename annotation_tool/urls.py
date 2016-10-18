from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.dataset_list, name='dataset_list'),
    url(r'^(?P<dataset_id>[0-9]+)/sound_list/$', views.sound_list, name='sound_list'),
    url(r'^(?P<dataset_id>[0-9]+)/sound_detail/(?P<sound_id>[0-9]+)$', views.sound_detail, name='sound_detail'),
]
