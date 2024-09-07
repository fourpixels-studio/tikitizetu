from django.shortcuts import render
from .card_validation import validate_card_number

def process_bank_payment(card_number, cvc_number, expiry_date, amount):
    if validate_card_number(card_number):
        return True
    else:
        return False


def payment_failed(request):
    return render(request, "payment_failed.html", {"title_tag": "Payment Failed."})


def process_payment(request):
    return render(request, "process_payment.html", {"title_tag": "Process Payment."})
