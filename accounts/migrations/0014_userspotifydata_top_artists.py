# Generated by Django 5.1 on 2024-11-30 22:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0013_userspotifydata_top_genres'),
    ]

    operations = [
        migrations.AddField(
            model_name='userspotifydata',
            name='top_artists',
            field=models.JSONField(blank=True, null=True),
        ),
    ]