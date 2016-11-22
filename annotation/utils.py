import os
import json
import shutil
import zipfile
import subprocess

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from .models import Sound, Exercise, Annotation, AnnotationSimilarity


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


def store_tmp_file(uploaded_file, exercise_name):
    """
    Stores the uploaded file to the TEMP folder
    Args:
        uploaded_file: an instance of InMemoryUploadedFile
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


def create_exercise_directory(exercise_name):
    """
    create directory for exercise audio files
    """
    exercise_files_path = os.path.join(settings.MEDIA_ROOT, exercise_name)
    if not os.path.exists(exercise_files_path):
        os.makedirs(exercise_files_path)
    return exercise_files_path


def decompress_files(exercise_name, zip_file_path):
    """
    Create directory for exercise audio files and decompress zip file into directory
    Args:
        exercise_name:
        zip_file_path:
    Return:
        exercise_files_path: path of files directory
    """
    # create directory for exercise audio files
    exercise_files_path = os.path.join(settings.MEDIA_ROOT, exercise_name)
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


def create_audio_waveform(exercise_files_path, sound_filename):
    # create wave form data
    waveform_data_filename = os.path.splitext(sound_filename)[0] + '.dat'
    waveform_data_file_path = os.path.join(exercise_files_path, waveform_data_filename)
    subprocess.call(["audiowaveform", "-i", os.path.join(exercise_files_path, sound_filename),
                     "-o", waveform_data_file_path, "-b", "8"])
    return waveform_data_file_path


def create_sound_object(exercise, sound_filename, waveform_data_file_path):
    sound_filename = os.path.join(exercise.name, sound_filename)
    waveform_data_filename = os.path.join(exercise.name, os.path.basename(waveform_data_file_path))
    sound = Sound.objects.create(filename=sound_filename, exercise=exercise,
                                 waveform_data=waveform_data_filename)
    return sound


def copy_sound_into_media(exercise_files_path, sound_filename, dataset_path, reference_sound_file):
    """
    Copy files from source to destination
    """
    # copy the sound into media
    dst = os.path.join(exercise_files_path, sound_filename)
    src = os.path.join(dataset_path, reference_sound_file)
    shutil.copyfile(src, dst)

    return dst
