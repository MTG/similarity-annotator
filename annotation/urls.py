from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.data_set_list, name='data_set_list'),
    url(r'^(?P<dataset_id>[0-9]+)/$', views.exercise_list, name='exercise_list'),
    url(r'^(?P<exercise_id>[0-9]+)/sound_list/$', views.sound_list, name='sound_list'),
    url(r'^(?P<exercise_id>[0-9]+)/(?P<sound_id>[0-9]+)/tiers_list/$', views.tier_list, name='tier_list'),
    url(r'^(?P<exercise_id>[0-9]+)/(?P<tier_id>[0-9]+)/(?P<sound_id>[0-9]+)/edit/$', views.tier_edit, name='tier_edit'),
    url(r'^(?P<exercise_id>[0-9]+)/(?P<tier_id>[0-9]+)/(?P<sound_id>[0-9]+)/delete/$', views.tier_delete,
        name='tier_delete'),
    url(r'^(?P<exercise_id>[0-9]+)/check_tiers_ajax/$', views.check_tiers_ajax, name='check_tiers_ajax'),
    url(r'^(?P<exercise_id>[0-9]+)/sound_detail/(?P<sound_id>[0-9]+)/(?P<tier_id>[0-9]+)$',
        views.sound_detail, name='sound_detail'),
    url(r'^(?P<exercise_id>[0-9]+)/ref_sound_detail/(?P<sound_id>[0-9]+)/(?P<tier_id>[0-9]+)$',
        views.ref_sound_detail, name='ref_sound_detail'),
    url(r'^annotation_action/(?P<sound_id>[0-9]+)/(?P<tier_id>[0-9]+)$',
        views.annotation_action, name='annotation-action'),
    url(r'^download_annotations/(?P<sound_id>[0-9]+)$', views.download_annotations, name='download-annotations'),
    url(r'^(?P<exercise_id>[0-9]+)/(?P<sound_id>[0-9]+)/tier_creation/$', views.tier_creation, name='tier_creation'),
]
