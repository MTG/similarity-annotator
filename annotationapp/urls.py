from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.exercise_list, name='exercise_list'),
    url(r'^(?P<exercise_id>[0-9]+)/sound_list/$', views.sound_list, name='sound_list'),
    url(r'^(?P<exercise_id>[0-9]+)/sound_detail/(?P<sound_id>[0-9]+)$', views.sound_detail, name='sound_detail'),
    url(r'^(?P<exercise_id>[0-9]+)/ref_sound_detail/(?P<sound_id>[0-9]+)$',
        views.ref_sound_detail, name='ref_sound_detail'),
    url(r'^annotation_action/(?P<sound_id>[0-9]+)/(?P<tier_id>[0-9]+)$',
        views.annotation_action, name='annotation-action'),
    url(r'^get_annotations/(?P<sound_id>[0-9]+)/(?P<tier_id>[0-9]+)$', views.get_annotations, name='get-annotations'),
    url(r'^download_annotations/(?P<sound_id>[0-9]+)$', views.download_annotations, name='download-annotations'),
    url(r'^upload/', views.upload, name='upload'),
    url(r'^(?P<exercise_id>[0-9]+)/download/', views.download, name='download')
]
