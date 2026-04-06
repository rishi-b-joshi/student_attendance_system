# from django.contrib import admin
# from .models import Student, Lecture, Attendance

# admin.site.register(Student)
# admin.site.register(Lecture)
# admin.site.register(Attendance)


from django.contrib import admin
from .models import Student, Lecture, Attendance

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "class_name")
    search_fields = ("id", "name", "class_name")


@admin.register(Lecture)
class LectureAdmin(admin.ModelAdmin):
    list_display = ("id", "subject", "section", "date")
    list_filter = ("date", "section")
    search_fields = ("subject", "section")


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("id", "student", "lecture", "timestamp")
    list_filter = ("lecture__date", "lecture__subject", "lecture__section")
    search_fields = ("student__id", "student__name", "lecture__subject")