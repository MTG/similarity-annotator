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

    def test_exercise_list(self):

        client = Client()
        client.login(username=self.username, password=self.password)
        response = client.get(reverse('exercise_list', kwargs={'dataset_id': self.data_set.id}))
        self.assertEqual(response.status_code, 200)
        exercise_list = response.context['exercises_list']
        self.assertTrue(self.exercise in exercise_list)
