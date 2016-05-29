# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-29 17:23
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='session',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=300)),
                ('pub_date', models.DateTimeField(verbose_name=b'date published')),
                ('end_date', models.DateTimeField(blank=True, null=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='session_message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=300)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='desk.session')),
            ],
        ),
        migrations.CreateModel(
            name='session_object',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_added', models.DateTimeField(verbose_name=b'date added')),
                ('data_type', models.CharField(max_length=200)),
                ('_data', models.TextField(blank=True, db_column=b'data')),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='desk.session')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='session_object_movement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('movement_type', models.CharField(max_length=30)),
                ('movement_time', models.DateTimeField(verbose_name=b'movement_time')),
                ('_data', models.TextField(blank=True, db_column=b'data')),
                ('session_object', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='desk.session_object')),
            ],
        ),
    ]
