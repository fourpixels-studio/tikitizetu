import uuid
from events.models import Event
from tickets.models import Ticket
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from payments.pesapal_payments import PesaPal
from tickets.utils import generate_pdf, generate_qr
from tickets.email import send_ticket_email
from django.urls import reverse


def view_ticket(request, slug, ticket_number, pk):
    ticket = get_object_or_404(Ticket, ticket_number=ticket_number)
    if ticket.paid:
        context = {
            "title_tag": f"Your {ticket.event.name} Ticket",
            "ticket": ticket,
            "event": ticket.event,
        }
        return render(request, "view_ticket.html", context)
    else:
        order_tracking_id = None
        try:
            order_tracking_id = request.GET.get('OrderTrackingId')
        except:
            order_tracking_id = request.GET.get('order_tracking_id')

        ticket.paid = True
        ticket.status = 'Paid'
        ticket.order_tracking_id = order_tracking_id
        ticket.save()

        ticket_url = request.build_absolute_uri(reverse(
            'view_ticket', args=[ticket.event.slug, ticket.ticket_number, ticket.event.pk]))
        ticket.save()

        generate_qr(ticket_url, ticket)
        ticket.save()

        generate_pdf(
            ticket_url, ticket.event, ticket, ticket.first_name, ticket.last_name,
            ticket.email, ticket.phone_number, ticket.amount, ticket.ticket_type
        )
        ticket.save()

        send_ticket_email(ticket, ticket.event)
        return redirect('view_ticket', ticket.event.slug, ticket.ticket_number, ticket.event.pk)


def purchase_ticket(request):
    if request.method == 'POST':
        event_id = request.POST.get('event')
        event = Event.objects.get(id=event_id)
        payment_method = request.POST.get('payment_method')

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
                    if payment_method.status_code == 200:
                        data = payment_response.json()
                        checkout_request_id = data["CheckoutRequestID"]
                        return JsonResponse({"CheckoutRequestId": checkout_request_id})
                else:
                    ticket.status = "Payment initiation failed"
                    ticket.save()
                    return redirect(f"https://www.tikitizetu.com/ticket/payment-failed/{ticket_number}")

            except Exception as e:
                ticket.status = f"Payment initiation failed: {str(e)}"
                ticket.save()
                return redirect(f"https://www.tikitizetu.com/ticket/payment-failed/{ticket_number}")

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
                    return redirect(f"https://www.tikitizetu.com/ticket/payment-failed/{ticket_number}")
            except KeyError as e:
                messages.error(request, f"Payment initiation failed: {str(e)}")
                ticket.status = f"Payment initiation failed: {str(e)}"
                ticket.save()
                return redirect(f"https://www.tikitizetu.com/ticket/payment-failed/{ticket_number}")
        else:
            return redirect(f"https://www.tikitizetu.com/ticket/payment-failed/{ticket_number}")
    return HttpResponse("Invalid request method", status=400)


def generate_ticket_number():
    return str(uuid.uuid4())




def format_phone_number(phone_number):
    # Remove any spaces or non-numeric characters like '+'
    phone_number = phone_number.strip().replace(" ", "").replace("+", "")

    # If the number starts with '07', replace it with '2547'
    if phone_number.startswith("07"):
        phone_number = "254" + phone_number[1:]

    # If the number starts with '01', replace it with '2547'
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
