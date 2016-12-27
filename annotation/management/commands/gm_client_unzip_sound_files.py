import py3gearman
import json
import logging

from django.conf import settings
from django.core.management.base import BaseCommand

logger = logging.getLogger("gearman_client_unzip_sound_files")


class Command(BaseCommand):
    """
    Send jobs to gearman job server
    """

    help = 'Unzip sounds via gearman'

    def handle(self, *args, **options):
        # create a client and connect it to GM server
        gm_client = py3gearman.GearmanClient(settings.GEARMAN_JOB_SERVERS)

        file_path = options['file_path']
        dataset_name = options['dataset_name']
        exercise_name = options['exercise_name']

        # Generate a job
        data = json.dumps({'file_path': file_path, 'dataset_name': dataset_name, 'exercise_name': exercise_name})

        # For the to-be-analyzed sounds, create a job and send it to the gearman server
        gm_client.submit_job('unzip_sound_files', data, background=True, wait_until_complete=False)
