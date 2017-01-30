# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-01-20 17:22
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('annotation', '0007_auto_20170120_1704'),
    ]

    operations = [
        migrations.AddField(
            model_name='annotationsimilarity',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='annotationsimilarity',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]