import os
import json
import shutil
import zipfile
import subprocess
import decimal

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from .models import Sound, Exercise, Annotation, AnnotationSimilarity


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)


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

    return json.dumps(sounds_annotations, cls=DecimalEncoder)


def store_tmp_file(uploaded_file, exercise_name):
    """
    Stores the uploaded file to the TEMP folder
    Args:
        uploaded_file: an instance of InMemoryUploadedFile
        dataset_name: name of the Dataset object
        exercise_name: name of the Exercise object
    Return:
        path: path to newly saved-to-disk file
    """
    path = os.path.join(settings.TEMP_ROOT, exercise_name + '.zip')
    try:
        destination = open(path, 'w+b')
        for chunk in uploaded_file.chunks():
            destination.write(chunk)
    finally:
        destination.close()
    return path


def create_exercise_directory(data_set, exercise_name):
    """
    create directory for exercise audio files
    """
    # first check if dataset directory exist adn create it if don't
    data_set_files_path = os.path.join(settings.MEDIA_ROOT, data_set)
    if not os.path.exists(data_set_files_path):
        os.makedirs(data_set_files_path)
    exercise_files_path = os.path.join(data_set_files_path, exercise_name)
    if not os.path.exists(exercise_files_path):
        os.makedirs(exercise_files_path)
    return exercise_files_path


def decompress_files(dataset_name, exercise_name, zip_file_path):
    """
    Create directory for exercise audio files and decompress zip file into directory
    Args:
        dataset_name:
        exercise_name:
        zip_file_path:
    Return:
        exercise_files_path: path of files directory
    """
    # create directory for exercise audio files
    exercise_files_path = os.path.join(settings.MEDIA_ROOT, dataset_name, exercise_name)
    if not os.path.exists(exercise_files_path):
        os.makedirs(exercise_files_path)

    # decompress zip file into directory
    zip_ref = zipfile.ZipFile(zip_file_path, 'r')
    for member in zip_ref.namelist():
        filename = os.path.basename(member)
        # skip directory
        if not filename:
            continue
        source = zip_ref.open(member)
        target = open(os.path.join(exercise_files_path, filename), 'wb')
        with source, target:
            shutil.copyfileobj(source, target)

    zip_ref.close()

    return exercise_files_path


def get_or_create_sound_object(exercise, sound_filename, original_filename=None):
    try:
        sound = Sound.objects.get(filename=sound_filename, exercise=exercise, original_filename=original_filename)
    except ObjectDoesNotExist:
        sound = Sound.objects.create(filename=sound_filename, exercise=exercise, original_filename=original_filename)
    return sound


def copy_sound_into_media(src, data_set_name, exercise_name, sound_filename):
    """
    Copy files from source to destination
    """
    dst = os.path.join(settings.MEDIA_ROOT, data_set_name, exercise_name, sound_filename)
    shutil.copyfile(src, dst)
    if dst.startswith("/media/"):
        dst = dst[7:]

    return dst
