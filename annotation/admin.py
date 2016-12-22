from django.contrib import admin
from .models import Sound, Tier, Exercise, Annotation, AnnotationSimilarity


class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_display_links = ('name', )
    list_filter = ('id', 'name')


class SoundAdmin(admin.ModelAdmin):
    list_display = ('filename', 'exercise', 'is_discarded')
    list_display_links = ('filename', 'exercise')
    list_filter = ('exercise', 'is_discarded', )


class AnnotationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'sound', 'tier')
    list_display_links = ('name', 'sound', 'tier')
    list_filter = ('id', 'sound')


class AnnotationSimilarityAdmin(admin.ModelAdmin):
    list_display = ('id', 'reference', 'similar_sound', 'similarity_measure')
    list_display_links = ('id', 'reference', 'similar_sound')

admin.site.register(Sound, SoundAdmin)
admin.site.register(Tier)
admin.site.register(Exercise, ExerciseAdmin)
admin.site.register(Annotation, AnnotationAdmin)
admin.site.register(AnnotationSimilarity, AnnotationSimilarityAdmin)


