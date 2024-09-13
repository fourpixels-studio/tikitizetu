import time
import requests
from django.views.decorators.debug import sensitive_variables
import json
from django.conf import settings
import uuid


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
            "ipn_notification_type": "GET",
        })

        headers = {
            "Accept": 'application/json',
            "Content-Type": 'application/json',
            "Authorization": self.authenticate(),
        }

        response = requests.request(
            "POST", self.base_url+endpoint, headers=headers, data=payload)

        return response.json()

    def submit_order(self, amount, ticket, first_name, last_name, email, phone_number):
        endpoint = "Transactions/SubmitOrderRequest"

        callback_url = f'https://www.tikitizetu.com/ticket/{ticket.event.slug}/{ticket.ticket_number}/{ticket.event.pk}/'

        payload = json.dumps({
            "id": str(uuid.uuid4()),
            "currency": "KES",
            "amount": amount,
            "description": f'Payment for: "{ticket.event.name}" - ticket',
            "callback_url": callback_url,
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
            "Content-Type": 'application/json',
            "Authorization": self.authenticate(),
        }

        response = requests.request(
            "POST", self.base_url+endpoint, headers=headers, data=payload)

        self.check_transaction(
            response.json()['order_tracking_id'], response.json()['status'])

        return response.json()

    def check_transaction(self, tracking_id, status_code):
        timeout = time.time() + 60

        if time.time() < timeout:
            if status_code == 200:

                endpoint = f'Transactions/GetTransactionStatus?orderTrackingId={tracking_id}'

                payload = {}

                headers = {
                    "Accept": 'application/json',
                    "Content-Type": 'application/json',
                    "Authorization": self.authenticate(),
                }

                response = requests.request(
                    "POST", self.endpoint, headers=headers, data=payload)

                print("Payment successful")

                return response.json()
            else:
                print("Payment not successful")
        else:
            print("Payment did not go through")
