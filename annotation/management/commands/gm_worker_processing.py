import os
import json
import py3gearman
import logging
import subprocess

from django.core.management.base import BaseCommand
from django.conf import settings
from annotation.models import Sound, Exercise, Tier
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
        for sound_file in os.listdir(exercise_files_path):
            # create wave form data with audiowaveform
            waveform_data_filename = os.path.splitext(sound_file)[0] + '.dat'
            waveform_data_file_path = os.path.join(exercise_files_path, waveform_data_filename)
            subprocess_result = subprocess.call(["audiowaveform", "-i", os.path.join(exercise_files_path, sound_file),
                                                 "-o", waveform_data_file_path, "-b", "8"])
            if not subprocess_result:
                sound_filename = os.path.join(exercise_name, sound_file)
                waveform_data_filename = os.path.join(exercise_name, os.path.basename(waveform_data_file_path))
                sound = Sound.objects.create(filename=sound_filename, exercise=exercise,
                                             waveform_data=waveform_data_filename)
                self.write_log("Created sound object %s for sound file %s" % (str(sound.id), sound_file))

        return "Done"

    def handle(self, *args, **options):
        gm_worker = py3gearman.GearmanWorker(settings.GEARMAN_JOB_SERVERS)
        gm_worker.register_task('unzip_sound_files', self.unzip_sound_files)
        self.write_log("Starting worker\n")

        gm_worker.work()  # infinite loop (never exits)
