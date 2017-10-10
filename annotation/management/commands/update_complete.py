import os
import json
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from annotation.models import Exercise, AnnotationSimilarity, DataSet, Complete


class Command(BaseCommand):
    """
    Update Complete objects for a DataSet. Complete indicate if the annotations of a Sound for a User are finished,
    meaning that there are as many Annotations in the sound as there are in the reference sound
    and that the user has as many AnnotationSimilarities as Annotations exist for the tier.
    """

    @staticmethod
    def add_arguments(parser):
        parser.add_argument('dataset', type=str, default=False, help='dataset name')

    def handle(self, *args, **options):
        data_set_name = options['dataset']

        try:
            data_set = DataSet.objects.get(name=data_set_name)
        except ObjectDoesNotExist:
            print("this data set does not exists in the database")
            return 0

        for exercise in Exercise.objects.filter(data_set=data_set).all():
            for sound in exercise.sounds.all():
                for tier in exercise.tiers.all():
                    for user in data_set.users.all():
                        annotations = tier.annotations.filter(sound=sound, tier=tier).all()
                        reference_annotations = exercise.reference_sound.annotations.filter(tier=tier)
                        similarities = AnnotationSimilarity.objects.filter(similar_sound__in=annotations, user=user)

                        try:
                            complete = Complete.objects.get(user=user, sound=sound)
                            if not annotations.count() == reference_annotations.count() and similarities.count() == \
                                    annotations.count():
                                complete.delete()
                                print("User %s hasn't completed annotations for sound %s" % (user.username, sound.name))
                        except ObjectDoesNotExist:
                            if annotations.count() == reference_annotations.count() and similarities.count() == \
                                    annotations.count():
                                Complete.objects.create(user=user, sound=sound)
                                print("User %s has completed annotations for sound %s" % (user.username, sound.name))
