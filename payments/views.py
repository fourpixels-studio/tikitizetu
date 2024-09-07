from .card_validation import validate_card_number

def process_bank_payment(card_number, cvc_number, expiry_date, amount):
    if validate_card_number(card_number):
        return True
    else:
        return False
