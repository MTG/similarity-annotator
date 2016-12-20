import os
import json
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from annotation.models import Sound, Annotation, AnnotationSimilarity, Tier


class Command(BaseCommand):
    """
    Upload annotations. The annotations should be written in the following format:

    { "tier_name": [
                     {"end_time": float,
                     "ref_end_time": float,
                     "ref_start_time": float,
                     "start_time": float,
                     "value": str,}
                    ]
    }
    """
    help = 'Upload annotations from .json files'

    @staticmethod
    def add_arguments(parser):
        parser.add_argument('path', type=str, default=False, help='path to dataset')
        parser.add_argument('username', type=str, default=False, help='username to upload annotations')

    def handle(self, *args, **options):
        annotations_files_path = options['path']
        user_name = options['username']
        # read files in the directory
        for file_name in [file for file in os.listdir(annotations_files_path) if file.endswith('.json')]:
            file_path = os.path.join(annotations_files_path, file_name)
            file_annotations = json.load(open(file_path))
            for tier_name, list_of_annotations in file_annotations.items():
                # check if sound exists and retrieve its exercise
                sound_name = os.path.splitext(file_name)[0]
                try:
                    sound = Sound.objects.get(filename=sound_name)
                except ObjectDoesNotExist:
                    print("This annotations file does have a corresponding sound in the Database")
                    return 0
                # check if tier exists and create it if not
                try:
                    tier = Tier.objects.get(name=tier_name, exercise=sound.exercise)
                except ObjectDoesNotExist:
                    tier = Tier.objects.create(name=tier_name, exercise=sound.exercise)
                # create annotations for each item in the list
                for annotation in list_of_annotations:
                    user = User.objects.get(username=user_name)
                    # create annotation for reference sound
                    reference_annotation = Annotation.objects.create(sound=sound.exercise.reference_sound,
                                                                     tier=tier, user=user,
                                                                     start_time=annotation['ref_start_time'],
                                                                     end_time=annotation['ref_end_time'])
                    # create annotation for similar sound
                    annotation = Annotation.objects.create(sound=sound, tier=tier, user=user,
                                                           start_time=annotation['start_time'],
                                                           end_time=annotation['end_time'])
                    # create similarity annotation
                    if type(annotation['value']) is str:
                        annotation_value = int(annotation['value'])
                    else:
                        annotation_value = annotation['value']
                    similarity_annotation = AnnotationSimilarity.objects.create(reference=reference_annotation,
                                                                                similar_sound=annotation,
                                                                                similarity_measure=annotation_value)
                    print("Create similarity_annotation %s from reference annotation %s and annotation %s" %
                          (similarity_annotation.id,
                           reference_annotation.id,
                           annotation.id))

