# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-11-07 17:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('card_catalog', '0002_scryfallcard'),
    ]

    operations = [
        migrations.AlterField(
            model_name='card',
            name='cmc',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name='scryfallcard',
            name='cmc',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
    ]
