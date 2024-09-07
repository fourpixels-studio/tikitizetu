from tickets.models import Ticket
from events.models import Event
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
import uuid
from django.http import HttpResponse
from .utils import generate_qr, generate_pdf
from payments.views import process_bank_payment
from django.contrib import messages
from .email import send_ticket_email


def view_ticket(request, slug, ticket_number, pk):
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
        ticket_type = request.POST.get('ticket_type')
        amount = request.POST.get('amount')
        num_tickets = request.POST.get('num_tickets')

        # Payment processing (using a payment gateway)
        card_number = request.POST.get('card_number')
        cvc_number = request.POST.get('cvc_number')
        expiry_date = request.POST.get('expiry_date')

        payment_success = process_bank_payment(
            card_number, cvc_number,
            expiry_date, amount
        )
        if payment_success:
            # Create the ticket instance
            ticket = Ticket(
                event=event,
                ticket_number=generate_ticket_number(),
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone_number=phone_number,
                ticket_type=ticket_type,
                num_tickets=num_tickets,
                amount=amount,
            )

            # Save the ticket initially to generate the ID and ticket_number
            ticket.save()

            # Generate the ticket URL
            ticket_url = request.build_absolute_uri(
                reverse(
                    'view_ticket', args=[
                        event.slug, ticket.ticket_number, event.pk
                    ])
            )

            # Generate QR Code containing the ticket URL
            generate_qr(ticket_url, ticket)
            ticket.save()

            generate_pdf(
                ticket_url, event, ticket, first_name, last_name,
                email, phone_number, amount, ticket_type
            )

            # Save the updated ticket with QR and PDF
            ticket.save()
            send_ticket_email(ticket, event)

            return redirect('view_ticket', event.slug, ticket.ticket_number, event.pk)
        else:
            messages.error(request, "Payment failed. Please try again.")
            return redirect('cart', slug=event.slug, pk=event.pk)


def generate_ticket_number():
    return str(uuid.uuid4())


def qr_scan_view(request, ticket_number):
    ticket = get_object_or_404(Ticket, ticket_number=ticket_number)
    ticket.scan_count += 1
    ticket.save()
    return HttpResponse(f"Ticket {ticket.ticket_number} has been scanned {ticket.scan_count} times.")
