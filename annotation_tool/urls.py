from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.sound_list, name='index'),
    url(r'^(?P<sound_id>[0-9]+)/$', views.sound_detail, name='sound_detail'),
]
