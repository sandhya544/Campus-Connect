from django.contrib import admin
from .models import skill, certification, internship, project, Student, Event

admin.site.register(skill)
admin.site.register(certification)
admin.site.register(internship)
admin.site.register(project)
admin.site.register(Student)
admin.site.register(Event)
# Register your models here.
