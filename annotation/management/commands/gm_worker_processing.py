import os
import json
import py3gearman
import logging

from django.core.management.base import BaseCommand
from django.conf import settings
from annotation.models import Exercise, Tier
import annotation.utils

logger = logging.getLogger("gearman_worker_processing")


class Command(BaseCommand):
    """
    Receive jobs from gearman jobserver
    """

    help = "Analyze sounds received via Gearman"

    @staticmethod
    def write_log(msg):
        logger.info("[%d] %s" % (os.getpid(), msg))

    def unzip_sound_files(self, gearman_worker, gearman_job):
        """
        Create directory for the audio files of an exercise, decompress audio files into it and create sound objects
        """
        data = json.loads(gearman_job.data)
        zip_file_path = data['file_path']
        exercise_name = data['exercise_name']

        self.write_log("Decompressing file for exercise %s" % exercise_name)

        exercise_files_path = annotation.utils.decompress_files(exercise_name, zip_file_path)

        exercise = Exercise.objects.get(name=exercise_name)
        # create initial tier "whole sound"
        Tier.objects.create(name="entire sound", exercise=exercise, entire_sound=True)
        for sound_filename in os.listdir(exercise_files_path):
            waveform_data_file_path = annotation.utils.create_audio_waveform(exercise_files_path, sound_filename)
            sound = annotation.utils.create_sound_object(exercise, sound_filename, waveform_data_file_path)
            self.write_log("Created sound object %s for sound file %s" % (str(sound.id), sound_filename))
        return "Done"

    def handle(self, *args, **options):
        gm_worker = py3gearman.GearmanWorker(settings.GEARMAN_JOB_SERVERS)
        gm_worker.register_task('unzip_sound_files', self.unzip_sound_files)
        self.write_log("Starting worker\n")

        gm_worker.work()  # infinite loop (never exits)
