from django.db import models
from django.utils import timezone
import datetime


class skill(models.Model):
    skillName = models.CharField(max_length=100)
    proficiency = models.IntegerField()

    def __str__(self):
        return self.skillName


class certification(models.Model):
    rollNumber = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    certificationName = models.CharField(max_length=200)
    year = models.IntegerField(blank=True)
    url = models.TextField(max_length=1000)

    def __str__(self):
        return self.certificationName


class internship(models.Model):
    rollNumber = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    internshipName = models.CharField(max_length=200)
    year = models.IntegerField(blank=True)
    duration = models.IntegerField()
    provider = models.CharField(max_length=200)
    status = models.BooleanField(blank=False)
    url = models.TextField(max_length=1000)

    def __str__(self):
        return self.internshipName


class project(models.Model):
    rollNumber = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    projectName = models.CharField(max_length=200)
    description = models.TextField(max_length=250)
    year = models.IntegerField(blank=True)
    githubUrl = models.TextField(max_length=1000)

    def __str__(self):
        return self.projectName


class Student(models.Model):#19am1a0307
    rollNumber = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
    tagline = models.CharField(max_length=100, blank=True)
    about = models.CharField(max_length=500, blank=True)
    gender = models.BooleanField(default=False, blank=True)
    GradCollege = models.CharField(max_length=100, blank=True)
    GradBranch = models.CharField(max_length=100, blank=True)
    GradPercentage = models.IntegerField(default=0)
    GradYear = models.IntegerField(default=2024)
    PucCollege = models.CharField(max_length=100, blank=True)
    PucBranch = models.CharField(max_length=100, blank=True)
    PucPercentage = models.IntegerField(default=0)
    PucYear = models.IntegerField(default=2020)
    SscCollege = models.CharField(max_length=100, blank=True)
    SscBranch = models.CharField(max_length=100, blank=True)
    SscPercentage = models.IntegerField(default=0)
    SscYear = models.IntegerField(default=2018)
    skills = models.ManyToManyField(skill, blank=True)
    certifications = models.ManyToManyField(certification, blank=True)
    internships = models.ManyToManyField(internship, blank=True)
    projects = models.ManyToManyField(project, blank=True)
    githubProfile = models.TextField(max_length=1000, blank=True)
    linkedinProfile = models.TextField(max_length=1000, blank=True)
    address = models.CharField(max_length=200, blank=True)
    placed = models.BooleanField(default=False)

    def __str__(self):
        return self.rollNumber.username


class Event(models.Model):
    title = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    description = models.TextField(max_length=1000)
    date = models.DateTimeField(default=timezone.make_aware(
        datetime.datetime.combine(timezone.now().date(), datetime.time(10, 0)),
        timezone=timezone.get_current_timezone()
    ))
    expiryDate = models.DateTimeField(default=timezone.make_aware(
        datetime.datetime.combine(timezone.now().date(), datetime.time(23, 0)),
        timezone=timezone.get_current_timezone()
    ))
    venue = models.CharField(max_length=100)
    eventId = models.CharField(max_length=20)
    email = models.EmailField()
    eventCode = models.CharField(max_length=20)
    profiles = models.ManyToManyField(Student)
    selected = models.ManyToManyField(Student, related_name='selected', blank=True)

    def __str__(self):
        return self.company