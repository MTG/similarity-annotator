
from django.test import TestCase, Client

from django.contrib.auth.models import User
from annotation.models import DataSet, Exercise, Tier


class TierModelTests(TestCase):

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

        self.tier_1 = Tier.objects.create(name='tier_1', exercise=self.exercise)

    def test_get_special_child_tiers(self):
        special_child_tier_1 = Tier.objects.create(name='tier_2', exercise=self.exercise, special_parent_tier=self.tier_1)
        special_child_tier_2 = Tier.objects.create(name='tier_3', exercise=self.exercise,
                                                   special_parent_tier=special_child_tier_1)

        special_child_tier_1_1 = Tier.objects.create(name='tier_4', exercise=self.exercise,
                                                     special_parent_tier=self.tier_1)
        special_child_tier_2_1 = Tier.objects.create(name='tier_5', exercise=self.exercise,
                                                     special_parent_tier=special_child_tier_1_1)

        list_of_special_child_tiers = self.tier_1.get_special_child_tiers()

        self.assertTrue(special_child_tier_1 in list_of_special_child_tiers)
        self.assertTrue(special_child_tier_2 in list_of_special_child_tiers)
        self.assertTrue(special_child_tier_1_1 in list_of_special_child_tiers)
        self.assertTrue(special_child_tier_2_1 in list_of_special_child_tiers)

    def test_get_child_tiers(self):
        child_tier_1 = Tier.objects.create(name='tier_2', exercise=self.exercise, parent_tier=self.tier_1)
        child_tier_2 = Tier.objects.create(name='tier_3', exercise=self.exercise, parent_tier=child_tier_1)
        child_tier_1_1 = Tier.objects.create(name='tier_4', exercise=self.exercise, parent_tier=self.tier_1)
        child_tier_2_1 = Tier.objects.create(name='tier_5', exercise=self.exercise, parent_tier=child_tier_1_1)

        list_of_child_tiers = self.tier_1.get_child_tiers()

        self.assertTrue(child_tier_1 in list_of_child_tiers)
        self.assertTrue(child_tier_2 in list_of_child_tiers)
        self.assertTrue(child_tier_1_1 in list_of_child_tiers)
        self.assertTrue(child_tier_2_1 in list_of_child_tiers)

    def test_get_special_parent_tiers(self):
        special_child_tier_1 = Tier.objects.create(name='tier_2', exercise=self.exercise,
                                                   special_parent_tier=self.tier_1)
        special_child_tier_2 = Tier.objects.create(name='tier_3', exercise=self.exercise,
                                                   special_parent_tier=special_child_tier_1)

        list_of_special_parent_tiers = special_child_tier_2.get_special_parent_tiers()

        self.assertTrue(special_child_tier_1 in list_of_special_parent_tiers)
        self.assertTrue(self.tier_1 in list_of_special_parent_tiers)

