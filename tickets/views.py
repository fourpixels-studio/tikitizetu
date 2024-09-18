import uuid
import logging
from events.models import Event
from tickets.models import Ticket
from django.contrib import messages
from django.http import HttpResponse
from payments.pesapal_payments import PesaPal
from payments.safaricom_payments import Safaricom
from django.shortcuts import render, redirect, get_object_or_404

logger = logging.getLogger('django')


def view_ticket(request, slug, ticket_number, pk):
    ticket = get_object_or_404(Ticket, ticket_number=ticket_number)
    context = {
        "title_tag": f"Your {ticket.event.name} Ticket",
        "ticket": ticket,
        "event": ticket.event,
    }
    return render(request, "view_ticket.html", context)


def purchase_ticket(request):
    if request.method == 'POST':
        event_id = request.POST.get('event')
        payment_method = request.POST.get('payment_method')
        event = Event.objects.get(id=event_id)

        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        ticket_type = request.POST.get('ticket_type')
        amount = request.POST.get('amount')
        num_tickets = request.POST.get('num_tickets')
        ticket_number = generate_ticket_number()
        transaction_id = "TXN" + str(uuid.uuid4())[:47]

        ticket = Ticket(
            event=event,
            ticket_number=ticket_number,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
            ticket_type=ticket_type,
            num_tickets=num_tickets,
            amount=amount,
            paid=False,
            status="Pending",
            transaction_id=transaction_id,
            payment_mode=payment_method,
        )

        description = f'Payment for "{event.name[:23]}" ticket'
        event_slug = event.slug
        event_pk = event.pk
        display_name = f"{ticket_type} Ticket for {event.name}"

        if payment_method == 'safaricom':
            try:
                safaricom = Safaricom()
                phone_number = format_phone_number(phone_number)
                payment_response = safaricom.initiate_stk_push(
                    amount, phone_number, display_name
                )
                if payment_response:
                    checkout_request_id = payment_response["CheckoutRequestID"]
                    ticket.checkout_request_id = checkout_request_id
                    ticket.status = "Awaiting payment confirmation"
                    ticket.save()
                    return redirect('safaricom_processing_payment', ticket.ticket_number)
                else:
                    logger.error(
                        "No response from safaricom.initiate_stk_push")
                    ticket.status = "Payment initiation failed inside safaricom payment"
                    ticket.save()
                    return redirect('payment_failed', ticket.ticket_number)

            except Exception as e:
                logger.error(f"Payment initiation failed: {str(e)}")
                ticket.status = f"Payment initiation failed: {str(e)}"
                ticket.save()
                return redirect('payment_failed', ticket.ticket_number)

        elif payment_method == 'pesapal':
            try:
                pesapal = PesaPal()
                payment_response = pesapal.submit_order(
                    transaction_id, amount, description, phone_number, email,
                    first_name, last_name, ticket_number, event_slug, event_pk
                )

                if 'redirect_url' in payment_response:
                    ticket.save()
                    return redirect(payment_response['redirect_url'])
                else:
                    ticket.status = "Missing redirect URL"
                    ticket.save()
                    return redirect('payment_failed', ticket.ticket_number)
            except KeyError as e:
                messages.error(request, f"Payment initiation failed: {str(e)}")
                ticket.status = f"Payment initiation failed: {str(e)}"
                ticket.save()
                return redirect('payment_failed', ticket.ticket_number)
        else:
            ticket.status = "Payment initiation failed outside safaricom payment"
            messages.error(
                request, "Payment initiation failed outside safaricom payment")
            return redirect('payment_failed', ticket.ticket_number)
    return HttpResponse("Invalid request method", status=400)


def generate_ticket_number():
    return str(uuid.uuid4())


def format_phone_number(phone_number):
    # Remove any spaces or non-numeric characters like '+'
    phone_number = phone_number.strip().replace(" ", "").replace("+", "")

    # If the number starts with '07', replace it with '2547'
    if phone_number.startswith("07"):
        phone_number = "254" + phone_number[1:]

    # If the number starts with '01', replace it with '2541'
    elif phone_number.startswith("01"):
        phone_number = "254" + phone_number[1:]

    # If the number starts with '7', assume it's missing the '254' and add it
    elif phone_number.startswith("7"):
        phone_number = "254" + phone_number

    # If the number starts with '1', assume it's missing the '254' and add it
    elif phone_number.startswith("1"):
        phone_number = "254" + phone_number

    # If the number starts with '254', it's already in the correct format
    elif phone_number.startswith("254"):
        pass
    else:
        # Handle other cases (e.g., invalid numbers)
        raise ValueError("Invalid phone number format")

    return phone_number
