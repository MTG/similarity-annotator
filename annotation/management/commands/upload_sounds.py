import os
import json
from django.core.management.base import BaseCommand
from django.conf import settings
from annotation.models import Exercise, Tier
import annotation.utils


class Command(BaseCommand):
    """
    Upload sounds from a directory
    """

    help = 'Upload sounds from a given directory'

    @staticmethod
    def add_arguments(parser):
        parser.add_argument('path', type=str, default=False, help='path to dataset')

        parser.add_argument('description', type=str, default=False, help='description file')

    def handle(self, *args, **options):
        dataset_path = options['path']
        if options['description']:
            description_file_path = os.path.join(dataset_path, options['description'])
            descriptions = json.load(open(description_file_path))
            for exercise_name, exercise_description in descriptions.items():
                # create exercise
                exercise = Exercise.objects.create(name=exercise_name)
                exercise_files_path = annotation.utils.create_exercise_directory(exercise_name)
                # create initial tier "whole sound"
                Tier.objects.create(name="entire sound", exercise=exercise, entire_sound=True)
                # create reference sound
                try:
                    reference_sound_file_relative_path = exercise_description['ref_media']
                    source_path = os.path.join(dataset_path, reference_sound_file_relative_path)
                    reference_sound_filename = os.path.basename(reference_sound_file_relative_path)

                    # copy the sound into media
                    annotation.utils.copy_sound_into_media(source_path, exercise_name, reference_sound_filename)

                    waveform_data_file_path = annotation.utils.create_audio_waveform(exercise_files_path,
                                                                                     reference_sound_filename)
                    reference_sound = annotation.utils.create_sound_object(exercise, reference_sound_filename,
                                                                           waveform_data_file_path)
                    exercise.reference_sound = reference_sound
                    exercise.save()
                    print ("Created sound reference for exercise %s" % exercise_name)
                except KeyError:
                    print ("The exercise %s does not have reference sound" % exercise_name)

                # create pitch reference file
                try:
                    reference_pitch_file_relative_path = exercise_description['tanpura']
                    source_path = os.path.join(dataset_path, reference_pitch_file_relative_path)
                    reference_pitch_filename = os.path.basename(reference_sound_file_relative_path)
                    # copy the file into media
                    destination_path = annotation.utils.copy_sound_into_media(source_path, exercise_name,
                                                                              reference_pitch_filename)
                    exercise.reference_pitch_sound.name = destination_path
                    exercise.save()
                    print ("Created pitch reference for exercise %s" % exercise_name)
                except KeyError:
                    print ("The exercise %s does not have a pitch reference")

                for sound_description in exercise_description['recs']:
                    try:
                        sound_file_relative_path = sound_description['path']
                        source_path = os.path.join(dataset_path, sound_file_relative_path)
                        sound_filename = os.path.basename(sound_file_relative_path)

                        # copy the sound into media
                        annotation.utils.copy_sound_into_media(source_path, exercise_name, sound_filename)

                        waveform_data_file_path = annotation.utils.create_audio_waveform(exercise_files_path,
                                                                                         sound_filename)
                        sound = annotation.utils.create_sound_object(exercise, sound_filename, waveform_data_file_path)

                        print ("Created sound %s:%s of exercise %s" % (sound.id, sound_filename, exercise_name))
                    except Exception as e:
                        print (e.message)


