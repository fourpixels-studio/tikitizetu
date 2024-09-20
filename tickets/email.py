from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings


def send_ticket_email(ticket):
    context = {
        "ticket": ticket,
        "ticket_url": f"{settings.SITE_DOMAIN}/ticket/{ticket.event.slug}/{ticket.ticket_number}/{ticket.event.pk}/"
    }
    # Render the HTML content
    html_content = render_to_string('email/ticket_email.html', context)
    # Strips HTML tags for the plain text alternative
    text_content = strip_tags(html_content)

    # Create the email
    email = EmailMultiAlternatives(
        subject=f"Your Ticket for {ticket.event.name}",
        body=text_content,
        from_email=settings.EMAIL_HOST_USER,
        to=[ticket.get_email],
    )

    # Attach the HTML content
    email.attach_alternative(html_content, "text/html")

    # Send the email
    email.send()
