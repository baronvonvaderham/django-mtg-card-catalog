# Generated by Django 2.2 on 2019-04-04 13:32

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('card_catalog', '0007_cardprice'),
    ]

    operations = [
        migrations.AlterField(
            model_name='card',
            name='set',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='card_catalog.CardSet'),
        ),
        migrations.AlterField(
            model_name='cardprice',
            name='card',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='card_catalog.Card'),
        ),
        migrations.AlterField(
            model_name='cardprice',
            name='date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
