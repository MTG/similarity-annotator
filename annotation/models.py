import os
from decimal import Decimal

from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField


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


def default_keys():
    return ["value", ]


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
    similarity_keys = JSONField(blank=True, null=True, default=default_keys)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def get_special_child_tiers(self):
        t = []
        for special_child in self.special_child_tiers.all():
            t.append(special_child)
            t.extend(special_child.get_special_child_tiers())
        return t

    def get_child_tiers(self):
        t = []
        for child in self.child_tiers.all():
            t.append(child)
            t.extend(child.get_child_tiers())
        return t

    def get_special_parent_tiers(self):
        t = []
        if self.special_parent_tier:
            t.append(self.special_parent_tier)
            t.extend(self.special_parent_tier.get_special_parent_tiers())
        return t


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
                        'similarity': s.similarity
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
                    many_values.append(ref.similarity)

                if len(many_values) > 1:
                    annotation['manyValues'] = many_values

                if len(references):
                    reference = references[0]
                    annotation['similarity'] = "yes"
                    annotation['similValue'] = reference.similarity
                    annotation['reference'] = reference.reference_id
            ret.append(annotation)

        return ret

    @staticmethod
    def check_annotations_correspondence(old_annotations, new_annotations):
        """
        Check if all start times and end times in old annotations exist in new_annotations
        Args:
            old_annotations: Query with the old annotations
            new_annotations: List of the new annotations

        Returns:

        """
        new_start_times = [Decimal(str(a['start'])) for a in new_annotations]
        new_end_times = [Decimal(str(a['end'])) for a in new_annotations]
        there_is_start_time_correspondence = True
        there_is_end_time_correspondence = True

        for special_parent_annotation_start_time in old_annotations.values_list('start_time', flat=True):
            if special_parent_annotation_start_time not in new_start_times:
                there_is_start_time_correspondence = False

        for special_parent_annotation_end_time in old_annotations.values_list('end_time', flat=True):
            if special_parent_annotation_end_time not in new_end_times:
                there_is_end_time_correspondence = False

        return there_is_end_time_correspondence and there_is_start_time_correspondence

    def update_annotations(self, tier, annotations, user):
        added = {}
        old_annotations = Annotation.objects.filter(sound=self, tier=tier)

        # check if all annotations in special parent tier have a correspondence in the special child tier. This would
        # mean parent annotations shouldn't be modified.
        deny_special_parent_modification = False
        if tier.special_parent_tier:
            special_parent_related_annotations = Annotation.objects.filter(sound=self,
                                                                           tier=tier.special_parent_tier).all()
            deny_special_parent_modification = self.check_annotations_correspondence(
                special_parent_related_annotations, annotations)

        for a in annotations:
            a_obj = None
            if isinstance(a['id'], int):
                a_obj = old_annotations.filter(pk=a['id'])

            if a_obj and a_obj.count():
                new_annotation = a_obj[0]

                # Update the annotations in the sync tiers
                parent_related_annotations = Annotation.objects.filter(sound=self, start_time=new_annotation.start_time,
                                                                       end_time=new_annotation.end_time,
                                                                       name=new_annotation.name)
                if tier.parent_tier:
                    parent_related_annotations = parent_related_annotations.filter(tier=tier.parent_tier).all()
                    for rel in parent_related_annotations:
                        self.update_annotation_vals(rel, a, user)
                for child in tier.child_tiers.all():
                    parent_related_annotations = parent_related_annotations.filter(tier=child).all()
                    for rel in parent_related_annotations:
                        self.update_annotation_vals(rel, a, user)

                # Update the annotations in the special parent tier and the corresponding special parent tiers
                for special_parent_tier in tier.get_special_parent_tiers():
                    special_parent_start_time_annotations = Annotation.objects.filter(sound=self,
                                                                                      start_time=new_annotation.
                                                                                      start_time,
                                                                                      tier=special_parent_tier)
                    special_parent_end_time_annotations = Annotation.objects.filter(sound=self,
                                                                                    end_time=new_annotation.end_time,
                                                                                    tier=special_parent_tier)
                    if not deny_special_parent_modification:
                        for rel in special_parent_start_time_annotations:
                            a_copy = a.copy()
                            a_copy['end'] = rel.end_time
                            self.update_annotation_vals(rel, a_copy, user)
                        for rel in special_parent_end_time_annotations:
                            a_copy = a.copy()
                            a_copy['start'] = rel.start_time
                            self.update_annotation_vals(rel, a_copy, user)

                # Update the annotations in special child tiers
                if tier.special_child_tiers.all():
                    start_to_be_changed = end_to_be_changed = None
                    annotation_to_be_changed = Annotation.objects.get(id=a['id'])
                    if annotation_to_be_changed.start_time != a['start']:
                        start_to_be_changed = annotation_to_be_changed.start_time
                    if annotation_to_be_changed.end_time != a['end']:
                        end_to_be_changed = annotation_to_be_changed.end_time
                    for special_child in tier.get_special_child_tiers():
                        if start_to_be_changed:
                            if Annotation.objects.filter(sound=self, tier=special_child,
                                                         start_time=start_to_be_changed).all():
                                child_annotation = Annotation.objects.filter(sound=self, tier=special_child,
                                                                             start_time=start_to_be_changed).all()[0]
                                child_annotation.start_time = a['start']
                                child_annotation.save()
                        if end_to_be_changed:
                            if Annotation.objects.filter(sound=self, tier=special_child,
                                                         end_time=end_to_be_changed).all():
                                child_annotation = Annotation.objects.filter(sound=self, tier=special_child,
                                                                             end_time=end_to_be_changed).all()[0]
                                child_annotation.end_time = a['end']
                                child_annotation.save()

                # Update the annotation in the current tier
                self.update_annotation_vals(new_annotation, a, user)
            else:
                new_annotation = Annotation.objects.create(sound=self, start_time=a['start'], end_time=a['end'],
                                                           tier=tier, name=a['annotation'], user=user)
                if tier.parent_tier:
                    Annotation.objects.create(sound=self, start_time=a['start'], end_time=a['end'],
                                              tier=tier.parent_tier, name=a['annotation'], user=user)
                for child in tier.get_child_tiers():
                    Annotation.objects.create(sound=self, start_time=a['start'], end_time=a['end'],
                                              tier=child, name=a['annotation'], user=user)

                for child in tier.get_special_child_tiers():
                    Annotation.objects.create(sound=self, start_time=a['start'], end_time=a['end'],
                                              tier=child, name=a['annotation'], user=user)

            # Re-create all AnnotationSimilarity for this user
            new_annotation.annotationsimilarity_set.filter(user=user).delete()
            if a['similarity'] == 'yes':
                ref = Annotation.objects.get(id=int(a['reference']))
                AnnotationSimilarity.objects.create(reference=ref, similar_sound=new_annotation,
                                                    similarity=a['similValue'], user=user)

            added[new_annotation.id] = {'start': a['start'], 'end': a['end']}

        # Remove old_annotation that are not in new list
        for a in old_annotations.all():
            if a.id not in added:
                # Delete annotation in the parent tier and child
                Annotation.objects.filter(sound=self, start_time=a.start_time, end_time=a.end_time, name=a.name).delete()

        # create annotations in child tiers
        if tier.child_tiers.all():
            for child_tier in tier.child_tiers.all():
                if Annotation.objects.filter(sound=self, tier=child_tier).count() == 0:
                    for k in added.keys():
                        Annotation.objects.create(start_time=added[k]['start'], end_time=added[k]['end'], sound=self,
                                                  tier=child_tier, user=user)

        # update annotation_state of sound
        num_ref_annotations = Annotation.objects.filter(sound=self.exercise.reference_sound, tier=tier).count()
        added_annotations = Annotation.objects.filter(sound=self, tier=tier)
        num_similarity = AnnotationSimilarity.objects.filter(similar_sound__in=added_annotations).count()
        state = 'E'
        if num_ref_annotations == added_annotations.count():
            state = 'I'
            if num_similarity > 0:
                state = 'C'
        elif added_annotations.count() > 0:
            state = 'I'

        self.annotation_state = state
        self.save()

        return True

    @staticmethod
    def update_annotation_vals(old_annotation, new_annotation, user):
        old_annotation.start_time = new_annotation['start']
        old_annotation.end_time = new_annotation['end']
        old_annotation.name = new_annotation['annotation']
        old_annotation.user = user
        old_annotation.save()


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
    similarity = JSONField(blank=True, null=True, default=dict)
    user = models.ForeignKey(User, related_name='similarity_measures')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Tag(models.Model):
    name = models.CharField(max_length=200)
    tiers = models.ManyToManyField(Tier)
