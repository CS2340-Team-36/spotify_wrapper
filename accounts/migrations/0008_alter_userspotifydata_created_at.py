# Generated by Django 5.1 on 2024-11-30 16:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_remove_userspotifydata_top_tracks_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userspotifydata',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]