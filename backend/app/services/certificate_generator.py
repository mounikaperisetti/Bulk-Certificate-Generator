from datetime import date
from pathlib import Path

from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas


def generate_certificate(
    recipient_name: str,
    organization: str | None,
    course_name: str | None,
    start_date: date | None,
    end_date: date | None,
    completion_date: date | None,
    event_name: str | None,
    event_date: date | None,
    output_path: str,
):
    """Generate one certificate PDF using the available certificate data."""
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    page_width, page_height = landscape(A4)

    pdf = canvas.Canvas(str(output_file), pagesize=landscape(A4))

    pdf.setLineWidth(3)
    pdf.rect(30, 30, page_width - 60, page_height - 60)

    pdf.setLineWidth(1)
    pdf.rect(40, 40, page_width - 80, page_height - 80)

    pdf.setFont("Helvetica-Bold", 30)
    pdf.drawCentredString(
        page_width / 2,
        page_height - 110,
        "CERTIFICATE",
    )

    pdf.setFont("Helvetica", 15)
    pdf.drawCentredString(
        page_width / 2,
        page_height - 150,
        "This certificate is proudly presented to",
    )

    pdf.setFont("Helvetica-Bold", 26)
    pdf.drawCentredString(
        page_width / 2,
        page_height - 205,
        recipient_name,
    )

    current_y = page_height - 255

    if organization:
        pdf.setFont("Helvetica", 13)
        pdf.drawCentredString(
            page_width / 2,
            current_y,
            organization,
        )
        current_y -= 30

    if course_name:
        pdf.setFont("Helvetica", 15)
        pdf.drawCentredString(
            page_width / 2,
            current_y,
            f"Course: {course_name}",
        )
        current_y -= 30

    if start_date and end_date:
        pdf.setFont("Helvetica", 12)
        pdf.drawCentredString(
            page_width / 2,
            current_y,
            f"Duration: {start_date} to {end_date}",
        )
        current_y -= 25
    elif start_date:
        pdf.setFont("Helvetica", 12)
        pdf.drawCentredString(
            page_width / 2,
            current_y,
            f"Start Date: {start_date}",
        )
        current_y -= 25
    elif end_date:
        pdf.setFont("Helvetica", 12)
        pdf.drawCentredString(
            page_width / 2,
            current_y,
            f"End Date: {end_date}",
        )
        current_y -= 25

    if completion_date:
        pdf.setFont("Helvetica", 12)
        pdf.drawCentredString(
            page_width / 2,
            current_y,
            f"Completion Date: {completion_date}",
        )
        current_y -= 25

    if event_name:
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawCentredString(
            page_width / 2,
            current_y,
            f"Event: {event_name}",
        )
        current_y -= 25

    if event_date:
        pdf.setFont("Helvetica", 12)
        pdf.drawCentredString(
            page_width / 2,
            current_y,
            f"Event Date: {event_date}",
        )

    pdf.line(120, 85, 250, 85)
    pdf.setFont("Helvetica", 10)
    pdf.drawCentredString(185, 70, "Authorized Signature")

    pdf.save()