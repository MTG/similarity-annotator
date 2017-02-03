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
    exercise_id = models.CharField(max_length=50, blank=True, null=True)
    data_set = models.ForeignKey(DataSet, related_name='exercises')
    reference_sound = models.ForeignKey('Sound', blank=True, null=True, related_name="%(class)s_related")
    reference_pitch_sound = models.FileField(blank=True, null=True, upload_to=exercise_upload_to)
    created_at = models.DateTimeField(auto_now_add=True)

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
    ANNOTATION_CHOICES = (
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

    def get_annotations_for_tier(self, tier, user=False):
        ret = []
        for a in Annotation.objects.filter(sound=self, tier=tier).all():
            annotation = {
                "start": a.start_time,
                "end": a.end_time,
                "annotation": a.name,
                "id": a.id,
                }

            if user:
                annotation['similarity'] = 'no'
                references = a.annotationsimilarity_set
                # If user is staff then we return all the AnnotationSimilarity values
                if not user.is_staff:
                    references = references.filter(user=user)

                references = references.all()
                many_values = []
                for ref in references:
                    many_values.append(ref.similarity_measure)

                if len(many_values) > 1:
                    annotation['manyValues'] = many_values

                if len(references):
                    reference = references[0]
                    annotation['similarity'] = "yes"
                    annotation['similValue'] = reference.similarity_measure
                    annotation['reference'] = reference.reference_id
            ret.append(annotation)

        return ret

    def update_annotations(self, tier, annotations, user):
        added = {}
        old_annotations = Annotation.objects.filter(sound=self, tier=tier)
        for a in annotations:
            a_obj = None
            if isinstance(a['id'], int):
                a_obj = old_annotations.filter(pk=a['id'])

            if a_obj and a_obj.count():
                new_annotation = a_obj[0]
                # Update the annotatons in the parent tier and child
                related_annotations = Annotation.objects.filter(sound=self, start_time=new_annotation.start_time,
                                                                end_time=new_annotation.end_time,
                                                                name=new_annotation.name)
                if tier.parent_tier:
                    related_annotations = related_annotations.filter(tier=tier.parent_tier).all()
                    for rel in related_annotations:
                        update_annotation(rel, a, user)
                for child in tier.child_tiers.all():
                    related_annotations = related_annotations.filter(tier=child).all()
                    for rel in related_annotations:
                        update_annotation(rel, a, user)

                # Update the annotation in the current tier
                update_annotation(new_annotation, a, user)
            else:
                new_annotation = Annotation.objects.create(sound=self, start_time=a['start'], end_time=a['end'],
                                                           tier=tier, name=a['annotation'], user=user)
                if tier.parent_tier:
                    parent_annotation = Annotation.objects.create(sound=self, start_time=a['start'], end_time=a['end'],
                           tier=tier.parent_tier, name=a['annotation'], user=user)
                for child in tier.child_tiers.all():
                    child_annotation = Annotation.objects.create(sound=self, start_time=a['start'], end_time=a['end'],
                           tier=child, name=a['annotation'], user=user)

            # Re-create all AnnotationSimilarity for this user
            new_annotation.annotationsimilarity_set.filter(user=user).delete()
            if a['similarity'] == 'yes':
                ref = Annotation.objects.get(id=int(a['reference']))
                AnnotationSimilarity.objects.create(reference=ref, similar_sound=new_annotation,
                                                    similarity_measure=float(a['similValue']),
                                                    user=user)

            added[new_annotation.id] = {'start': a['start'], 'end': a['end']}

        # Remove old_annotation that are not in new list
        for a in old_annotations.all():
            if a.id not in added:
                # Delete annotation in the parent tier and child
                related_annotations = Annotation.objects.filter(sound=self, start_time=a.start_time,
                                                                end_time=a.end_time, name=a.name)
        return True


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
