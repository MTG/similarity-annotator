from __future__ import unicode_literals

from django.db import models


class Dataset(models.Model):
    name = models.CharField(max_lenght=50)


class Sound(models.Model):
    filename = models.CharField(max_length=200)
    dataset = models.ForeignKey(Dataset, related_name='sounds')
