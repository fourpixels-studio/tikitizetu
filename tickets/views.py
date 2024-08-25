from tickets.models import Ticket
from events.models import Event
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
import uuid
from django.http import HttpResponse
from .utils import generate_qr, generate_pdf


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
    if request.method == 'POST':
        event_id = request.POST.get('event')
        event = Event.objects.get(id=event_id)

        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        amount = request.POST.get('amount')
        num_tickets = request.POST.get('num_tickets')
        ticket_type = str("Regular")

        # Create the ticket instance
        ticket = Ticket(
            event=event,
            ticket_number=generate_ticket_number(),
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            email=email,
            amount=amount,
            num_tickets=num_tickets,
        )

        # Save the ticket initially to generate the ID and ticket_number
        ticket.save()

        # Generate the ticket URL
        ticket_url = request.build_absolute_uri(
            reverse('view_ticket', args=[ticket.pk, ticket.ticket_number])
        )

        # Generate QR Code containing the ticket URL
        generate_qr(ticket_url, ticket)
        ticket.save()
        generate_pdf(
            ticket_url, event, ticket, first_name, last_name,
            email, phone_number, amount, num_tickets, ticket_type
        )

        # Save the updated ticket with QR and PDF
        ticket.save()

        return redirect('view_ticket', event.pk, ticket.ticket_number)

    return render(request, 'new_ticket.html')


def generate_ticket_number():
    return str(uuid.uuid4())


def qr_scan_view(request, ticket_number):
    ticket = get_object_or_404(Ticket, ticket_number=ticket_number)
    ticket.scan_count += 1
    ticket.save()
    return HttpResponse(f"Ticket {ticket.ticket_number} has been scanned {ticket.scan_count} times.")
