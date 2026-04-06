from django.urls import path
from .views import (
    create_student,
    create_lecture,
    generate_lecture_token,
    verify_qr,
    lecture_report,
    generate_lecture_qr_svg,
    generate_lecture_qr_svg_base64
    )

urlpatterns = [
    path("students/create/", create_student, name="create_student"),
    path("lectures/create/", create_lecture, name="create_lecture"),
    path("lectures/<int:lecture_id>/token/", generate_lecture_token, name="generate_lecture_token"),
    path("verify/", verify_qr, name="verify_qr"),
    path("lectures/<int:lecture_id>/report/", lecture_report, name="lecture_report"),

    
    path("lectures/<int:lecture_id>/qr-svg/", generate_lecture_qr_svg, name="generate_lecture_qr_svg"),
    path("lectures/<int:lecture_id>/qr-svg-base64/", generate_lecture_qr_svg_base64, name="generate_lecture_qr_svg_base64"),


]