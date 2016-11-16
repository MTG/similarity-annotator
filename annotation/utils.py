import os
import json

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from .models import Exercise, Annotation, AnnotationSimilarity


def exercise_annotations_to_json(exercise_id):
    """
    Queries for the annotations of an exercise and returns them in json format
    Args:
        exercise_id:
    Return:
        annotations: json serialisation of the annotations
    """
    exercise = Exercise.objects.get(id=exercise_id)
    exercise_sounds = exercise.sounds.all()

    sounds_annotations = {}

    for sound in exercise_sounds:
        tiers = {}
        for tier in exercise.tiers.all():

            annotations = {}
            for annotation in Annotation.objects.filter(sound=sound, tier=tier).all():
                # check if there is an annotation similarity
                try:
                    annotation_similarity = AnnotationSimilarity.objects.get(similar_sound=annotation)
                    similarity = {'reference_annotation': annotation_similarity.reference.id,
                                  'similarity_value': annotation_similarity.similarity_measure
                                  }
                except ObjectDoesNotExist:
                    similarity = None
                annotation_dict = {'start_time': annotation.start_time,
                                   'end_time': annotation.end_time,
                                   'similarity': similarity
                                   }
                annotations[annotation.id] = annotation_dict

            tiers[tier.name] = annotations

        sounds_annotations[sound.filename] = tiers

    return json.dumps(sounds_annotations)


def store_tmp_file(uploaded_file):
    """Stores the uploaded file to the TEMP folder
    :param uploaded_file: an instance of InMemoryUploadedFile
    :return: path to newly saved-to-disk file
    """
    path = os.path.join(settings.TEMP_ROOT, uploaded_file.name)
    # if file name already exists in path, create new filename with increasing counter
    repeated_name_counter = 0
    while os.path.isfile(path):
        file_path, file_extension = os.path.splitext(path)
        path = file_path + '_' + str(repeated_name_counter) + file_extension
        repeated_name_counter += 1
    try:
        destination = open(path, 'w+b')
        for chunk in uploaded_file.chunks():
            destination.write(chunk)
    finally:
        destination.close()
    return path
