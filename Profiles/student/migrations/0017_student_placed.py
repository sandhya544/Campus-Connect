# Generated by Django 5.0 on 2023-12-28 13:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0016_alter_event_date_alter_event_expirydate'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='placed',
            field=models.BooleanField(default=False),
        ),
    ]
