import json

from django.test import TestCase
from django.contrib.auth.models import User

from annotation.models import DataSet, Exercise, Tier, Sound, Annotation, AnnotationSimilarity
import annotation.utils


class CreateSoundTest(TestCase):

    def setUp(self):
        username = 'test'
        password = '1234567'
        self.user = User.objects.create_user(username, '', password)

        data_set_name = 'test_data_set'
        self.data_set = DataSet.objects.create(name=data_set_name)

        exercise_name = 'test_exercise'
        self.exercise = Exercise.objects.create(name=exercise_name, data_set=self.data_set)

        tier_name = 'test_tier'
        self.tier = Tier.objects.create(name=tier_name, exercise=self.exercise)

        sound_filename = 'test_sound.wav'
        sound_original_filename = '/directory/%s' % sound_filename
        self.sound = Sound.objects.create(filename=sound_filename, exercise=self.exercise,
                                          original_filename=sound_original_filename)

        sound_reference_filename = 'reference_test_sound.wav'
        original_sound_reference_filename = '/directory/%s' % sound_reference_filename
        self.reference_sound = Sound.objects.create(filename=sound_reference_filename, exercise=self.exercise,
                                                    original_filename=original_sound_reference_filename)

        self.exercise.reference_sound = self.reference_sound
        self.exercise.save()

    def test_sound_creation(self):
        sound_filename_2 = 'test_sound_2.wav'
        sound_original_filename_2 = '/directory/%s' % sound_filename_2
        sounds_before_creation = Sound.objects.all().count()
        sound = annotation.utils.get_or_create_sound_object(self.exercise, sound_filename_2, sound_original_filename_2)
        sounds_after_creation = Sound.objects.all().count()

        self.assertTrue(sound in Sound.objects.all())
        self.assertNotEqual(sounds_before_creation, sounds_after_creation)
        self.assertEqual(sound.original_filename, sound_original_filename_2)
        self.assertEqual(sound.filename, sound_filename_2)

    def test_download_annotations(self):
        annotation_name = 'test_annotation'
        start_time = 10
        end_time = 20
        Annotation.objects.create(name=annotation_name, start_time=start_time, end_time=end_time,
                                  sound=self.reference_sound, tier=self.tier, user=self.user)

        exercise_annotations = annotation.utils.exercise_annotations_to_json(self.exercise.id)
        exercise_annotations_json = json.loads(exercise_annotations)

        # the utils should retrieve a json serialisation
        self.assertEqual(type(exercise_annotations), str)
        # the sounds file names should be in the dictionary
        self.assertTrue(self.sound.filename in exercise_annotations_json.keys())
        self.assertTrue(self.reference_sound.filename in exercise_annotations_json.keys())
        # the tier name should be a key in the sound
        self.assertTrue(self.tier.name in exercise_annotations_json[self.reference_sound.filename].keys())
        # it should be one annotation in the tier of the reference sound
        self.assertEqual(len(exercise_annotations_json[self.reference_sound.filename][self.tier.name]), 1)
        # the annotation should have the attributes defined in here
        self.assertEqual(exercise_annotations_json[self.reference_sound.filename][self.tier.name][0]['start_time'],
                         start_time)
        self.assertEqual(exercise_annotations_json[self.reference_sound.filename][self.tier.name][0]['end_time'],
                         end_time)
