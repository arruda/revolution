# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='is_ready',
            field=models.BooleanField(verbose_name='Ready', default=False),
        ),
    ]
