from django import forms
from .models import Ticket


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = (
            'event',
            'ticket_number',
            'first_name',
            'last_name',
            'amount',
            'qr',
        )
