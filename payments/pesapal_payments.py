import json
import time
import logging
import requests
from django.conf import settings
from django.utils import timezone
from tickets.models import Ticket
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.debug import sensitive_variables

logger = logging.getLogger('django')


@sensitive_variables('PESAPAL_CONSUMER_KEY', 'PESAPAL_CONSUMER_SECRET')
class PesaPal:
    def __init__(self):
        self.base_url = 'https://pay.pesapal.com/v3/api/'

        self.payload = json.dumps({
            "consumer_key": settings.PESAPAL_CONSUMER_KEY,
            "consumer_secret": settings.PESAPAL_CONSUMER_SECRET,
        })

    def authenticate(self):
        endpoint = "Auth/RequestToken"

        headers = {
            "Content-Type": 'application/json',
            "Accept": 'application/json',
        }

        response = requests.request(
            "POST", self.base_url+endpoint, headers=headers, data=self.payload)

        return response.json()['token']

    def registerIPN_URL(self):
        endpoint = "URLSetup/RegisterIPN"
        myIPN_url = f'{settings.SITE_DOMAIN}pesapal/ipn/'

        payload = json.dumps({
            "url": myIPN_url,
            "ipn_notification_type": "POST",
        })

        headers = {
            "Accept": 'application/json',
            "Content-Type": 'application/json',
            "Authorization": self.authenticate(),
        }

        response = requests.request(
            "POST", self.base_url+endpoint, headers=headers, data=payload)

        return response.json()

    def submit_order(self, ticket, description):
        endpoint = "Transactions/SubmitOrderRequest"

        callback_url = f'{settings.SITE_DOMAIN}pesapal/payment-callback/'
        cancellation_url = f'{settings.SITE_DOMAIN}payment-failed/{ticket.ticket_number}/'

        payload = json.dumps({
            "id": ticket.ticket_number,
            "currency": "KES",
            "amount": ticket.amount,
            "description": description,
            "callback_url": callback_url,
            "cancellation_url": cancellation_url,
            "notification_id": self.registerIPN_URL()['ipn_id'],
            "billing_address": {
                "email_address": ticket.get_email,
                "phone_number": ticket.phone_number,
                "first_name": ticket.first_name,
                "middle_name": "",
                "last_name": ticket.last_name,
                "line_1": "",
                "line_2": "",
                "city": "",
                "state": "",
                "postal_code": None,
                "zip_code": None,
            }
        })

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": self.authenticate(),
        }

        response = requests.post(
            self.base_url + endpoint,
            headers=headers, data=payload
        )

        response_data = response.json()

        if 'order_tracking_id' in response_data and 'redirect_url' in response_data:
            return response_data
        else:
            raise KeyError(
                "The response from Pesapal does not contain 'order_tracking_id' or 'redirect_url'.")

    def check_transaction(self, tracking_id):
        timeout = time.time() + 60
        while time.time() < timeout:
            endpoint = f'Transactions/GetTransactionStatus?orderTrackingId={tracking_id}'
            headers = {
                "Accept": 'application/json',
                "Content-Type": 'application/json',
                "Authorization": self.authenticate(),
            }
            response = requests.get(self.base_url + endpoint, headers=headers)

            if response.status_code == 200:
                return response.json()
            else:
                print("Wrong transaction ID")
            time.sleep(5)

        raise Exception("Transaction status check timed out.")


@csrf_exempt
def pesapal_payment_callback(request):
    try:
        order_tracking_id = request.GET.get('OrderTrackingId')
        order_merchant_reference = request.GET.get('OrderMerchantReference')
        ticket = Ticket.objects.get(
            ticket_number=order_merchant_reference)
        pesapal = PesaPal()
        transaction_data = pesapal.check_transaction(order_tracking_id)
        status = transaction_data['payment_status_description']
        if status == 'Completed':
            ticket.status = status
            if transaction_data['confirmation_code']:
                ticket.mpesa_code = transaction_data['confirmation_code']
            ticket.paid = True
            ticket.payment_date = transaction_data['created_date']
            ticket.save()
            return redirect('payment_success', ticket.ticket_number)
        else:
            status = transaction_data['payment_status_description']
            ticket.paid = False
            ticket.save()
            return redirect('payment_failed', ticket.ticket_number)
    except:
        return HttpResponse("Invalid request", status=405)


@csrf_exempt
def pesapal_payment_ipn(request):
    if request.method == 'POST':
        order_tracking_id = request.POST.get('OrderTrackingId')
        merchant_reference = request.POST.get('OrderMerchantReference')
        notification_type = request.POST.get('OrderNotificationType')
        if notification_type == 'IPNCHANGE':
            pesapal = PesaPal()
            transaction_status = pesapal.check_transaction(
                order_tracking_id)
            try:
                ticket = Ticket.objects.get(ticket_number=merchant_reference)
                if transaction_status['status'] == 'COMPLETED':
                    ticket.paid = True
                    ticket.status = 'Paid'
                    ticket.order_tracking_id = order_tracking_id
                    ticket.payment_date = timezone.now()
                    ticket.save()
                    logger.info(f"Returnng IPN Handled")
                    return HttpResponse("IPN handled", status=200)
            except Ticket.DoesNotExist:
                return HttpResponse("Ticket not found", status=404)
        return HttpResponse("Invalid IPN request", status=400)
    return HttpResponse(status=405)
