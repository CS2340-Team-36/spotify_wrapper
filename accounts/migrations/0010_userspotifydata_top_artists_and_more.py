# Generated by Django 5.1 on 2024-11-30 18:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_remove_userspotifydata_created_at_alter_genre_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userspotifydata',
            name='top_artists',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userspotifydata',
            name='top_genres',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userspotifydata',
            name='top_tracks',
            field=models.JSONField(blank=True, null=True),
        ),
    ]