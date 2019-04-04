# Generated by Django 2.2 on 2019-04-04 16:28

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Card',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('tcg_product_id', models.CharField(max_length=64)),
                ('product_url', models.URLField(blank=True, null=True)),
                ('image_url', models.URLField(blank=True, null=True)),
                ('mana_cost', models.CharField(blank=True, max_length=128, null=True)),
                ('cmc', models.IntegerField(blank=True, null=True)),
                ('types', models.CharField(blank=True, max_length=256, null=True)),
                ('subtypes', models.CharField(blank=True, max_length=256, null=True)),
                ('colors', models.CharField(blank=True, max_length=128, null=True)),
                ('color_identity', models.CharField(blank=True, max_length=128, null=True)),
                ('oracle_text', models.CharField(blank=True, max_length=2048, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CardSet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(blank=True, max_length=10, null=True)),
                ('name', models.CharField(max_length=150)),
                ('tcgplayer_group_id', models.IntegerField()),
                ('release_date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='ScryfallCard',
            fields=[
                ('oracle_id', models.CharField(max_length=128, primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, max_length=256, null=True)),
                ('mana_cost', models.CharField(blank=True, max_length=128, null=True)),
                ('cmc', models.IntegerField(blank=True, null=True)),
                ('types', models.CharField(blank=True, max_length=256, null=True)),
                ('subtypes', models.CharField(blank=True, max_length=256, null=True)),
                ('colors', models.CharField(blank=True, max_length=128, null=True)),
                ('color_identity', models.CharField(blank=True, max_length=128, null=True)),
                ('oracle_text', models.CharField(blank=True, max_length=2048, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CardPrice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('low', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('mid', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('high', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('market', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('foil_low', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('foil_mid', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('foil_high', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('foil_market', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('card', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='card_catalog.Card')),
            ],
        ),
        migrations.AddField(
            model_name='card',
            name='set',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='card_catalog.CardSet'),
        ),
    ]
