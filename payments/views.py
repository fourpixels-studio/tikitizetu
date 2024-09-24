from django.urls import reverse
from tickets.models import Ticket
from tickets.email import send_ticket_email
from tickets.generate_qr import generate_qr
from django.shortcuts import render, redirect
from tickets.generate_pdf_ticket import generate_pdf


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
    generate_pdf(ticket)
    ticket.save()
    send_ticket_email(ticket)
    ticket.status = 'Complete'
    ticket.save()
    return redirect('view_ticket', ticket.event.slug, ticket.ticket_number, ticket.event.pk)
