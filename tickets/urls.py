from django.urls import path
from .views import view_ticket, purchase_ticket
from payments.views import pesapal_payment_failed

urlpatterns = [
    path("<slug:slug>/<str:ticket_number>/<int:pk>/", view_ticket, name="view_ticket"),
    path("purchase/", purchase_ticket, name="purchase_ticket"),
    path("payment-failed/<str:ticket_number>/", pesapal_payment_failed, name="pesapal_payment_failed"),
]
