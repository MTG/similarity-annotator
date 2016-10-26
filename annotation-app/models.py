from django.db import models
from django.contrib.auth.models import User


class Exercise(models.Model):
    name = models.CharField(max_length=50)
    reference_sound = models.ForeignKey('Sound', blank=True, null=True, related_name="%(class)s_related")

    def __str__(self):
        return self.name


class Tier(models.Model):
    name = models.CharField(max_length=50)
    parent_tier = models.ForeignKey('self', blank=True, null=True, related_name='child_tiers')
    tier = models.ForeignKey(Exercise, blank=True, null=True, related_name='tiers')

    def __str__(self):
        return self.name


class Sound(models.Model):
    filename = models.CharField(max_length=200)
    exercise = models.ForeignKey(Exercise, related_name='sounds')
    is_reference = models.BooleanField(default=False)
    has_annotations = models.BooleanField(default=False)

    def __str__(self):
        return self.filename


class Annotation(models.Model):
    name = models.CharField(max_length=200)
    start_time = models.IntegerField("start_time")
    end_time = models.IntegerField("end_time", blank=True, null=True)
    sound = models.ForeignKey(Sound, related_name='annotations')
    tier = models.ForeignKey(Tier, related_name='annotations')
    user = models.ForeignKey(User, related_name='annotations')

    def __str__(self):
        return self.name


class AnnotationSimilarity(models.Model):
    reference = models.ForeignKey(Annotation, related_name="%(class)s_related")
    similar_sound = models.ForeignKey(Annotation)
    similarity_measure = models.IntegerField("similarity_measure")
