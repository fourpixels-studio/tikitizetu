import time
import requests
import json
from django.views.decorators.debug import sensitive_variables
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from tickets.models import Ticket


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
        myIPN_url = 'https://www.tikitizetu.com/pesapal/payment-callback/'

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

    def submit_order(self, transaction_id, amount, description, phone_number, email, first_name, last_name, ticket_number, event_slug, event_id):
        endpoint = "Transactions/SubmitOrderRequest"

        callback_url = f'https://www.tikitizetu.com/ticket/{event_slug}/{ticket_number}/{event_id}/'
        cancellation_url = f'https://www.tikitizetu.com/ticket/payment-failed/{ticket_number}/'

        payload = json.dumps({
            "id": transaction_id,
            "currency": "KES",
            "amount": amount,
            "description": description,
            "callback_url": callback_url,
            "cancellation_url": cancellation_url,
            "notification_id": self.registerIPN_URL()['ipn_id'],
            "billing_address": {
                "email_address": email,
                "phone_number": phone_number,
                "first_name": first_name,
                "middle_name": "",
                "last_name": last_name,
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
            response = requests.get(
                self.base_url + endpoint, headers=headers
            )
            response_data = response.json()

            if response_data.get('status') == 'Completed':
                return response_data
            time.sleep(5)

        raise Exception("Transaction status check timed out.")


@csrf_exempt
def pesapal_payment_callback(request):
    order_tracking_id = request.GET.get('OrderTrackingId')
    order_merchant_reference = request.GET.get('OrderMerchantReference')
    order_notification_type = request.GET.get('OrderNotificationType')

    if order_notification_type == 'CALLBACKURL':
        try:
            ticket = Ticket.objects.get(
                transaction_id=order_merchant_reference)
            pesapal = PesaPal()

            transaction_data = pesapal.check_transaction(order_tracking_id)
            status = transaction_data.get('status')

            if status == 'Completed':
                ticket.order_tracking_id = order_tracking_id
                ticket.save()
                return redirect('view_ticket', ticket.event.slug, ticket.ticket_number, ticket.event.pk)
            else:
                ticket.status = 'Payment Failed (callback invalid)'
                ticket.save()
                return redirect('cart', slug=ticket.event.slug, pk=ticket.event.pk)

        except Ticket.DoesNotExist:
            return HttpResponse("Ticket not found", status=404)


@csrf_exempt
def pesapal_payment_ipn(request):
    if request.method == 'GET':
        order_tracking_id = request.GET.get('OrderTrackingId')
        merchant_reference = request.GET.get('OrderMerchantReference')
        notification_type = request.GET.get('OrderNotificationType')

        if notification_type == 'IPNCHANGE':
            pesapal = PesaPal()
            transaction_status = pesapal.check_transaction(order_tracking_id)

            try:
                ticket = Ticket.objects.get(transaction_id=merchant_reference)
                if transaction_status['status'] == 'COMPLETED':
                    ticket.paid = True
                    ticket.status = 'Paid'
                    ticket.order_tracking_id = order_tracking_id
                    ticket.save()
                    return HttpResponse("IPN handled", status=200)
            except Ticket.DoesNotExist:
                return HttpResponse("Ticket not found", status=404)

        return HttpResponse("Invalid IPN request", status=400)

    return HttpResponse(status=405)
