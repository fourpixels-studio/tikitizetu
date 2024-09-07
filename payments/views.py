import os
from .card_validation import validate_card_number
BANK_ACCOUNT_NUMBER = os.environ.get('BANK_ACCOUNT_NUMBER')
BANK_CODE = 57
BANK_NAME = 'I&M Bank Limited'
ACCOUNT_NAME = 'NAVINE ERIC'
SWIFT_CODE = 'IMBLKENA'
BRANCH_NAME = 'Nairobi Head Office'
CURRENCY = 'KES'
num = 4539148803436467


def process_bank_payment(card_number, cvc_number, expiry_date, amount):
    if validate_card_number(card_number):
        return True
    else:
        return False
