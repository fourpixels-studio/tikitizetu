from django.views.decorators.debug import sensitive_variables
import requests
import base64
from datetime import datetime
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.shortcuts import redirect
from tickets.models import Ticket


@sensitive_variables('PESAPAL_CONSUMER_KEY', 'PESAPAL_CONSUMER_SECRET', 'SAFARICOM_PASSKEY')
class Safaricom:
    def __init__(self):
        self.base_url = 'https://sandbox.safaricom.co.ke/'
        self.InitiatorName = 'testapi'
        self.InitiatorPassword = settings.SAFARICOM_INITIATOR_PASSWORD
        self.shortcode = settings.SAFARICOM_SHORTCODE
        self.passkey = settings.SAFARICOM_PASSKEY

    def get_access_token(self):
        endpoint = "oauth/v1/generate?grant_type=client_credentials"
        response = requests.get(
            self.base_url+endpoint,
            auth=(
                settings.SAFARICOM_CONSUMER_KEY,
                settings.SAFARICOM_CONSUMER_SECRET
            )
        )
        return response.json()['access_token']

    def generate_password(self, timestamp):
        data_to_encode = self.shortcode + self.passkey + timestamp
        encoded_string = base64.b64encode(data_to_encode.encode())
        return encoded_string.decode('utf-8')

    def initiate_stk_push(self, amount, PhoneNumber, event_slug, ticket_number, event_pk):
        endpoint = "mpesa/stkpush/v1/processrequest"
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        CallBackURL = f'https://www.tikitizetu.com/ticket/{event_slug}/{ticket_number}/{event_pk}/'

        headers = {
            'Authorization': f'Bearer {self.get_access_token()}',
            'Content-Type': 'application/json',
        }

        payload = {
            "BusinessShortCode": "174379",
            "Password": self.generate_password(timestamp),
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": PhoneNumber,
            "PartyB": "174379",
            "PhoneNumber": PhoneNumber,
            "CallBackURL": CallBackURL,
            "AccountReference": "Tikiti Zetu",
            "TransactionDesc": "Tikiti Zetu"
        }
        response = requests.post(
            self.base_url+endpoint,
            json=payload, headers=headers
        )
        if response.status_code == 200:
            response_data = response.json()
            if response_data['ResponseCode'] == "0":
                print(response.json())
                return True
            else:
                print(f"Error: {response_data['ResponseDescription']}")
                return False
        else:
            print(f"HTTP Error: {response.status_code}")
            print(response.json())
            return False


@csrf_exempt
def safaricom_payment_callback(request):
    ResponseCode = request.GET.get('ResponseCode')
    MpesaReceiptNumber = request.GET.get('MpesaReceiptNumber')

    if ResponseCode == '0':
        try:
            ticket = Ticket.objects.get(mpesa_code=MpesaReceiptNumber)
            ticket.paid = True
            ticket.status = "Paid"
            ticket.save()
            return redirect('view_ticket', ticket.event.slug, ticket.ticket_number, ticket.event.pk)
        except Ticket.DoesNotExist:
            ticket.status = 'Ticket not found'
            ticket.save()
            return redirect('cart', slug=ticket.event.slug, pk=ticket.event.pk)
    return HttpResponse("Payment failed", status=404)
