import os

from django.db import models
from django.contrib.auth.models import User


def exercise_upload_to(instance, filename):
    return os.path.join(instance.name, filename)


class DataSet(models.Model):
    users = models.ManyToManyField(User, related_name="datasets")
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Exercise(models.Model):
    name = models.CharField(max_length=50)
    exercise_id = models.CharField(max_length=50, blank=True, null=True)
    data_set = models.ForeignKey(DataSet, related_name='exercises')
    reference_sound = models.ForeignKey('Sound', blank=True, null=True, related_name="%(class)s_related")
    reference_pitch_sound = models.FileField(blank=True, null=True, upload_to=exercise_upload_to)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Tier(models.Model):
    name = models.CharField(max_length=50)
    # If tiers are related using parent_tier, then annotations are copied to
    # all parent and child tiers, if they are related using special_parent_tier
    # then annotations are copied only to child tiers
    parent_tier = models.ForeignKey('self', blank=True, null=True, related_name='child_tiers')
    special_parent_tier = models.ForeignKey('self', blank=True, null=True, related_name='special_child_tiers')
    exercise = models.ForeignKey(Exercise, related_name='tiers')
    entire_sound = models.BooleanField(default=False)
    point_annotations = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Sound(models.Model):
    ANNOTATION_CHOICES =(
            ('E', 'empty'),
            ('I', 'incomplete'),
            ('C', 'complete')
    )
    filename = models.CharField(max_length=200)
    original_filename = models.CharField(max_length=200, default=None)
    exercise = models.ForeignKey(Exercise, related_name='sounds')
    has_annotations = models.BooleanField(default=False)
    is_discarded = models.BooleanField(default=False)
    annotation_state = models.CharField(max_length=2, choices=ANNOTATION_CHOICES, default='E')

    def __str__(self):
        return self.filename

    def get_annotations_as_dict(self):
        ret = {}
        for tier in self.exercise.tiers.all():
            annotations = Annotation.objects.filter(sound=self, tier=tier)

            ret[tier.name] = []
            for i in annotations.all():
                for s in i.annotationsimilarity_set.all():
                    ret[tier.name].append({
                        'ref_start_time': float(s.reference.start_time),
                        'start_time': float(i.start_time),
                        'ref_end_time': float(s.reference.end_time),
                        'end_time': float(i.end_time),
                        'value': s.similarity_measure
                        })
        return ret


class Annotation(models.Model):
    name = models.CharField(max_length=200)
    start_time = models.DecimalField(max_digits=6, decimal_places=3)
    end_time = models.DecimalField(max_digits=6, decimal_places=3, blank=True, null=True)
    sound = models.ForeignKey(Sound, related_name='annotations')
    tier = models.ForeignKey(Tier, related_name='annotations')
    user = models.ForeignKey(User, related_name='annotations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class AnnotationSimilarity(models.Model):
    reference = models.ForeignKey(Annotation, related_name="%(class)s_related")
    similar_sound = models.ForeignKey(Annotation)
    similarity_measure = models.IntegerField("similarity_measure")
    user = models.ForeignKey(User, related_name='similarity_measures')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Tag(models.Model):
    name = models.CharField(max_length=200)
    tiers = models.ManyToManyField(Tier)
