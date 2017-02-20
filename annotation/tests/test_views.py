import os

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.conf import settings
from annotation.models import DataSet, Exercise, Sound, Tier, Annotation, AnnotationSimilarity


class ExerciseListViewTests(TestCase):

    def setUp(self):
        data_set_name = 'test_data_set'
        self.data_set = DataSet.objects.create(name=data_set_name)
        exercise_name = 'test_exercise'
        self.exercise = Exercise.objects.create(data_set=self.data_set, name=exercise_name)

        username = 'test'
        password = '1234567'
        self.user = User.objects.create(username=username)
        self.user.set_password(password)
        self.user.save()

        self.test_client = Client()
        self.test_client.login(username=username, password=password)

    def test_exercise_list_succeed(self):

        response = self.test_client.get(reverse('exercise_list', kwargs={'dataset_id': self.data_set.id}))
        self.assertEqual(response.status_code, 200)
        exercise_list = response.context['exercises_list']
        self.assertTrue(self.exercise in exercise_list)
        self.assertTrue(len(exercise_list), 1)

    def test_exercise_list_not_logged(self):
        response = self.client.get(reverse('exercise_list', kwargs={'dataset_id': self.data_set.id}))
        # if the client is not logged it should be redirected to login
        self.assertEqual(response.status_code, 302)
        self.assertTrue('accounts/login' in response.url)

    def test_exercise_list_order(self):
        exercise_2 = Exercise.objects.create(data_set=self.data_set, name='test_exercise_2')
        response = self.test_client.get(reverse('exercise_list', kwargs={'dataset_id': self.data_set.id}))
        self.assertEqual(response.context['exercises_list'][0], exercise_2)
        self.assertEqual(response.context['exercises_list'][1], self.exercise)

    def test_exercises_list_data_set_id(self):
        response = self.test_client.get(reverse('exercise_list', kwargs={'dataset_id': self.data_set.id}))
        self.assertEqual(response.context['dataset_id'], str(self.data_set.id))


class DataSetListViewTests(TestCase):
    def setUp(self):
        data_set_name = 'test_data_set'
        self.data_set = DataSet.objects.create(name=data_set_name)

        username = 'test'
        password = '1234567'
        self.user = User.objects.create(username=username)
        self.user.set_password(password)
        self.user.save()

        self.test_client = Client()
        self.test_client.login(username=username, password=password)

    def test_data_set_list_not_logged(self):
        response = self.client.get(reverse('data_set_list'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue('accounts/login' in response.url)

    def test_data_set_list_no_user(self):
        response = self.test_client.get(reverse('data_set_list'))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.data_set in response.context['data_sets_list'])

    def test_data_set_list_user(self):
        self.data_set.users.add(self.user)
        self.data_set.save()
        response = self.test_client.get(reverse('data_set_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.data_set in response.context['data_sets_list'])


class TierListViewTests(TestCase):
    def setUp(self):
        data_set_name = 'test_data_set'
        self.data_set = DataSet.objects.create(name=data_set_name)

        exercise_name = 'test_exercise'
        self.exercise = Exercise.objects.create(data_set=self.data_set, name=exercise_name)

        tier_name = 'test_tier'
        self.tier = Tier.objects.create(name=tier_name, exercise=self.exercise)

        username = 'test'
        password = '1234567'
        self.user = User.objects.create(username=username)
        self.user.set_password(password)
        self.user.save()

        self.test_client = Client()
        self.test_client.login(username=username, password=password)

        sound_filename = 'test_sound'
        self.sound = Sound.objects.create(filename=sound_filename, original_filename=sound_filename,
                                          exercise=self.exercise)

    def test_tier_list_not_logged(self):
        response = self.client.get(reverse('tier_list', kwargs={'exercise_id': self.exercise.id,
                                                                'sound_id': self.sound.id}))
        self.assertEqual(response.status_code, 302)

    def test_tier_list(self):
        response = self.test_client.get(reverse('tier_list', kwargs={'exercise_id': self.exercise.id,
                                                                     'sound_id': self.sound.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.tier in response.context['tiers_list'])
        self.assertEqual(self.exercise, response.context['exercise'])
        self.assertEqual(self.sound, response.context['sound'])

    def test_tier_list_reference_sound(self):
        reference_sound = Sound.objects.create(filename='test_reference_sound', original_filename='',
                                               exercise=self.exercise)
        self.exercise.reference_sound = reference_sound
        self.exercise.save()
        response = self.test_client.get(reverse('tier_list', kwargs={'exercise_id': self.exercise.id,
                                                                     'sound_id': reference_sound.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.tier in response.context['tiers_list'])
        self.assertEqual(self.exercise, response.context['exercise'])
        self.assertEqual(reference_sound, response.context['sound'])
        self.assertTrue(response.context['reference_sound'])

    def test_tier_list_post_empty(self):
        response = self.test_client.post(reverse('tier_list', kwargs={'exercise_id': self.exercise.id,
                                                                      'sound_id': self.sound.id}), {})
        self.assertFormError(response, 'form', 'name', 'This field is required.')

    def test_tier_list_post(self):
        post_data = {'name': 'new_test_tier', 'parent_tier': None}
        response = self.test_client.post(reverse('tier_list', kwargs={'exercise_id': self.exercise.id,
                                                                      'sound_id': self.sound.id}), post_data)
        self.assertEqual(response.status_code, 200)


class SoundListViewTests(TestCase):
    def setUp(self):
        data_set_name = 'test_data_set'
        self.data_set = DataSet.objects.create(name=data_set_name)

        exercise_name = 'test_exercise'
        self.exercise = Exercise.objects.create(data_set=self.data_set, name=exercise_name)

        tier_name = 'test_tier'
        self.tier = Tier.objects.create(name=tier_name, exercise=self.exercise)

        username = 'test'
        password = '1234567'
        self.user = User.objects.create(username=username)
        self.user.set_password(password)
        self.user.save()

        self.test_client = Client()
        self.test_client.login(username=username, password=password)

        sound_filename = 'test_sound'
        self.sound = Sound.objects.create(filename=sound_filename, original_filename=sound_filename,
                                          exercise=self.exercise)

    def test_sound_list_not_logged(self):
        response = self.client.get(reverse('sound_list', kwargs={'exercise_id': self.exercise.id}))
        self.assertEqual(response.status_code, 302)

    def test_sound_list_get_no_reference(self):
        response = self.test_client.get(reverse('sound_list', kwargs={'exercise_id': self.exercise.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.sound in response.context['sounds_list'])
        self.assertFalse('reference_sound' in response.context.keys())

    def test_sound_list_get_reference(self):
        reference_sound = Sound.objects.create(filename='reference_sound', original_filename='', exercise=self.exercise)
        self.exercise.reference_sound = reference_sound
        self.exercise.save()
        response = self.test_client.get(reverse('sound_list', kwargs={'exercise_id': self.exercise.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(reference_sound == response.context['reference_sound'])

    def test_sound_list_post(self):
        reference_sound = Sound.objects.create(filename='reference_sound', original_filename='', exercise=self.exercise)
        post_data = {'reference sound': reference_sound.id}
        response = self.test_client.post(reverse('sound_list', kwargs={'exercise_id': self.exercise.id}), post_data)
        self.assertEqual(response.status_code, 200)
        exercise = Exercise.objects.get(id=self.exercise.id)
        self.assertEqual(exercise.reference_sound, reference_sound)


class SoundDetailViewTests(TestCase):
    def setUp(self):
        data_set_name = 'test_data_set'
        self.data_set = DataSet.objects.create(name=data_set_name)

        exercise_name = 'test_exercise'
        self.exercise = Exercise.objects.create(data_set=self.data_set, name=exercise_name)

        tier_name = 'test_tier'
        self.tier = Tier.objects.create(name=tier_name, exercise=self.exercise)

        username = 'test'
        password = '1234567'
        self.user = User.objects.create(username=username)
        self.user.set_password(password)
        self.user.save()

        self.test_client = Client()
        self.test_client.login(username=username, password=password)

        sound_filename = 'test_sound'
        self.sound = Sound.objects.create(filename=sound_filename, original_filename=sound_filename,
                                          exercise=self.exercise)

    def test_sound_detail(self):
        response = self.test_client.get(reverse('sound_detail', kwargs={'exercise_id': self.exercise.id,
                                                                        'tier_id': self.tier.id,
                                                                        'sound_id': self.sound.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['sound'], self.sound)
        self.assertEqual(response.context['tier'], self.tier)
        # the current tier shouldn't be in other tiers list
        self.assertFalse(self.tier in response.context['other_tiers'])
        tier_2 = Tier.objects.create(name='tier_2', exercise=self.exercise)
        response = self.test_client.get(reverse('sound_detail', kwargs={'exercise_id': self.exercise.id,
                                                                        'tier_id': self.tier.id,
                                                                        'sound_id': self.sound.id}))
        self.assertTrue(tier_2 in response.context['other_tiers'])

    def test_sound_detail_discard_sound(self):
        # the sound is not discarded by default, so by post should change to is_discarded=True
        self.test_client.post(reverse('sound_detail', kwargs={'exercise_id': self.exercise.id,
                                                              'tier_id': self.tier.id, 'sound_id': self.sound.id}))
        sound = Sound.objects.get(id=self.sound.id)
        self.assertTrue(sound.is_discarded)
        # if is_discarded=True, a post request should change it to is_discarded=False
        self.test_client.post(reverse('sound_detail', kwargs={'exercise_id': self.exercise.id,
                                                              'tier_id': self.tier.id, 'sound_id': self.sound.id}))
        sound = Sound.objects.get(id=self.sound.id)
        self.assertFalse(sound.is_discarded)


class AnnotationActionViewTests(TestCase):
    def setUp(self):
        data_set_name = 'test_data_set'
        self.data_set = DataSet.objects.create(name=data_set_name)

        exercise_name = 'test_exercise'
        self.exercise = Exercise.objects.create(data_set=self.data_set, name=exercise_name)

        tier_name = 'test_tier'
        self.tier = Tier.objects.create(name=tier_name, exercise=self.exercise)

        username = 'test'
        password = '1234567'
        self.user = User.objects.create(username=username)
        self.user.set_password(password)
        self.user.save()

        self.test_client = Client()
        self.test_client.login(username=username, password=password)

        sound_filename = 'test_sound'
        self.sound = Sound.objects.create(filename=sound_filename, original_filename=sound_filename,
                                          exercise=self.exercise)

        self.reference_sound = Sound.objects.create(filename='reference_sound', original_filename='', exercise=self.exercise)
        self.exercise.reference_sound = self.reference_sound
        self.exercise.save()

    def test_annotation_action_get_empty(self):
        response = self.test_client.get(reverse('annotation-action', kwargs={'sound_id': self.sound.id,
                                                                             'tier_id': self.tier.id}))
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        # no segments are created
        self.assertEqual(response_data['task']['segments'], [])

        # create annotation in reference sound that should be in the response
        reference_annotation = Annotation.objects.create(name='reference_annotation', start_time=1.000, end_time=2.000,
                                                         sound=self.reference_sound, tier=self.tier, user=self.user)
        response = self.test_client.get(reverse('annotation-action', kwargs={'sound_id': self.sound.id,
                                                                             'tier_id': self.tier.id}))
        self.assertEqual(response.json()['task']['segments_ref'][0]['annotation'], reference_annotation.name)
        self.assertEqual(float(response.json()['task']['segments_ref'][0]['start']), reference_annotation.start_time)
        self.assertEqual(float(response.json()['task']['segments_ref'][0]['end']), reference_annotation.end_time)
        self.assertEqual(response.json()['task']['url'], os.path.join(settings.MEDIA_URL, self.data_set.name,
                                                                      self.exercise.name, self.sound.filename))


class DownloadAnnotationsViewTests(TestCase):
    def setUp(self):
        data_set_name = 'test_data_set'
        self.data_set = DataSet.objects.create(name=data_set_name)

        exercise_name = 'test_exercise'
        self.exercise = Exercise.objects.create(data_set=self.data_set, name=exercise_name)

        tier_name = 'test_tier'
        self.tier = Tier.objects.create(name=tier_name, exercise=self.exercise)

        username = 'test'
        password = '1234567'
        self.user = User.objects.create(username=username)
        self.user.set_password(password)
        self.user.save()

        self.test_client = Client()
        self.test_client.login(username=username, password=password)

        sound_filename = 'test_sound'
        self.sound = Sound.objects.create(filename=sound_filename, original_filename=sound_filename,
                                          exercise=self.exercise)

        self.reference_sound = Sound.objects.create(filename='reference_sound', original_filename='',
                                                    exercise=self.exercise)
        self.exercise.reference_sound = self.reference_sound
        self.exercise.save()

        self.annotation = Annotation.objects.create(name='test_annotation', start_time=1.000, end_time=2.000,
                                                         sound=self.sound, tier=self.tier, user=self.user)
        self.reference_annotation = Annotation.objects.create(name='reference_annotation', start_time=1.000,
                                                              end_time=2.000,  sound=self.reference_sound,
                                                              tier=self.tier, user=self.user)

    def test_download_annotations(self):
        annotation_similarity = AnnotationSimilarity.objects.create(reference=self.reference_annotation,
                                                                    similar_sound=self.annotation,
                                                                    similarity_measure=10, user=self.user)
        response = self.test_client.get(reverse('download-annotations', kwargs={'sound_id': self.sound.id}))

        self.assertEqual(response.json()[self.tier.name][0]['start_time'], self.annotation.start_time)
        self.assertEqual(response.json()[self.tier.name][0]['end_time'], self.annotation.end_time)
        self.assertEqual(response.json()[self.tier.name][0]['ref_start_time'],
                         self.reference_annotation.start_time)
        self.assertEqual(response.json()[self.tier.name][0]['ref_end_time'], self.reference_annotation.end_time)
        self.assertEqual(response.json()[self.tier.name][0]['value'], annotation_similarity.similarity_measure)



