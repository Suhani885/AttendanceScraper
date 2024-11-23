from django.db import models

class Subject(models.Model):
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    total_classes = models.IntegerField()
    total_present = models.IntegerField()
    attendance_percentage = models.FloatField()

class AttendanceDetail(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    date = models.DateField()
    slot = models.CharField(max_length=50)
    status = models.CharField(max_length=20)

    