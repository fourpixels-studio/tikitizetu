from django.shortcuts import render
from tickets.models import Ticket


def pesapal_payment_failed(request, ticket_number):
    context = {
        "title_tag": "Payment Failed!",
        "ticket": Ticket.objects.get(ticket_number=ticket_number),
    }
    return render(request, "pesapal/pesapal_payment_failed.html", context)
