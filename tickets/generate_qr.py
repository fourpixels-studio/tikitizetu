import qrcode  # type: ignore
from io import BytesIO
from django.core.files import File


def generate_qr(ticket_url, ticket):
    """
    Generate a QR code for the given ticket URL and save it to the ticket's `qr` field.
    """
    qr = qrcode.make(ticket_url)
    qr_io = BytesIO()
    qr.save(qr_io, format='PNG')
    qr_io.seek(0)
    ticket.qr.save(f'qr_{ticket.ticket_number}.png', File(qr_io), save=False)
