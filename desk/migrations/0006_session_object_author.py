# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-29 17:33
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('desk', '0005_remove_session_object_author'),
    ]

    operations = [
        migrations.AddField(
            model_name='session_object',
            name='author',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
