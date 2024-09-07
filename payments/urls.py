from django.urls import path
from .views import payment_failed, process_payment

urlpatterns = [
    path("failed/", payment_failed, name="payment_failed"),
    path("process-payment/", process_payment, name="process_payment"),
]
