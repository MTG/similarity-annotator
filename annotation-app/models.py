from __future__ import unicode_literals

from django.db import models


class Tier(models.Model):
    name = models.CharField(max_length=50)
    parent_tier = models.ForeignKey('self', blank=True, null=True, related_name='child_tiers')

    def __str__(self):
        return self.name


class Exercise(models.Model):
    name = models.CharField(max_length=50)
    tiers = models.ManyToManyField(Tier, blank=True, related_name='exercise')
    reference_sound = models.ForeignKey('Sound', blank=True, null=True, related_name="%(class)s_related")

    def __str__(self):
        return self.name


class Sound(models.Model):
    filename = models.CharField(max_length=200)
    waveform_data = models.CharField(max_length=200)
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


class AnnotationSimilarity(models.Model):
    reference = models.ForeignKey(Annotation, related_name="%(class)s_related")
    other_sound = models.ForeignKey(Annotation)
    similarity_measure = models.IntegerField("similarity_measure")
