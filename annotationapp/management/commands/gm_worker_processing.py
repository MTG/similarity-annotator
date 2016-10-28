import os
import json
import py3gearman
import logging
import zipfile
import shutil

from django.core.management.base import BaseCommand
from django.conf import settings
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

        return "Done"

    def handle(self, *args, **options):
        gm_worker = py3gearman.GearmanWorker(settings.GEARMAN_JOB_SERVERS)
        gm_worker.register_task('unzip_sound_files', self.unzip_sound_files)
        self.write_log("Starting worker\n")

        gm_worker.work()  # infinite loop (never exits)
