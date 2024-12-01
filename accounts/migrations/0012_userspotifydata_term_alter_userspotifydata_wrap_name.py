# Generated by Django 5.1 on 2024-11-30 21:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0011_remove_genre_spotify_data_remove_track_spotify_data_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userspotifydata',
            name='term',
            field=models.CharField(choices=[('short_term', 'Short Term'), ('medium_term', 'Medium Term'), ('long_term', 'Long Term')], default=[], max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='userspotifydata',
            name='wrap_name',
            field=models.CharField(max_length=255),
        ),
    ]
