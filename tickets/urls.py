from django.urls import path
from .views import view_ticket, purchase_ticket

urlpatterns = [
    path("<slug:slug>/<str:ticket_number>/<int:pk>/", view_ticket, name="view_ticket"),
    path("purchase/", purchase_ticket, name="purchase_ticket"),
]
