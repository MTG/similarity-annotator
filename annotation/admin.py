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
    list_display = ('filename', 'exercise', 'is_discarded')
    list_display_links = ('filename', 'exercise')
    list_filter = ('exercise', 'is_discarded', )


class AnnotationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'sound', 'tier', 'get_exercise', 'start_time', 'user')
    list_display_links = ('id', 'name', )
    list_filter = ('sound', )

    @staticmethod
    def get_exercise(obj):
        return obj.sound.exercise


class AnnotationSimilarityAdmin(admin.ModelAdmin):
    list_display = ('id', 'reference', 'similar_sound', 'similarity_measure')
    list_display_links = ('id', 'reference', 'similar_sound')


class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

admin.site.register(Sound, SoundAdmin)
admin.site.register(Tier, TierAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Exercise, ExerciseAdmin)
admin.site.register(Annotation, AnnotationAdmin)
admin.site.register(AnnotationSimilarity, AnnotationSimilarityAdmin)
admin.site.register(DataSet, DataSetAdmin)



