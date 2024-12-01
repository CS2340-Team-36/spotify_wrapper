# Generated by Django 5.1 on 2024-11-29 23:18

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_rename_ser_userspotifydata_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='userspotifydata',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='userspotifydata',
            name='top_artists',
            field=models.JSONField(default=list),
        ),
        migrations.AddField(
            model_name='userspotifydata',
            name='top_genres',
            field=models.JSONField(default=list),
        ),
        migrations.AlterField(
            model_name='userspotifydata',
            name='wrap_name',
            field=models.CharField(max_length=255),
        ),
    ]