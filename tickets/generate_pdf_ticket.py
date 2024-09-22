from io import BytesIO
from django.core.files import File
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors


def generate_pdf(ticket):
    """
    Generate a PDF for the given ticket with a layout similar to the provided HTML.
    """
    pdf_buffer = BytesIO()
    p = canvas.Canvas(pdf_buffer, pagesize=letter)
    width, height = letter
    p.setFont("Helvetica", 12)

    # Define padding and border parameters
    padding = 40
    border_radius = 20
    border_size = 1
    border_color = colors.grey
    line_color = colors.grey

    # Draw a rounded rectangle background
    p.setStrokeColor(border_color)
    p.setLineWidth(border_size)
    p.roundRect(
        padding, height - 750, width - 2 * padding,
        700, border_radius, fill=False, stroke=True)

    # Event name and venue
    p.setFont("Helvetica-Bold", 16)
    p.setFillColorRGB(0, 0, 0)
    p.drawString(padding + 30, height - 80, ticket.event.name)
    p.setFont("Helvetica", 12)
    p.setFillColor(line_color)
    p.drawString(
        padding + 30, height - 100,
        f"{ticket.event.venue}, {ticket.event.location}")

    # Event host
    p.setFont("Helvetica-Bold", 10)
    p.setFillColorRGB(0, 0, 0)
    p.drawString(padding + 30, height - 120, f"Hosted by {ticket.event.host}")

    # Draw a line
    p.setStrokeColor(line_color)
    p.line(padding + 30, height - 130, width - padding - 30, height - 130)

    # Personal details
    y = height - 160
    p.setFillColorRGB(0, 0, 0)

    p.setFont("Helvetica", 10)
    p.drawString(padding + 30, y, "Name")
    p.setFont("Helvetica-Bold", 12)
    p.drawString(padding + 110, y, ticket.get_fullname)

    y -= 30
    p.setFont("Helvetica", 10)
    p.drawString(padding + 30, y, "Email")
    p.setFont("Helvetica-Bold", 12)
    p.drawString(padding + 110, y, ticket.get_email)

    y -= 30
    p.setFont("Helvetica", 10)
    p.drawString(padding + 30, y, "Phone Number")
    p.setFont("Helvetica-Bold", 12)
    p.drawString(padding + 110, y, ticket.get_phone_number)

    # Draw another line
    p.line(padding + 30, y - 20, width - padding - 30, y - 20)

    y -= 40
    p.setFont("Helvetica", 10)
    p.drawString(padding + 30, y, "Ticket type:")
    p.setFont("Helvetica-Bold", 12)
    p.drawString(padding + 110, y, ticket.ticket_type)

    p.setFont("Helvetica", 10)
    p.drawString(padding + 300, y, "Ticket(s):")
    p.setFont("Helvetica-Bold", 12)
    p.drawString(padding + 370, y, ticket.num_tickets)

    y -= 40
    p.setFont("Helvetica", 10)
    p.drawString(padding + 30, y, "Ticket Number:")
    p.setFont("Helvetica-Bold", 12)
    p.drawString(padding + 110, y, f"No {ticket.get_reference_number}")

    # Draw another line
    p.line(padding + 30, y - 20, width - padding - 30, y - 20)

    y -= 40
    p.setFont("Helvetica", 10)
    p.drawString(padding + 30, y, "Paid:")
    p.setFont("Helvetica-Bold", 12)
    p.drawString(padding + 110, y, f"KES {ticket.amount}")

    p.setFont("Helvetica", 10)
    p.drawString(padding + 300, y, "Paid Via:")
    p.setFont("Helvetica-Bold", 12)
    p.drawString(padding + 370, y, ticket.get_payment_method)

    y -= 40
    p.setFont("Helvetica", 10)
    p.drawString(padding + 30, y, "Code:")
    p.setFont("Helvetica-Bold", 12)
    p.drawString(padding + 110, y, ticket.get_transaction_code)

    # Draw another line
    p.line(padding + 30, y - 20, width - padding - 30, y - 20)

    # Event details
    y -= 50
    p.setFont("Helvetica", 10)
    p.drawString(padding + 30, y, "Date")
    p.setFont("Helvetica-Bold", 12)
    p.drawString(padding + 110, y, ticket.event.date.strftime("%Y-%m-%d"))

    p.setFont("Helvetica", 10)
    p.drawString(padding + 300, y, "Time")
    p.setFont("Helvetica-Bold", 12)
    p.drawString(
        padding + 370, y,
        f"{ticket.event.start_time} - {ticket.event.end_time}"
    )

    y -= 40
    p.setFont("Helvetica", 10)
    p.setFillColor(line_color)
    p.drawCentredString(width // 2, y, "Show the QR Code at the entrance")

    # QR Code
    if ticket.qr and ticket.qr.path:
        p.drawImage(
            ticket.qr.path, width // 2 - 108,
            y - 230, width=220, height=220)

    y -= 260
    p.setFont("Helvetica", 8)
    p.setFillColor(line_color)
    p.drawCentredString(width // 2, y, ticket.event.event_disclaimer)

    # Finalize the PDF
    p.showPage()
    p.save()

    # Save the PDF to the `pdf_ticket` field
    pdf_buffer.seek(0)
    ticket.pdf_ticket.save(
        f'ticket_{ticket.ticket_number}.pdf', File(pdf_buffer), save=False)
