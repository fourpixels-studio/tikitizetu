import qrcode
from io import BytesIO
from django.core.files import File
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors


def generate_qr(ticket_url, ticket):
    """
    Generate a QR code for the given ticket URL and save it to the ticket's `qr` field.
    """
    qr = qrcode.make(ticket_url)
    qr_io = BytesIO()
    qr.save(qr_io, format='PNG')
    qr_io.seek(0)
    ticket.qr.save(f'qr_{ticket.ticket_number}.png', File(qr_io), save=False)


def generate_pdf(ticket_url, event, ticket, first_name, last_name, email, phone_number, amount, ticket_type):
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
    border_color = colors.black
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
    p.drawString(padding + 30, height - 80, event.name)
    p.setFont("Helvetica", 12)
    p.setFillColor(line_color)
    p.drawString(
        padding + 30, height - 100,
        f"{event.venue}, {event.location}")

    # Draw a line
    p.setStrokeColor(line_color)
    p.line(padding + 30, height - 110, width - padding - 30, height - 110)

    # Personal details
    y = height - 140
    p.setFillColorRGB(0, 0, 0)

    p.setFont("Helvetica", 10)
    p.drawString(padding + 30, y, "Name")
    p.setFont("Helvetica-Bold", 12)
    p.drawString(padding + 110, y, f"{first_name} {last_name}")

    y -= 30
    p.setFont("Helvetica", 10)
    p.drawString(padding + 30, y, "Email")
    p.setFont("Helvetica-Bold", 12)
    p.drawString(padding + 110, y, email)

    y -= 30
    p.setFont("Helvetica", 10)
    p.drawString(padding + 30, y, "Phone Number")
    p.setFont("Helvetica-Bold", 12)
    p.drawString(padding + 110, y, ticket.phone_number)

    # Draw another line
    p.line(padding + 30, y - 20, width - padding - 30, y - 20)

    y -= 40
    p.setFont("Helvetica", 10)
    p.drawString(padding + 30, y, "Paid")
    p.setFont("Helvetica-Bold", 12)
    p.drawString(padding + 110, y, f"Ksh {amount}")

    y -= 30
    p.setFont("Helvetica", 10)
    p.drawString(padding + 30, y, "Ticket type")
    p.setFont("Helvetica-Bold", 12)
    p.drawString(padding + 110, y, ticket_type)

    y -= 30
    p.setFont("Helvetica", 10)
    p.drawString(padding + 30, y, "Ticket Number")
    p.setFont("Helvetica-Bold", 12)
    p.drawString(padding + 110, y, ticket.ticket_number[:8])

    # Draw another line
    p.line(padding + 30, y - 20, width - padding - 30, y - 20)

    # Event details
    y -= 50
    p.setFont("Helvetica", 10)
    p.drawString(padding + 30, y, "Date")
    p.setFont("Helvetica-Bold", 12)
    p.drawString(padding + 110, y, event.date.strftime("%Y-%m-%d"))

    p.setFont("Helvetica", 10)
    p.drawString(padding + 300, y, "Time")
    p.setFont("Helvetica-Bold", 12)
    p.drawString(padding + 370, y, f"{event.start_time} - {event.end_time}")

    y -= 80
    p.setFont("Helvetica", 10)
    p.setFillColor(line_color)
    p.drawCentredString(width // 2, y, "Show the QR Code at the entrance")

    # QR Code
    if ticket.qr and ticket.qr.path:
        p.drawImage(
            ticket.qr.path, width // 2 - 125,
            y - 270, width=250, height=250)

    # Finalize the PDF
    p.showPage()
    p.save()

    # Save the PDF to the `pdf_ticket` field
    pdf_buffer.seek(0)
    ticket.pdf_ticket.save(
        f'ticket_{ticket.ticket_number}.pdf', File(pdf_buffer), save=False)
