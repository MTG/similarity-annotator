import os

from django.db import models
from django.contrib.auth.models import User


def exercise_upload_to(instance, filename):
    return os.path.join(instance.name, filename)


class DataSet(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Exercise(models.Model):
    name = models.CharField(max_length=50)
    data_set = models.ForeignKey(DataSet, related_name='exercises')
    reference_sound = models.ForeignKey('Sound', blank=True, null=True, related_name="%(class)s_related")
    reference_pitch_sound = models.FileField(blank=True, null=True, upload_to=exercise_upload_to)

    def __str__(self):
        return self.name


class Tier(models.Model):
    name = models.CharField(max_length=50)
    parent_tier = models.ForeignKey('self', blank=True, null=True, related_name='child_tiers')
    exercise = models.ForeignKey(Exercise, related_name='tiers')
    entire_sound = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Sound(models.Model):
    filename = models.CharField(max_length=200)
    exercise = models.ForeignKey(Exercise, related_name='sounds')
    has_annotations = models.BooleanField(default=False)
    is_discarded = models.BooleanField(default=False)

    def __str__(self):
        return self.filename


class Annotation(models.Model):
    name = models.CharField(max_length=200)
    start_time = models.DecimalField(max_digits=6, decimal_places=3)
    end_time = models.DecimalField(max_digits=6, decimal_places=3, blank=True, null=True)
    sound = models.ForeignKey(Sound, related_name='annotations')
    tier = models.ForeignKey(Tier, related_name='annotations')
    user = models.ForeignKey(User, related_name='annotations')

    def __str__(self):
        return self.name


class AnnotationSimilarity(models.Model):
    reference = models.ForeignKey(Annotation, related_name="%(class)s_related")
    similar_sound = models.ForeignKey(Annotation)
    similarity_measure = models.IntegerField("similarity_measure")


class Tag(models.Model):
    name = models.CharField(max_length=200)
