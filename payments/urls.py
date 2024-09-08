from django.urls import path
from .im_payments import im_payment_callback, im_payment_success, im_payment_failed

urlpatterns = [
    # I&M Bank
    path("im/payment-callback/", im_payment_callback, name="im_payment_callback"),
    path("im/payment-success/", im_payment_success, name="im_payment_success"),
    path("im/payment-failed/", im_payment_failed, name="im_payment_failed"),
]
