# Generated by Django 5.0 on 2023-12-11 07:45

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0011_event_expirydate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2023, 12, 11, 10, 0, tzinfo=datetime.timezone.utc)),
        ),
    ]
