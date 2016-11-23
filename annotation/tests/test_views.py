from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from annotation.models import Exercise


class ExerciseListViewTests(TestCase):

    def setUp(self):
        exercise_name = 'test_exercise'
        self.exercise = Exercise.objects.create(name=exercise_name)
        self.username = 'test'
        self.password = '1234567'
        self.user = User.objects.create_user(self.username, '', self.password)

    def test_exercise_list(self):

        response = self.client.get('')
        self.assertEqual(response.status_code, 302)
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('exercise_list'))
        self.assertEqual(response.status_code, 200)
        exercise_list = response.context['exercises_list']
        self.assertTrue(self.exercise in exercise_list)
