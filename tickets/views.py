import logging
from events.models import Event
from tickets.models import Ticket
from django.contrib import messages
from django.http import HttpResponse
from payments.pesapal_payments import PesaPal
from payments.safaricom_payments import Safaricom
from .utils import generate_ticket_number, format_phone_number
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

        ticket = Ticket(
            email=email,
            event=event,
            paid=False,
            amount=amount,
            status="pending",
            last_name=last_name,
            first_name=first_name,
            ticket_type=ticket_type,
            num_tickets=num_tickets,
            phone_number=phone_number,
            ticket_number=ticket_number,
            payment_mode=payment_method,
        )

        description = f'Payment for "{event.name[:23]}" ticket'
        transaction_description = f"{ticket_type} Ticket for {event.name}"

        if payment_method == 'safaricom':
            try:
                safaricom = Safaricom()
                phone_number = format_phone_number(phone_number)
                
                payment_response = safaricom.initiate_stk_push(
                    amount, phone_number, transaction_description
                )
                
                if payment_response:
                    checkout_request_id = payment_response["CheckoutRequestID"]
                    ticket.checkout_request_id = checkout_request_id
                    ticket.status = 'pending'
                    ticket.save()
                    return redirect('safaricom_processing_payment', ticket.ticket_number)
                else:
                    logger.error("No response from safaricom.initiate_stk_push")
                    ticket.status = "failed"
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
                payment_response = pesapal.submit_order(ticket, description)

                if 'redirect_url' in payment_response:
                    ticket.order_tracking_id = payment_response['order_tracking_id']
                    ticket.status = "Awaiting payment confirmation"
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
            messages.error(request, "Payment initiation failed outside safaricom payment")
            return redirect('payment_failed', ticket.ticket_number)
            
    return HttpResponse("Invalid request method", status=400)


def tickets(request):
    if request.user.is_superuser:
        context = {
            "title_tag": "All Tickets",
            "tickets": Ticket.objects.order_by("-pk"),
        }
        return render(request, "tickets.html", context)
    return redirect("index")
