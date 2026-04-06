from django.db import models

class Student(models.Model):
    id = models.CharField(primary_key=True, max_length=20)
    name = models.CharField(max_length=100)
    class_name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.id} - {self.name}"


class Lecture(models.Model):
    subject = models.CharField(max_length=100)
    section = models.CharField(max_length=50)
    date = models.DateField()

    def __str__(self):
        return f"{self.subject} ({self.section}) on {self.date}"


class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'lecture')
