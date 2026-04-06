from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Student, Lecture, Attendance


# Signed token (cannot be forged) + timestamp based expiry
signer = TimestampSigner(salt="lecture-attendance-qr")

import base64
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from .models import Lecture

import qrcode
import qrcode.image.svg


signer = TimestampSigner(salt="lecture-attendance-qr")


@api_view(["POST"])
def create_student(request):
    """
    POST /attendance/students/create/
    Body:
    {
      "id": "S001",
      "name": "Alice Johnson",
      "class_name": "FY-CS"
    }
    """
    student_id = request.data.get("id")
    name = request.data.get("name")
    class_name = request.data.get("class_name")

    if not student_id or not name or not class_name:
        return Response(
            {"status": "error", "message": "id, name, class_name are required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Create if doesn't exist; otherwise return info
    student, created = Student.objects.get_or_create(
        id=student_id,
        defaults={"name": name, "class_name": class_name}
    )

    if created:
        return Response(
            {"status": "success", "message": "Student created", "student_id": student.id},
            status=status.HTTP_201_CREATED
        )

    return Response(
        {"status": "success", "message": "Student already exists", "student_id": student.id},
        status=status.HTTP_200_OK
    )


@api_view(["POST"])
def create_lecture(request):
    """
    POST /attendance/lectures/create/
    Body:
    {
      "subject": "Maths",
      "section": "A",
      "date": "2026-04-04"
    }
    """
    subject = request.data.get("subject")
    section = request.data.get("section")
    date = request.data.get("date")  # yyyy-mm-dd

    if not subject or not section or not date:
        return Response(
            {"status": "error", "message": "subject, section, date are required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    lecture = Lecture.objects.create(subject=subject, section=section, date=date)

    return Response(
        {
            "status": "success",
            "message": "Lecture created",
            "lecture_id": lecture.id
        },
        status=status.HTTP_201_CREATED
    )


# @api_view(["GET"])
# def generate_lecture_token(request, lecture_id):
#     """
#     GET /attendance/lectures/<lecture_id>/token/

#     Returns ONLY a signed token.
#     You generate QR image externally using the returned token.
#     """
#     try:
#         lecture = Lecture.objects.get(id=lecture_id)
#     except Lecture.DoesNotExist:
#         return Response(
#             {"status": "error", "message": "Lecture not found"},
#             status=status.HTTP_404_NOT_FOUND
#         )

#     token = signer.sign(str(lecture.id))

#     return Response(
#         {
#             "status": "success",
#             "lecture_id": lecture.id,
#             "lecture": str(lecture),
#             "qr_token": token,
#             "expires_in_seconds": 300
#         },
#         status=status.HTTP_200_OK
#     )


@api_view(["POST"])
def verify_qr(request):
    """
    POST /attendance/verify/
    Body:
    {
      "student_id": "S001",
      "qr_token": "<SIGNED_TOKEN>"
    }

    QR token expires in 300 seconds (5 minutes).
    """
    student_id = request.data.get("student_id")
    qr_token = request.data.get("qr_token")

    if not student_id or not qr_token:
        return Response(
            {"status": "error", "message": "student_id and qr_token are required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Validate student
    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        return Response(
            {"status": "error", "message": "Student not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    # Validate token (signature + expiry)
    try:
        lecture_id = signer.unsign(qr_token, max_age=300)
    except SignatureExpired:
        return Response(
            {"status": "error", "message": "QR expired"},
            status=status.HTTP_400_BAD_REQUEST
        )
    except BadSignature:
        return Response(
            {"status": "error", "message": "Invalid QR token"},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Validate lecture
    try:
        lecture = Lecture.objects.get(id=lecture_id)
    except Lecture.DoesNotExist:
        return Response(
            {"status": "error", "message": "Lecture not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    # Mark attendance once
    attendance, created = Attendance.objects.get_or_create(student=student, lecture=lecture)

    if created:
        return Response(
            {
                "status": "success",
                "message": f"Attendance marked for {student.name} in {lecture.subject}",
                "student": {"id": student.id, "name": student.name},
                "lecture": {"id": lecture.id, "subject": lecture.subject, "section": lecture.section, "date": str(lecture.date)}
            },
            status=status.HTTP_200_OK
        )

    return Response(
        {"status": "error", "message": "Attendance already recorded"},
        status=status.HTTP_409_CONFLICT
    )

@api_view(["GET"])
def generate_lecture_token(request, lecture_id):
    """
    GET /attendance/lectures/<lecture_id>/token/
    Returns signed token only.
    """
    try:
        lecture = Lecture.objects.get(id=lecture_id)
    except Lecture.DoesNotExist:
        return Response({"status": "error", "message": "Lecture not found"}, status=404)

    token = signer.sign(str(lecture.id))
    return Response({
        "status": "success",
        "lecture_id": lecture.id,
        "qr_token": token,
        "expires_in_seconds": 300
    })


@api_view(["GET"])
def generate_lecture_qr_svg(request, lecture_id):
    """
    GET /attendance/lectures/<lecture_id>/qr-svg/
    Generates QR code as SVG (NO Pillow) for lecture token.
    Returns raw SVG file as response.
    """
    try:
        lecture = Lecture.objects.get(id=lecture_id)
    except Lecture.DoesNotExist:
        return Response({"status": "error", "message": "Lecture not found"}, status=404)

    token = signer.sign(str(lecture.id))

    factory = qrcode.image.svg.SvgImage
    img = qrcode.make(token, image_factory=factory)

    svg_bytes = img.to_string()  # bytes

    return HttpResponse(svg_bytes, content_type="image/svg+xml")


@api_view(["GET"])
def generate_lecture_qr_svg_base64(request, lecture_id):
    """
    GET /attendance/lectures/<lecture_id>/qr-svg-base64/
    Generates QR code as SVG (NO Pillow) and returns base64 string.
    Useful for frontend embedding.
    """
    try:
        lecture = Lecture.objects.get(id=lecture_id)
    except Lecture.DoesNotExist:
        return Response({"status": "error", "message": "Lecture not found"}, status=404)

    token = signer.sign(str(lecture.id))

    factory = qrcode.image.svg.SvgImage
    img = qrcode.make(token, image_factory=factory)

    svg_bytes = img.to_string()
    svg_b64 = base64.b64encode(svg_bytes).decode("utf-8")

    return Response({
        "status": "success",
        "lecture_id": lecture.id,
        "qr_token": token,
        "qr_svg_base64": svg_b64,
        "expires_in_seconds": 300
    })


@api_view(["GET"])
def lecture_report(request, lecture_id):
    """
    GET /attendance/lectures/<lecture_id>/report/

    Returns attendance list for a lecture.
    """
    try:
        lecture = Lecture.objects.get(id=lecture_id)
    except Lecture.DoesNotExist:
        return Response(
            {"status": "error", "message": "Lecture not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    records = Attendance.objects.filter(lecture=lecture).select_related("student").order_by("timestamp")

    data = [
        {
            "student_id": r.student.id,
            "student_name": r.student.name,
            "class_name": r.student.class_name,
            "timestamp": r.timestamp.isoformat()
        }
        for r in records
    ]

    return Response(
        {
            "status": "success",
            "lecture": {
                "id": lecture.id,
                "subject": lecture.subject,
                "section": lecture.section,
                "date": str(lecture.date)
            },
            "count": len(data),
            "attendance": data
        },
        status=status.HTTP_200_OK
    )