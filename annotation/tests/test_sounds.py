from django.test import TestCase
from django.contrib.auth.models import User

from annotation.models import Exercise, Sound
from annotation.utils import create_sound_object


class CreateSoundTest(TestCase):

    def setUp(self):
        username = 'test'
        password = '1234567'
        self.user = User.objects.create_user(username, '', password)

        exercise_name = 'test_exercise'
        self.exercise = Exercise.objects.create(name=exercise_name)

    def test_sound_creation(self):
        sound_filename = 'test_sound.wav'
        sounds_before_creation = Sound.objects.all().count()
        sound = create_sound_object(self.exercise, sound_filename)
        sounds_after_creation = Sound.objects.all().count()

        self.assertTrue(sound in Sound.objects.all())
        self.assertNotEqual(sounds_before_creation, sounds_after_creation)
