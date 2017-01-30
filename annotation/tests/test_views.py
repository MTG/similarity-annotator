from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from annotation.models import DataSet, Exercise


class ExerciseListViewTests(TestCase):

    def setUp(self):
        data_set_name = 'test_data_set'
        self.data_set = DataSet.objects.create(name=data_set_name)
        exercise_name = 'test_exercise'
        self.exercise = Exercise.objects.create(data_set=self.data_set, name=exercise_name)
        self.username = 'test'
        self.password = '1234567'

        self.user = User.objects.create(username=self.username)
        self.user.set_password(self.password)
        self.user.save()

        self.test_client = Client()
        self.test_client.login(username=self.username, password=self.password)

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
