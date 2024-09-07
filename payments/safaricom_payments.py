import requests
import base64
from datetime import datetime
import os


def generate_password(shortcode, passkey, timestamp):
    data_to_encode = shortcode + passkey + timestamp
    encoded_string = base64.b64encode(data_to_encode.encode())
    return encoded_string.decode('utf-8')


def get_mpesa_access_token(consumer_key, consumer_secret):
    api_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    r = requests.get(api_url, auth=(consumer_key, consumer_secret))
    return r.json()['access_token']


def process_payment(phone_number, amount):
    consumer_key = os.environ.get('MPESA_CONSUMER_KEY')
    consumer_secret = os.environ.get('MPESA_CONSUMER_SECRET')
    shortcode = os.environ.get('MPESA_SHORTCODE')
    passkey = os.environ.get('MPESA_PASSKEY')

    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password = generate_password(shortcode, passkey, timestamp)
    access_token = get_mpesa_access_token(consumer_key, consumer_secret)

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }

    payload = {
        "BusinessShortCode": shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": shortcode,
        "PhoneNumber": phone_number,
        "CallBackURL": "https://tikitizetu.com/mpesa-callback/",
        "AccountReference": "Ticket Purchase",
        "TransactionDesc": "Payment for event ticket",
    }

    api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    response = requests.post(api_url, json=payload, headers=headers)

    if response.status_code == 200:
        response_data = response.json()
        if response_data['ResponseCode'] == "0":
            return True
        else:
            print(f"Error: {response_data['ResponseDescription']}")
            return False
    else:
        print(f"HTTP Error: {response.status_code}")
        return False
