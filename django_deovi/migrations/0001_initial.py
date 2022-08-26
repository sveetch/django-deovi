# Generated by Django 3.1.14 on 2022-08-24 23:56

import django.core.validators
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MediaFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, default='', help_text='Title label', max_length=150, verbose_name='title')),
                ('path', models.TextField(default='', help_text='The full path where the file is stored.', unique=True, verbose_name='path')),
                ('absolute_dir', models.CharField(default='', help_text='The absolute directory path where the file is stored', max_length=150, verbose_name='absolute directory path')),
                ('directory', models.CharField(blank=True, default='', help_text='The directory name where file is stored.', max_length=200, verbose_name='directory')),
                ('filename', models.CharField(default='', help_text='The file name', max_length=150, verbose_name='filename')),
                ('container', models.CharField(default='', help_text='The media container as determined from its file extension.', max_length=50, verbose_name='media container')),
                ('filesize', models.BigIntegerField(default=0, help_text='The file size', validators=[django.core.validators.MinValueValidator(0)], verbose_name='filesize')),
                ('stored_date', models.DateTimeField(db_index=True, default=None, verbose_name='stored date')),
                ('loaded_date', models.DateTimeField(db_index=True, default=django.utils.timezone.now, verbose_name='loaded date')),
            ],
            options={
                'verbose_name': 'MediaFile',
                'verbose_name_plural': 'MediaFiles',
                'ordering': ['stored_date'],
            },
        ),
    ]
