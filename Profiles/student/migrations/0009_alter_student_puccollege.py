# Generated by Django 4.2.7 on 2023-12-03 19:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0008_alter_student_puccollege'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='PucCollege',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
