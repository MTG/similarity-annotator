from __future__ import unicode_literals

from django.db import models


class Tier(models.Model):
    name = models.CharField(max_length=50)


class Dataset(models.Model):
    name = models.CharField(max_length=50)
    tiers = models.ManyToManyField(Tier)


class Sound(models.Model):
    filename = models.CharField(max_length=200)
    dataset = models.ForeignKey(Dataset, related_name='sounds')
