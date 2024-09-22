import json
import base64
import logging
import requests
from datetime import datetime
from django.conf import settings
from tickets.models import Ticket
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.debug import sensitive_variables
from django.shortcuts import render, get_object_or_404, redirect

logger = logging.getLogger('django')


@sensitive_variables('SAFARICOM_INITIATOR_NAME', 'SAFARICOM_INITIATOR_PASSWORD', 'SAFARICOM_SHORTCODE', 'SAFARICOM_PASSKEY')
class Safaricom:

    def __init__(self):
        self.base_url = settings.SAFARICOM_BASE_URL
        self.callback_url = f'{settings.SITE_DOMAIN}s/payment-confirmation/'
        self.validation_url = f'{settings.SITE_DOMAIN}s/payment-validation/'
        self.InitiatorName = settings.SAFARICOM_INITIATOR_NAME
        self.InitiatorPassword = settings.SAFARICOM_INITIATOR_PASSWORD
        self.shortcode = settings.SAFARICOM_SHORTCODE
        self.passkey = settings.SAFARICOM_PASSKEY
        self.timestamp = timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        self.password = self.generate_password(timestamp)

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

    def registerURL(self):
        endpoint = "mpesa/c2b/v1/registerurl"

        headers = {
            'Authorization': f'Bearer {self.get_access_token()}',
            'Content-Type': 'application/json',
        }

        payload = {
            "ShortCode": self.shortcode,
            "ResponseType": "Completed",
            "ConfirmationURL": self.callback_url,
            "ValidationURL": self.validation_url,
        }

        response = requests.post(
            self.base_url+endpoint, headers=headers, json=payload
        )

        if response.status_code == 200:
            response_data = response.json()
            if response_data['ResponseCode'] == "0":
                logger.info(
                    f"URL registration successful: {response_data['ResponseDescription']}")
                return response.json()
            else:
                logger.info(f"Error: {response_data['ResponseDescription']}")
                return False
        else:
            logger.info(f"HTTP Error: {response.status_code}")
            logger.info(response.json())
            return False

    def initiate_stk_push(self, amount, phone_number, transaction_description):
        endpoint = "mpesa/stkpush/v1/processrequest"

        headers = {
            'Authorization': f'Bearer {self.get_access_token()}',
            'Content-Type': 'application/json',
        }

        payload = {
            "BusinessShortCode": self.shortcode,
            "Password": self.password,
            "Timestamp": self.timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone_number,
            "PartyB": self.shortcode,
            "PhoneNumber": phone_number,
            "CallBackURL": self.callback_url,
            "AccountReference": "TIKITI ZETU",
            "TransactionDesc": transaction_description,
        }
        response = requests.post(
            self.base_url+endpoint,
            json=payload, headers=headers
        )

        if response.status_code == 200:
            response_data = response.json()
            if response_data['ResponseCode'] == "0":
                return response.json()
            else:
                logger.info(f"Error: {response_data['ResponseDescription']}")
                return False
        else:
            logger.info(f"HTTP Error: {response.status_code}")
            logger.info(response.json())
            return response.json()

    def check_transaction_status(self, checkout_request_id):
        endpoint = 'mpesa/stkpushquery/v1/query'

        headers = {
            'Authorization': f'Bearer {self.get_access_token()}',
            'Content-Type': 'application/json',
        }
        query_data = {
            "BusinessShortCode": self.shortcode,
            "Password": self.password,
            "Timestamp": self.timestamp,
            "CheckoutRequestID": checkout_request_id
        }

        response = requests.post(
            self.base_url+endpoint, json=query_data, headers=headers)

        return response.json()

    def get_transaction(self, phone_number, transaction_id):
        endpoint = 'mpesa/transactionstatus/v1/query'

        headers = {
            'Authorization': f'Bearer {self.get_access_token()}',
            'Content-Type': 'application/json',
        }
        query_data = {
            "Initiator": self.InitiatorName,
            "SecurityCredential": self.password,
            "Command ID": "TransactionStatusQuery",
            "Transaction ID": transaction_id,
            "OriginatorConversationID": "AG_20190826_0000777ab7d848b9e721",
            "PartyA": phone_number,
            "IdentifierType": "4",
            "ResultURL": f"{settings.SITE_DOMAIN}transactionstatus/result",
            "QueueTimeOutURL": f"{settings.SITE_DOMAIN}8080/timeout",
            "Remarks": "OK",
            "Occasion": "OK",
        }

        response = requests.post(
            self.base_url+endpoint, json=query_data, headers=headers)

        return response.json()


@csrf_exempt
def safaricom_payment_callback(request):
    if request.method == "POST":
        try:
            # Safaricom will send the callback data as JSON in the request body
            callback_data = json.loads(request.body)

            body = callback_data.get('Body', {})
            stk_callback = body.get('stkCallback', {})
            result_code = stk_callback.get('ResultCode')
            result_desc = stk_callback.get('ResultDesc')
            checkout_request_id = stk_callback.get('CheckoutRequestID')

            # You can get the metadata about the transaction from 'CallbackMetadata'
            callback_metadata = stk_callback.get('CallbackMetadata', {}).get('Item', [])

            # Extract necessary data from callback metadata
            amount = None
            mpesa_code = None
            payment_date = None

            # Parse metadata items
            for item in callback_metadata:
                if item['Name'] == "Amount":
                    amount = item['Value']
                elif item['Name'] == "MpesaReceiptNumber":
                    mpesa_code = item['Value']
                elif item['Name'] == "TransactionDate":
                    payment_date = item['Value']

            # Check if the payment was successful
            if result_code == 0:
                ticket = Ticket.objects.get(
                    checkout_request_id=checkout_request_id)
                ticket.paid = True
                ticket.status = 'Paid'
                ticket.mpesa_code = mpesa_code
                ticket.amount = amount
                ticket.payment_date = payment_date
                ticket.save()

                JsonResponse({"status": "success"})
            else:
                # Handle failed payment case
                ticket = Ticket.objects.get(
                    checkout_request_id=checkout_request_id)
                ticket.paid = False
                ticket.status = f"Failed: {result_desc}"
                ticket.save()
                logger.warning(f"Payment failed: {result_desc}")

                return JsonResponse({"status": "failed", "message": result_desc})

        except Exception as e:
            logger.error(
                f"Error processing the callback: {e}")
            return JsonResponse({"status": "failed", "message": e})
    response = {
        "ResultCode": 0,
        "ResultDesc": "Received Successfully",
        "status": "success"
    }
    return JsonResponse(response)


@csrf_exempt
def safaricom_processing_payment(request, ticket_number):
    try:
        ticket = get_object_or_404(Ticket, ticket_number=ticket_number)
        if ticket:
            if ticket.paid:
                return redirect('view_ticket', ticket.event.slug, ticket.ticket_number, ticket.event.pk)
            else:
                context = {
                    "title_tag": "Processing your Payment.",
                    'ticket': ticket,
                }
                return render(request, "safaricom/processing_payment.html", context)
    except Ticket.DoesNotExist:
        return JsonResponse({"status": "invalid method"}, status=400)


@csrf_exempt
def safaricom_check_payment_status(request, ticket_number):
    try:
        ticket = get_object_or_404(Ticket, ticket_number=ticket_number)
        safaricom = Safaricom()
        checkout_request_id = ticket.checkout_request_id
        response = safaricom.check_transaction_status(checkout_request_id)
        if ticket.paid:
            return JsonResponse({'status': 'success'})
        else:
            if response['ResultCode'] == '0':
                ticket.status = "Paid"
                ticket.save()
                return JsonResponse({'status': 'success'})
            else:
                ticket.status = response['ResultDesc']
                ticket.save()
                return JsonResponse({'status': 'failed'})
    except Ticket.DoesNotExist:
        logger.info("status failed message Ticket not found")
        return JsonResponse({'status': 'failed', 'message': 'Ticket not found'})


@csrf_exempt
def safaricom_payment_validation(request):
    if request.method == "POST":
        try:
            callback_data = json.loads(request.body)
            body = callback_data.get('Body', {})
            stk_callback = body.get('stkCallback', {})
            result_code = stk_callback.get('ResultCode')
            result_desc = stk_callback.get('ResultDesc')
            checkout_request_id = stk_callback.get('CheckoutRequestID')
            callback_metadata = stk_callback.get(
                'CallbackMetadata', {}).get('Item', [])
            amount = None
            mpesa_code = None
            payment_date = None
            for item in callback_metadata:
                if item['Name'] == "Amount":
                    amount = item['Value']
                elif item['Name'] == "MpesaReceiptNumber":
                    mpesa_code = item['Value']
                elif item['Name'] == "TransactionDate":
                    payment_date = item['Value']
            if result_code == 0:
                ticket = Ticket.objects.get(
                    checkout_request_id=checkout_request_id)
                ticket.paid = True
                ticket.status = 'Paid'
                ticket.mpesa_code = mpesa_code
                ticket.amount = amount
                ticket.payment_date = payment_date
                ticket.save()
                JsonResponse({"status": "success"})
            else:
                ticket = Ticket.objects.get(
                    checkout_request_id=checkout_request_id)
                ticket.paid = False
                ticket.status = f"Failed: {result_desc}"
                ticket.save()
                logger.warning(f"Payment failed: {result_desc}")
                return JsonResponse({"status": "failed", "message": result_desc})
        except Exception as e:
            logger.error(f"Error processing the callback: {e}")
    return JsonResponse({"ResultCode": 0, "ResultDesc": "Received Successfully"})
