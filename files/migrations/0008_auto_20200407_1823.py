# Generated by Django 3.0.4 on 2020-04-07 18:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('files', '0007_fileupload_sha512_hash'),
    ]

    operations = [
        migrations.RenameField(
            model_name='fileupload',
            old_name='sha512_hash',
            new_name='sha512_file_hash',
        ),
    ]
