# Generated by Django 4.2.7 on 2023-12-03 19:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('company', models.CharField(max_length=100)),
                ('description', models.TextField(max_length=1000)),
                ('date', models.DateTimeField()),
                ('venue', models.CharField(max_length=100)),
                ('eventId', models.CharField(max_length=20)),
                ('email', models.EmailField(max_length=254)),
                ('eventCode', models.CharField(max_length=20)),
                ('profiles', models.ManyToManyField(to='student.student')),
            ],
        ),
    ]
