from django.urls import path
from .views import view_ticket, new_ticket

urlpatterns = [
    path("<slug:slug>/<str:ticket_number>/<int:pk>/", view_ticket, name="view_ticket"),
    path("new-ticket/", new_ticket, name="new_ticket"),
]
