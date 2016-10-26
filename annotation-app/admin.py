from django.contrib import admin
from .models import Sound, Tier, Exercise, Annotation, AnnotationSimilarity


class AnnotationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'sound', 'tier')
    list_display_links = ('name', 'sound', 'tier')
    list_filter = ('id', 'sound')


class SoundAdmin(admin.ModelAdmin):
    list_display = ('filename', 'exercise')
    list_display_links = ('filename', 'exercise')
    list_filter = ('exercise',)


admin.site.register(Sound, SoundAdmin)
admin.site.register(Tier)
admin.site.register(Exercise)
admin.site.register(Annotation, AnnotationAdmin)
admin.site.register(AnnotationSimilarity)


