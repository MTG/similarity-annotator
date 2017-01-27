from django.test import TestCase
from django.contrib.auth.models import User

from annotation.models import DataSet, Exercise, Sound
from annotation.utils import get_or_create_sound_object


class CreateSoundTest(TestCase):

    def setUp(self):
        username = 'test'
        password = '1234567'
        self.user = User.objects.create_user(username, '', password)

        data_set_name = 'test_data_set'
        self.data_set = DataSet.objects.create(name=data_set_name)

        exercise_name = 'test_exercise'
        self.exercise = Exercise.objects.create(name=exercise_name, data_set=self.data_set)

    def test_sound_creation(self):
        sound_filename = 'test_sound.wav'
        sound_original_filename = '/directory/%s' % sound_filename
        sounds_before_creation = Sound.objects.all().count()
        sound = get_or_create_sound_object(self.exercise, sound_filename, sound_original_filename)
        sounds_after_creation = Sound.objects.all().count()

        self.assertTrue(sound in Sound.objects.all())
        self.assertNotEqual(sounds_before_creation, sounds_after_creation)
        self.assertEqual(sound.original_filename, sound_original_filename)
        self.assertEqual(sound.filename, sound_filename)


