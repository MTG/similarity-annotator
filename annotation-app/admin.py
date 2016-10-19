from django.contrib import admin

from .models import Sound, Tier, Exercise, Annotation

admin.site.register(Sound)
admin.site.register(Tier)
admin.site.register(Exercise)
admin.site.register(Annotation)


