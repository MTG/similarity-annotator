import os
import json
import py3gearman
import logging
import zipfile

from django.core.management.base import BaseCommand
from django.conf import settings
from annotationapp.models import Sound
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

        # create directory for exercise audio files
        exercise_files_path = os.path.join(settings.MEDIA_ROOT, exercise_name)
        if not os.path.exists(exercise_files_path):
            os.makedirs(exercise_files_path)

        # decompress zip file into directory
        zip_ref = zipfile.ZipFile(zip_file_path, 'r')
        zip_ref.extractall(exercise_files_path)
        zip_ref.close()

        # create sound objects for each sound file in the directory
        for audio_file in os.listdir(exercise_files_path):
            print (audio_file)

    def handle(self, *args, **options):
        gm_worker = py3gearman.GearmanWorker(settings.GEARMAN_JOB_SERVERS)
        self.write_log("Starting worker\n")

        gm_worker.work()  # infinite loop (never exits)
