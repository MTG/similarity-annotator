from django.contrib import admin
from django.core.urlresolvers import reverse

from .models import Sound, Tier, Exercise, Annotation, AnnotationSimilarity, DataSet, Tag, Complete


class DataSetAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('name',)
    list_filter = ('id', 'name')


class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'data_set')
    list_display_links = ('name', )
    list_filter = ('id', 'name')


class TierAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'data_set', 'exercise', 'entire_sound')
    list_display_links = ('name',)

    @staticmethod
    def data_set(obj):
        return obj.exercise.data_set


class SoundAdmin(admin.ModelAdmin):
    list_display = ('id', 'detail', 'filename', 'data_set', 'exercise', 'is_reference', 'is_discarded')
    list_display_links = ('filename',)
    list_filter = ('exercise', 'is_discarded', )
    search_fields = ['id', 'filename']

    def detail(self, obj):
        if obj.name:
            name = obj.name
        else:
            name = obj.filename
        return '<a href="/%s/sound_detail/%s/%s">%s</a>' % (obj.exercise.id, obj.id,
                                                            obj.exercise.tiers.all()[0].id, name)
    detail.allow_tags = True

    @staticmethod
    def data_set(obj):
        return obj.exercise.data_set

    def is_reference(self, obj):
        return obj.exercise.reference_sound == obj
    is_reference.boolean = True


class AnnotationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'sound', 'tier', 'exercise', 'start_time', 'end_time', 'user', 'created_at',
                    'updated_at')
    list_display_links = ('id', 'name', )
    list_filter = ('sound', )

    @staticmethod
    def exercise(obj):
        return obj.sound.exercise


class AnnotationSimilarityAdmin(admin.ModelAdmin):
    list_display = ('id', 'annotation', 'sound', 'exercise', 'similarity_value', 'user', 'created_at', 'updated_at')
    list_display_links = ('id', )
    search_fields = ['user__username']

    def annotation(self, obj):
        annotation = obj.similar_sound
        url = reverse('admin:%s_%s_change' % ('annotation', 'annotation'), args=(annotation.id,))
        return '<a href="%s">%s</a>' % (url, annotation.id)

    annotation.allow_tags = True

    @staticmethod
    def similarity_value(obj):
        if 'value' in obj.similarity:
            return obj.similarity['value']
        return None

    def sound(self, obj):
        sound = obj.similar_sound.sound
        if sound.name:
            sound_name = sound.name
        else:
            sound_name = sound.filename
        return '<a href="/%s/sound_detail/%s/%s">%s</a>' % (sound.exercise.id, sound.id,
                                                            sound.exercise.tiers.all()[0].id, sound_name)

    @staticmethod
    def exercise(obj):
        exercise = obj.similar_sound.sound.exercise
        return exercise.name

    sound.allow_tags = True


class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


class CompleteAdmin(admin.ModelAdmin):
    list_display = ('id', 'sound_link', 'user')
    list_filter = ('user',)
    search_fields = ['sound__name', 'user__username']

    def sound_link(self, obj):
        sound = obj.sound
        if sound.name:
            sound_name = sound.name
        else:
            sound_name = sound.filename
        return '<a href="/%s/sound_detail/%s/%s">%s</a>' % (sound.exercise.id, sound.id,
                                                            sound.exercise.tiers.all()[0].id, sound_name)
    sound_link.allow_tags = True

admin.site.register(Sound, SoundAdmin)
admin.site.register(Tier, TierAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Exercise, ExerciseAdmin)
admin.site.register(Annotation, AnnotationAdmin)
admin.site.register(AnnotationSimilarity, AnnotationSimilarityAdmin)
admin.site.register(DataSet, DataSetAdmin)
admin.site.register(Complete, CompleteAdmin)
