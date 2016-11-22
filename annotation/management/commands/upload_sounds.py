import os
import json
from django.core.management.base import BaseCommand
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
            for exercise_name in descriptions:
                # create exercise
                exercise = Exercise.objects.create(name=exercise_name)
                exercise_files_path = annotation.utils.create_exercise_directory(exercise_name)
                # create initial tier "whole sound"
                Tier.objects.create(name="entire sound", exercise=exercise, entire_sound=True)
                # create reference sound
                try:
                    reference_sound_file = descriptions[exercise_name]['ref_media']
                    sound_filename = os.path.basename(reference_sound_file)
                    sound_path = os.path.join(dataset_path, os.path.dirname(reference_sound_file))
                    waveform_data_file_path = annotation.utils.create_audio_waveform(sound_path, sound_filename)
                    reference_sound = annotation.utils.create_sound_object(exercise, sound_filename,
                                                                           waveform_data_file_path)
                    exercise.reference_sound = reference_sound
                    exercise.save()
                    # copy the sound into media
                    annotation.utils.copy_sound_into_media(exercise_files_path, sound_filename,
                                                           dataset_path, reference_sound_file)
                    print ("Created sound reference for exercise %s" % exercise_name)
                except KeyError:
                    print ("The exercise %s does not have reference sound" % exercise_name)

                # create pitch reference file
                try:
                    reference_pitch_file = descriptions[exercise_name]['tanpura']
                    # copy the sound into media
                    destination_path = annotation.utils.copy_sound_into_media(exercise_files_path, sound_filename,
                                                                              dataset_path, reference_pitch_file)
                    exercise.reference_pitch_sound.name = destination_path
                    exercise.save()
                    print ("Created pitch reference for exercise %s" % exercise_name)
                except KeyError:
                    print ("The exercise %s does not have a pitch reference")

                for sound_description in descriptions[exercise_name]['recs']:
                    try:
                        sound_file_path = sound_description['path']
                        sound_filename = os.path.basename(sound_file_path)
                        sound_path = os.path.join(dataset_path, os.path.dirname(sound_file_path))
                        waveform_data_file_path = annotation.utils.create_audio_waveform(sound_path, sound_filename)
                        sound = annotation.utils.create_sound_object(exercise, sound_filename, waveform_data_file_path)
                        # copy the sound into media
                        annotation.utils.copy_sound_into_media(exercise_files_path, sound_filename,
                                                               dataset_path, reference_sound_file)
                        print ("Created sound %s:%s of exercise %s" % (sound.id, sound_filename, exercise_name))
                    except Exception as e:
                        print (e.message)


