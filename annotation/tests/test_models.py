
from django.test import TestCase, Client

from django.contrib.auth.models import User
from annotation.models import DataSet, Exercise, Tier, Sound, Annotation


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


class SoundModelTests(TestCase):

    def setUp(self):
        data_set_name = 'test_data_set_2'
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

        self.reference_sound_2 = Sound.objects.create(filename='reference sound', exercise=self.exercise,
                                                      original_filename='')
        self.sound = Sound.objects.create(filename='test sound', exercise=self.exercise, original_filename='')

    def test_get_annotations_from_sound(self):
        annotations = self.sound.get_annotations_as_dict()

        self.assertTrue(isinstance(annotations, dict))
        self.assertEqual(annotations, {})

        # create tier for annotations
        tier = Tier.objects.create(name='test tier', exercise=self.exercise)
        # create annotations
        start_time = 1
        end_time = 2
        annotation_1 = Annotation.objects.create(start_time=start_time, end_time=end_time, sound=self.sound,
                                                 tier=tier, user=self.user)
        annotations = self.sound.get_annotations_as_dict()

        self.assertTrue(isinstance(annotations, dict))
        self.assertTrue('test tier' in annotations.keys())
        self.assertEqual(len(annotations['test tier']), 1)
        self.assertEqual(annotations['test tier'][0]['start_time'], annotation_1.start_time)
        self.assertEqual(annotations['test tier'][0]['end_time'], annotation_1.end_time)

    def test_get_annotations_for_tier(self):
        # create tier for annotations
        tier = Tier.objects.create(name='test tier', exercise=self.exercise)
        annotations = self.sound.get_annotations_for_tier(tier)
        self.assertFalse(annotations)

        # create annotations
        start_time = 1
        end_time = 2
        annotation_1 = Annotation.objects.create(start_time=start_time, end_time=end_time, sound=self.sound,
                                                 tier=tier, user=self.user)
        annotations = self.sound.get_annotations_for_tier(tier)
        self.assertTrue(isinstance(annotations, list))
        self.assertTrue(isinstance(annotations[0], dict))
        self.assertEqual(annotations[0]['start'], annotation_1.start_time)
        self.assertEqual(annotations[0]['end'], annotation_1.end_time)
        self.assertEqual(annotations[0]['annotation'], annotation_1.name)

    def test_update_annotations(self):
        # create annotation data as it is done in the interface
        new_annotations = [{
            "annotation": "",
            "end": 20,
            "id": "",
            "similarity": "",
            "start": 10
        }]
        tier = Tier.objects.create(name='test tier', exercise=self.exercise)
        self.sound.update_annotations(tier, new_annotations, self.user)
        # as the annotation didn't exist previously, a new annotation should be created
        self.assertTrue(self.sound.annotations.all())
        self.assertEqual(self.sound.annotations.all()[0].start_time, new_annotations[0]["start"])
        self.assertEqual(self.sound.annotations.all()[0].end_time, new_annotations[0]["end"])
        self.assertFalse(self.sound.annotations.all()[0].name)

        # update previous annotation
        new_annotations = [{
            "annotation": "new",
            "end": 20,
            "id": self.sound.annotations.all()[0].id,
            "similarity": "",
            "start": 10
        }]
        self.sound.update_annotations(tier, new_annotations, self.user)

        self.assertEqual(self.sound.annotations.all().count(), 1)
        self.assertEqual(self.sound.annotations.all()[0].start_time, new_annotations[0]["start"])
        self.assertEqual(self.sound.annotations.all()[0].end_time, new_annotations[0]["end"])
        self.assertEqual(self.sound.annotations.all()[0].name, new_annotations[0]["annotation"])

    def test_update_annotations_when_sync_tier(self):
        tier = Tier.objects.create(name='parent', exercise=self.exercise)
        sync_tier = Tier.objects.create(name='son', exercise=self.exercise, parent_tier=tier)

        new_annotations = [{
            "annotation": "",
            "end": 20,
            "id": "",
            "similarity": "",
            "start": 10
        }]

        self.sound.update_annotations(tier, new_annotations, self.user)

        # One annotation should be created in both tiers, as they are sync

        tier_annotations = self.sound.get_annotations_for_tier(tier)
        sync_tier_annotations = self.sound.get_annotations_for_tier(sync_tier)

        self.assertEqual(len(tier_annotations), len(sync_tier_annotations))
        self.assertEqual(tier_annotations[0]['start'], sync_tier_annotations[0]['start'])
        self.assertEqual(tier_annotations[0]['end'], sync_tier_annotations[0]['end'])

        # If an annotation in one tier is modified, it should be also modified in the sync tier

        new_annotations = [{
            "annotation": "",
            "id": self.sound.annotations.filter(tier=tier).all()[0].id,
            "start": 5,
            "end": 20,
            "similarity": ""
        }]
        self.sound.update_annotations(tier, new_annotations, self.user)

        tier_annotations = self.sound.get_annotations_for_tier(tier)
        sync_tier_annotations = self.sound.get_annotations_for_tier(sync_tier)
        self.assertEqual(len(tier_annotations), len(sync_tier_annotations))
        self.assertEqual(tier_annotations[0]['start'], sync_tier_annotations[0]['start'])
        self.assertEqual(tier_annotations[0]['end'], sync_tier_annotations[0]['end'])
        self.assertEqual(tier_annotations[0]['start'], new_annotations[0]['start'])
        self.assertEqual(tier_annotations[0]['end'], new_annotations[0]['end'])

        # The sync modification should work both ways

        new_annotations = [{
            "annotation": "",
            "id": self.sound.annotations.filter(tier=sync_tier).all()[0].id,
            "start": 5,
            "end": 10,
            "similarity": ""
        }]

        self.sound.update_annotations(sync_tier, new_annotations, self.user)
        tier_annotations = self.sound.get_annotations_for_tier(tier)
        sync_tier_annotations = self.sound.get_annotations_for_tier(sync_tier)
        self.assertEqual(len(tier_annotations), len(sync_tier_annotations))
        self.assertEqual(tier_annotations[0]['start'], sync_tier_annotations[0]['start'])
        self.assertEqual(tier_annotations[0]['end'], sync_tier_annotations[0]['end'])
        self.assertEqual(tier_annotations[0]['start'], new_annotations[0]['start'])
        self.assertEqual(tier_annotations[0]['end'], new_annotations[0]['end'])

    def test_update_annotations_when_parent_tier(self):
        parent_tier = Tier.objects.create(name='parent', exercise=self.exercise)
        son_tier = Tier.objects.create(name='son', exercise=self.exercise, special_parent_tier=parent_tier)

        new_annotations = [{
            "annotation": "",
            "start": 1,
            "end": 2,
            "id": "",
            "similarity": "",
        }]

        # create annotation in parent should also create annotation in son
        self.sound.update_annotations(parent_tier, new_annotations, self.user)
        parent_tier_annotations = self.sound.get_annotations_for_tier(parent_tier)
        son_tier_annotations = self.sound.get_annotations_for_tier(son_tier)
        self.assertEqual(len(parent_tier_annotations), len(son_tier_annotations))
        self.assertEqual(parent_tier_annotations[0]['start'], son_tier_annotations[0]['start'])
        self.assertEqual(parent_tier_annotations[0]['end'], son_tier_annotations[0]['end'])
        self.assertEqual(son_tier_annotations[0]['start'], new_annotations[0]['start'])
        self.assertEqual(son_tier_annotations[0]['end'], new_annotations[0]['end'])
        