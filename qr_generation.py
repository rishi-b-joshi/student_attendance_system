import qrcode

def generate_qr_code(text: str, filename: str) -> None:
    """
    Generate a QR code from the given text and save it as an image file.

    Parameters:
    text (str): The text or data to encode into the QR code.
    filename (str): The name of the file to save the QR code image.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(filename)
    print(f"QR code generated for: {text} → {filename}")


# Example: Generate QR codes for multiple students
students = [
    {"id": "S001", "name": "Alice Johnson"},
    {"id": "S002", "name": "Bob Smith"},
    {"id": "S003", "name": "Charlie Davis"},
]

for student in students:
    # Encode student details into QR text
    qr_text = f"ID: {student['id']}, Name: {student['name']}"
    filename = f"{student['id']}_qr.png"
    generate_qr_code(qr_text, filename)
