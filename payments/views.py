from django.shortcuts import render, redirect
from tickets.models import Ticket
from django.urls import reverse
from tickets.utils import generate_pdf, generate_qr
from tickets.email import send_ticket_email


def payment_failed(request, ticket_number):
    context = {
        "title_tag": "Payment Failed!",
        "ticket": Ticket.objects.get(ticket_number=ticket_number),
    }
    return render(request, "payment_failed.html", context)


def payment_success(request, ticket_number):
    ticket = Ticket.objects.get(ticket_number=ticket_number)
    ticket_url = request.build_absolute_uri(reverse(
        'view_ticket', args=[ticket.event.slug, ticket.ticket_number, ticket.event.pk]))
    generate_qr(ticket_url, ticket)
    ticket.save()
    generate_pdf(
        ticket_url, ticket.event, ticket, ticket.first_name, ticket.last_name,
        ticket.email, ticket.phone_number, ticket.amount, ticket.ticket_type
    )
    ticket.save()
    send_ticket_email(ticket, ticket.event)
    ticket.save()
    return redirect('view_ticket', ticket.event.slug, ticket.ticket_number, ticket.event.pk)
