from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User


class Tier(models.Model):
    name = models.CharField(max_length=50)
    related_tiers = models.ForeignKey('self', blank=True, null=True)

    def __str__(self):
        return self.name


class Dataset(models.Model):
    name = models.CharField(max_length=50)
    tiers = models.ManyToManyField(Tier, blank=True, null=True)
    users = models.ManyToManyField(User, blank=True, null=True)

    def __str__(self):
        return self.name


class Sound(models.Model):
    filename = models.CharField(max_length=200)
    dataset = models.ForeignKey(Dataset, related_name='sounds')
