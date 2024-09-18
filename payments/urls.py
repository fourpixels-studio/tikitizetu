from django.urls import path
from .pesapal_payments import pesapal_payment_ipn, pesapal_payment_callback
from .safaricom_payments import safaricom_payment_callback, safaricom_payment_validation, safaricom_processing_payment, safaricom_check_payment_status
from .views import payment_failed, payment_success


urlpatterns = [
    # pesapal urls
    path("pesapal/payment-callback/", pesapal_payment_callback, name="pesapal_payment_callback"),
    path('pesapal/payment-ipn/', pesapal_payment_ipn, name='pesapal_payment_ipn'),
    # safaricom urls
    path('s/processing-payment/<str:ticket_number>/', safaricom_processing_payment, name='safaricom_processing_payment'),
    path("s/payment-confirmation/", safaricom_payment_callback, name="safaricom_payment_callback"),
    path("s/payment-validation/", safaricom_payment_validation, name="safaricom_payment_validation"),
    path("s/check-payment-status/<str:ticket_number>/", safaricom_check_payment_status, name="safaricom_check_payment_status"),
    # general urls
    path("payment-failed/<str:ticket_number>/", payment_failed, name="payment_failed"),
    path("payment-success/<str:ticket_number>/", payment_success, name="payment_success"),

]
