# Generated by Django 4.2.7 on 2023-12-03 19:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0002_event'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='status',
            field=models.BooleanField(default=False),
        ),
    ]
