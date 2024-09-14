from django.urls import path
from .pesapal_payments import pesapal_payment_ipn, pesapal_payment_callback

urlpatterns = [
    path("pesapal/payment-callback/", pesapal_payment_callback, name="pesapal_payment_callback"),
    path('pesapal/payment-ipn/', pesapal_payment_ipn, name='pesapal_payment_ipn')
]
