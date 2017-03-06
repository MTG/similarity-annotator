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

    # Update annotations to test annotation_state update correctly
    def test_update_annotations(self):
        annotations = [{'id': 1, 'start': 1, 'end': 2, 'annotation': 'name', 'similarity': 'no'}]
        self.reference_sound.update_annotations(self.tier, annotations, self.user)

        annotations = [{'id': 4, 'start': 1, 'end': 2, 'similarity': 'no', 'annotation': 'name'}]

        self.assertEqual(self.sound.annotations.count(), 0)
        self.assertEqual(self.sound.annotation_state, 'E')
        self.sound.update_annotations(self.tier, annotations, self.user)
        self.assertEqual(self.sound.annotations.count(), 1)

        self.assertEqual(self.sound.annotation_state, 'I')
        annotations = [{'id': 4, 'start': 1, 'end': 2, 'reference': 3,
                        'similarity': 'yes', 'annotation': 'name', 'similValue': 1}]

        self.sound.update_annotations(self.tier, annotations, self.user)
        self.assertEqual(self.sound.annotations.count(), 1)
        self.assertEqual(self.sound.annotation_state, 'C')

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

    def test_download_annotations_for_exercise(self):
        annotation_name = 'test_annotation'
        start_time = 10
        end_time = 20
        reference_annotation = Annotation.objects.create(name=annotation_name, start_time=start_time, end_time=end_time,
                                                         sound=self.reference_sound, tier=self.tier, user=self.user)

        exercise_annotations = annotation.utils.exercise_annotations_to_json(self.exercise.id)
        exercise_annotations_json = json.loads(exercise_annotations)

        # the utils should retrieve a json serialisation
        self.assertTrue(isinstance(exercise_annotations, str))
        # the sounds file names should be in the dictionary
        self.assertTrue(self.sound.filename in exercise_annotations_json.keys())
        self.assertTrue(self.reference_sound.filename in exercise_annotations_json.keys())
        # the tier name should be a key in the sound
        self.assertTrue(self.tier.name in exercise_annotations_json[self.reference_sound.filename].keys())
        # there should be one annotation in the tier of the reference sound
        self.assertEqual(len(exercise_annotations_json[self.reference_sound.filename][self.tier.name]),
                1)
        # the annotation should have the attributes defined in here
        self.assertEqual(exercise_annotations_json[self.reference_sound.filename][self.tier.name][0]['start_time'],
                         start_time)
        self.assertEqual(exercise_annotations_json[self.reference_sound.filename][self.tier.name][0]['end_time'],
                         end_time)

        # test annotation similarities download
        annotation_name_2 = 'test_annotation_2'
        start_time_2 = 10
        end_time_2 = 20
        similarity_measure = {'value': 1}
        similar_annotation = Annotation.objects.create(name=annotation_name_2, start_time=start_time_2,
                                                       end_time=end_time_2, sound=self.sound, tier=self.tier,
                                                       user=self.user)
        AnnotationSimilarity.objects.create(reference=reference_annotation, similar_sound=similar_annotation,
                                            similarity=similarity_measure, user=self.user)

        exercise_annotations = annotation.utils.exercise_annotations_to_json(self.exercise.id)
        exercise_annotations_json = json.loads(exercise_annotations)

        # check if the annotation similarity is in the json serialisation
        self.assertEqual(exercise_annotations_json[self.sound.filename][self.tier.name][0]['similarity']
                         ['reference_annotation_start_time'], start_time)
        self.assertEqual(exercise_annotations_json[self.sound.filename][self.tier.name][0]['similarity']
                         ['reference_annotation_end_time'], end_time)



