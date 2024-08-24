from tickets.models import Ticket
from .forms import TicketForm
from events.models import Event

from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
import uuid
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.http import HttpResponse
from .utils import generate_pdf_ticket
# from .email import send_email_with_inline_logo


def view_ticket(request, pk, ticket_number):
    ticket = get_object_or_404(Ticket, ticket_number=ticket_number)
    event = ticket.get_event
    context = {
        "title_tag": f"Your {event.name} Ticket",
        "ticket": ticket,
        "event": event,
    }
    return render(request, "view_ticket.html", context)


def new_ticket(request):
    # Initialize the form with or without POST data
    new_ticket_form = TicketForm(request.POST or None)

    if request.method == 'POST':
        if new_ticket_form.is_valid():

            # Assigning the event signup instance with a ticket number
            new_ticket = new_ticket_form.save(commit=False)
            # Function to generate ticket number
            new_ticket.ticket_number = generate_ticket_number()
            new_ticket.save()

            # Extract information for logging and email
            first_name = new_ticket.first_name

            # Display success message
            messages.success(
                request, f"{first_name} was successfully added!")
            return redirect('event_signup_portal')

    context = {
        'new_ticket_form': new_ticket_form,
    }

    # Render the template
    return render(request, 'event_signup.html', context)


def generate_ticket_number():
    return str(uuid.uuid4())[:6]


def qr_scan_view(request, ticket_number):
    ticket = get_object_or_404(Ticket, ticket_number=ticket_number)
    ticket.scan_count += 1
    ticket.save()
    return HttpResponse(f"Ticket {ticket.ticket_number} has been scanned {ticket.scan_count} times.")


def download_ticket(request, first_name, last_name, ticket_number, event_name, event_date):
    pdf_content = generate_pdf_ticket(
        first_name, last_name, ticket_number, event_name, event_date)
    response = HttpResponse(pdf_content, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ticket_{ticket_number}.pdf"'
    return response
