# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-11-13 21:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('card_catalog', '0005_auto_20181113_2133'),
    ]

    operations = [
        migrations.AlterField(
            model_name='card',
            name='cmc',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='scryfallcard',
            name='cmc',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
