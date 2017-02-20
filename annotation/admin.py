import os

from django.contrib import admin
from .models import Sound, Tier, Exercise, Annotation, AnnotationSimilarity, DataSet, Tag


class DataSetAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('name',)
    list_filter = ('id', 'name')


class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('name', )
    list_filter = ('id', 'name')


class TierAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'exercise', 'entire_sound')
    list_display_links = ('name',)


class SoundAdmin(admin.ModelAdmin):
    list_display = ('filename', 'data_set', 'exercise', 'is_discarded', 'sound_tier_list_url')
    list_display_links = ('filename',)
    list_filter = ('exercise', 'is_discarded', )
    search_fields = ['filename']

    def sound_tier_list_url(self, obj):
        url_name_to_show = os.path.splitext(obj.filename)[0]
        return '<a href="/%s/%s/tiers_list/">%s</a>' % (obj.exercise.id, obj.id, url_name_to_show)
    sound_tier_list_url.allow_tags = True

    @staticmethod
    def data_set(obj):
        return obj.exercise.data_set


class AnnotationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'sound', 'tier', 'exercise', 'start_time', 'user', 'created_at', 'updated_at')
    list_display_links = ('id', 'name', )
    list_filter = ('sound', )

    @staticmethod
    def exercise(obj):
        return obj.sound.exercise


class AnnotationSimilarityAdmin(admin.ModelAdmin):
    list_display = ('id', 'reference', 'similar_sound', 'similarity_measure', 'user', 'created_at', 'updated_at')
    list_display_links = ('id', )


class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

admin.site.register(Sound, SoundAdmin)
admin.site.register(Tier, TierAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Exercise, ExerciseAdmin)
admin.site.register(Annotation, AnnotationAdmin)
admin.site.register(AnnotationSimilarity, AnnotationSimilarityAdmin)
admin.site.register(DataSet, DataSetAdmin)



