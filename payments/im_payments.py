import hashlib
from urllib.parse import urlencode
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
import uuid
import os
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from tickets.models import Ticket
from events.models import Event


def process_payment(request):
    if request.method == "POST":
        # Collect the necessary data from the form
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        phone_number = request.POST['phone_number']
        amount = request.POST['amount']
        ticket_type = request.POST['ticket_type']
        ticket_number = request.POST['ticket_number']
        event_id = request.POST['event_id']

        # I&M Bank iPay credentials
        vendor_id = os.environ.get('IM_VENDOR_ID')
        api_key = os.environ.get('IM_API_KEY')
        security_credential = os.environ.get('IM_SECURITY_CREDENTIAL')

        # Payment details
        transaction_id = "TXN" + str(uuid.uuid4())
        # Replace with your callback URL
        callback_url = 'https://tikitizetu.com/im/payment-callback/'
        # Replace with your success URL
        redirect_url = 'https://tikitizetu.com/im/payment-success/'
        # Replace with your error URL
        error_url = 'https://tikitizetu.com/im/payment-failure/'

        # Create the hash to secure the payment request
        hash_string = f"{vendor_id}{transaction_id}{amount}{callback_url}{api_key}"
        security_hash = hashlib.sha256(hash_string.encode('utf-8')).hexdigest()

        # Create the payment request payload
        payload = {
            'live': '0',  # 1 for live environment, 0 for sandbox
            'oid': transaction_id,
            'inv': 'Invoice' + str(uuid.uuid4()),
            'ttl': amount,
            'tel': phone_number,
            'eml': email,
            'vid': vendor_id,
            'curr': 'KES',
            'p1': first_name,
            'p2': last_name,
            'p3': ticket_type,
            'p4': f'{ticket_type} Ticket',
            'cbk': callback_url,
            'cst': '1',
            'crl': '0',
            'hsh': security_hash,
            'redirect': redirect_url,
            'error': error_url,
            'ticket_type': ticket_type,
            'ticket_number': ticket_number,
            'event_id': event_id,
        }
        return redirect(f"https://payments.imbank.com/pay/?{urlencode(payload)}")

    return redirect('buy_ticket')


@csrf_exempt
def im_payment_callback(request):
    if request.method == "POST":
        transaction_id = request.POST.get('id')
        status = request.POST.get('status')
        ticket_number = request.POST.get('ticket_number')
        try:
            ticket = Ticket.objects.get(ticket_number=ticket_number)
            if status == 'success':
                ticket.paid = True
                ticket.status = 'Paid'
                ticket.transaction_id = transaction_id
                ticket.save()
                return True
            else:
                ticket.status = 'Payment Failed'
                ticket.save()
                return redirect(f"https://tikitizetu.com/im/payment-failure/?ticket_number={ticket_number}")
        except Ticket.DoesNotExist:
            return HttpResponse(status=404)  # Ticket not found

    return HttpResponse(status=400)


def im_payment_failed(request):
    ticket_number = request.GET.get('ticket_number')
    try:
        ticket = Ticket.objects.get(ticket_number=ticket_number)
        event_id = ticket.event.pk
        event = get_object_or_404(Event, pk=event_id)
        context = {
            "title_tag": "Payment Failed",
            "event": event,
            "ticket": ticket
        }
        return render(request, "im/im_payment_failed.html", context)
    except Ticket.DoesNotExist:
        return HttpResponse(status=404)  # Ticket not found


def im_payment_success(request):
    ticket_number = request.GET.get('ticket_number')
    try:
        ticket = Ticket.objects.get(ticket_number=ticket_number)
        ticket.paid = True
        ticket.status = "Paid"
        ticket.save()
        event_id = ticket.event.pk
        event = get_object_or_404(Event, pk=event_id)
        return reverse("view_ticket", kwargs={
            "event_name": event.slug,
            "ticket_number": ticket_number,
            "event_id": event.pk,
        })
    except Ticket.DoesNotExist:
        return HttpResponse(status=404)  # Ticket not found
